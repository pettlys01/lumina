#!/usr/bin/env python3
"""
Monta as páginas do site a partir de partials de componente.

Motivo: o brief pede modularidade real ("cada componente em sua própria pasta"),
mas HTML estático não tem include nativo. Sem um passo de montagem, a marcação de
cada componente teria que ser copiada em toda página que o usa — e as cópias
divergiriam. Este script resolve isso sem introduzir framework: ele é um
pré-processador de texto, não uma dependência de runtime. A página entregue
continua sendo HTML puro.

Uso:
    python tools/build.py            # monta tudo que está em src/ (recursivo)
    python tools/build.py src/x.html # monta uma página só

Sintaxe, em qualquer página de src/:
    <!-- include: components/Hero/hero.html -->

O recuo da linha do include é aplicado a todas as linhas do partial, para que a
saída continue legível. Includes podem ser aninhados.

Convenção de caminho (importante para a Fase 5, primeira com páginas fora da
raiz): todo href/src escrito em qualquer partial ou página-fonte é relativo à
RAIZ do projeto — "styles/tokens.css", "assets/img/hero.jpg",
"especialidades/implantes.html" — nunca "../styles/..." nem "./algo". Um
componente é incluído por páginas em profundidades diferentes (index.html na
raiz, especialidades/implantes.html um nível abaixo); se o caminho já viesse
com "../" embutido, estaria certo num lugar e errado no outro. Em vez disso, o
autor do componente escreve sempre relativo à raiz, e este script corrige a
profundidade na saída (ver reescreve_profundidade). Um único jeito de escrever
caminho, correto em qualquer página que inclua o componente.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

INCLUDE = re.compile(r"^([ \t]*)<!--\s*include:\s*(\S+?)\s*-->[ \t]*$", re.M)

# href="..." / src="..." cujo valor deve ser reescrito com o prefixo "../"
# correto quando a página de saída não está na raiz do projeto. Excluídos por
# construção do regex: esquema absoluto (http, //, data:), âncora (#), e
# protocolo (mailto:, tel:) — nenhum desses é um caminho de arquivo do projeto.
ASSET_ATTR = re.compile(r'((?:href|src)=")(?!https?:|//|data:|#|mailto:|tel:)([^"]+)(")')

AVISO = (
    "<!-- ARQUIVO GERADO por tools/build.py — não editar aqui.\n"
    "     Edite o fonte em src/ ou o partial em components/. -->\n"
)


def resolve(text: str, stack: frozenset) -> str:
    """Troca cada diretiva de include pelo conteúdo do partial, recursivamente."""

    def replace(match: re.Match) -> str:
        indent, rel = match.group(1), match.group(2)
        path = (ROOT / rel).resolve()

        if path in stack:
            cadeia = " -> ".join(p.name for p in stack) + f" -> {path.name}"
            raise ValueError(f"include circular: {cadeia}")
        if not path.is_file():
            raise FileNotFoundError(f"partial não encontrado: {rel}")

        conteudo = resolve(path.read_text(encoding="utf-8").rstrip("\n"), stack | {path})

        # Reaplica o recuo da diretiva em cada linha, preservando linhas vazias.
        return "\n".join(
            (indent + linha) if linha.strip() else linha
            for linha in conteudo.split("\n")
        )

    return INCLUDE.sub(replace, text)


def reescreve_profundidade(html: str, profundidade: int) -> str:
    """Prefixa cada href/src relativo-à-raiz com "../" × profundidade.

    profundidade 0 (página na raiz, ex. index.html) não mexe em nada — é o
    caso de toda página até a Fase 4. profundidade 1 (ex.
    especialidades/implantes.html) transforma "styles/tokens.css" em
    "../styles/tokens.css", e "especialidades/clareamento.html" (link de uma
    página de especialidade para outra) em "../especialidades/clareamento.html",
    que resolve de volta para o caminho correto a partir de onde o arquivo
    realmente está no disco.
    """
    if profundidade == 0:
        return html
    prefixo = "../" * profundidade
    return ASSET_ATTR.sub(lambda m: f"{m.group(1)}{prefixo}{m.group(2)}{m.group(3)}", html)


def build(src_file: Path) -> Path:
    rel_src = src_file.relative_to(SRC)
    dest = ROOT / rel_src
    profundidade = len(rel_src.parts) - 1

    saida = resolve(src_file.read_text(encoding="utf-8"), frozenset({src_file.resolve()}))
    saida = reescreve_profundidade(saida, profundidade)

    # O aviso entra depois do doctype, para não deslocar a primeira linha.
    if saida.lstrip().lower().startswith("<!doctype"):
        fim = saida.index(">") + 1
        saida = saida[:fim] + "\n" + AVISO + saida[fim:].lstrip("\n")
    else:
        saida = AVISO + saida

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(saida, encoding="utf-8")
    n = len(INCLUDE.findall(src_file.read_text(encoding="utf-8")))
    print(f"  {src_file.relative_to(ROOT)} -> {dest.relative_to(ROOT)} ({n} include(s) de topo)")
    return dest


if __name__ == "__main__":
    alvos = [Path(a) for a in sys.argv[1:]] or sorted(SRC.glob("**/*.html"))
    if not alvos:
        sys.exit("nada para montar: src/ está vazio")
    print("montando:")
    for alvo in alvos:
        build(alvo if alvo.is_absolute() else ROOT / alvo)
