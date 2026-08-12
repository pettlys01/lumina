#!/usr/bin/env python3
"""
Gera uma cópia auto-contida de uma página do projeto, para revisão.

O site real usa CSS em arquivos separados e fontes auto-hospedadas — que é como
ele deve ser entregue. Mas para publicar uma versão de revisão em um único
arquivo, tudo precisa estar embutido: CSS inline e fontes como data URI.

Este script faz essa conversão sem tocar nos arquivos do projeto:

    python tools/inline.py styleguide.html build/styleguide.inline.html

O que ele faz:
  1. substitui cada <link rel="stylesheet"> pelo conteúdo do CSS;
  2. converte cada url(...woff2) do CSS em data URI base64;
  3. remove <link rel="preload"> de fonte (inútil depois de embutida);
  4. remove os invólucros <!DOCTYPE>/<html>/<head>/<body>, mantendo <title>,
     <style>, o conteúdo do body e os <script> — formato exigido pela
     publicação de artifact.
"""

import base64
import re
import sys
from pathlib import Path


def inline_fonts(css: str, css_path: Path) -> tuple[str, int]:
    """Troca url(...woff2) por data URI, resolvendo o caminho a partir do CSS.

    Aceita url(x.woff2), url('x.woff2') e url("x.woff2") — as três formas são
    válidas em CSS, e um padrão que só cobrisse a primeira falharia em silêncio.
    """

    def replace(match: re.Match) -> str:
        raw = match.group(1).strip().strip("'\"")
        font_path = (css_path.parent / raw).resolve()
        if not font_path.is_file():
            raise FileNotFoundError(f"fonte não encontrada: {font_path} (em {css_path})")
        encoded = base64.b64encode(font_path.read_bytes()).decode("ascii")
        return f"url(data:font/woff2;base64,{encoded})"

    css, count = re.subn(r"""url\(\s*['"]?([^)'"]+?\.woff2)['"]?\s*\)""", replace, css)

    # Um CSS que declara @font-face mas não teve nenhuma fonte embutida geraria
    # uma página que cai silenciosamente para a fonte do sistema.
    if "@font-face" in css and count == 0:
        raise ValueError(f"{css_path.name} declara @font-face mas nenhuma fonte foi embutida")

    return css, count


def build(src: Path, dest: Path) -> None:
    html = src.read_text(encoding="utf-8")
    root = src.parent

    fonts_inlined = 0

    # 1 + 2. Cada folha de estilo vira um <style> com as fontes já embutidas.
    def replace_link(match: re.Match) -> str:
        nonlocal fonts_inlined
        href = match.group(1)
        css_path = (root / href).resolve()
        if not css_path.is_file():
            raise FileNotFoundError(f"CSS não encontrado: {css_path}")
        css, n_fonts = inline_fonts(css_path.read_text(encoding="utf-8"), css_path)
        fonts_inlined += n_fonts
        return f"<style>\n/* ---- {href} ---- */\n{css}\n</style>"

    html, n_css = re.subn(
        r'<link\s+rel="stylesheet"\s+href="([^"]+)"\s*/?>',
        replace_link,
        html,
    )

    # 3. Preload de fonte não faz sentido depois da fonte virar data URI.
    html, n_preload = re.subn(
        r'\s*<link\s+rel="preload"[^>]*as="font"[^>]*>', "", html
    )

    # 4. Extrai <title>, <style>, corpo e <script>; descarta os invólucros.
    title = re.search(r"<title>(.*?)</title>", html, re.S)
    styles = re.findall(r"<style>.*?</style>", html, re.S)
    body = re.search(r"<body[^>]*>(.*?)</body>", html, re.S)

    if not body:
        raise ValueError("não encontrei <body> no arquivo de origem")

    parts = []
    if title:
        parts.append(f"<title>{title.group(1).strip()}</title>")
    parts.extend(styles)
    parts.append(body.group(1).strip())

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n\n".join(parts), encoding="utf-8")

    size_kb = dest.stat().st_size / 1024
    print(f"{src.name} -> {dest}")
    print(f"  {n_css} folha(s) de estilo embutida(s), {n_preload} preload removido(s)")
    print(f"  {fonts_inlined} fonte(s) embutida(s)")
    print(f"  {size_kb:.0f} KB")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"uso: python {sys.argv[0]} <origem.html> <destino.html>")
    build(Path(sys.argv[1]), Path(sys.argv[2]))
