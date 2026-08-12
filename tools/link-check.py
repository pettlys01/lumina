#!/usr/bin/env python3
"""
Confere os links internos das páginas montadas.

O Project Bible (Seção 5) proíbe beco sem saída: todo caminho leva a algum
lugar. Um href para uma âncora inexistente não dá erro nenhum no navegador —
o clique simplesmente não faz nada, que é o pior tipo de link quebrado, porque
não aparece em log nem em teste de carregamento.

Classifica cada link em três grupos:
  OK        — âncora existe na própria página, ou o arquivo de destino existe;
  PENDENTE  — arquivo previsto para uma fase futura (lista abaixo);
  QUEBRADO  — nem uma coisa nem outra. Sai com código 1.

Uso: python tools/link-check.py
"""

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# Destinos que ainda não existem por decisão de faseamento, não por engano.
PENDENTES = {
    "contato.html": "Fase 5",
    "especialidades/implantes.html": "Fase 5",
    "especialidades/lentes-de-contato-dental.html": "Fase 5",
    "especialidades/harmonizacao-facial.html": "Fase 5",
    "especialidades/ortodontia-estetica.html": "Fase 5",
    "especialidades/clareamento.html": "Fase 5",
    "#instagram": "perfil externo",
    "#facebook": "perfil externo",
    "#youtube": "perfil externo",
    "#privacidade": "página legal",
    "#termos": "página legal",
}

PAGINA_PRINCIPAL = "index.html"

# Folhas técnicas internas. Elas demonstram Navbar e Footer fora da Home, então
# âncoras como #especialidades naturalmente não resolvem ali — o componente está
# correto, o contexto é que é outro. Isso é informação, não defeito; o que seria
# defeito é a âncora não existir nem na Home.
PAGINAS_DEMO = {"componentes.html", "styleguide.html"}

PAGINAS = [PAGINA_PRINCIPAL, "componentes.html", "styleguide.html"]


def ids_de(nome: str) -> set:
    pagina = RAIZ / nome
    if not pagina.is_file():
        return set()
    return set(re.findall(r'id="([^"]+)"', pagina.read_text(encoding="utf-8")))


def conferir(pagina: Path, ids_home: set):
    html = pagina.read_text(encoding="utf-8")
    ids = set(re.findall(r'id="([^"]+)"', html))
    hrefs = re.findall(r'href="([^"]+)"', html)
    ehDemo = pagina.name in PAGINAS_DEMO

    ok, pendentes, demo, quebrados = [], [], [], []

    for href in dict.fromkeys(hrefs):
        if href.startswith(("http://", "https://", "mailto:", "tel:", "data:")):
            continue
        if href in PENDENTES:
            pendentes.append(href)
        elif href.startswith("#"):
            if href[1:] in ids:
                ok.append(href)
            elif ehDemo and href[1:] in ids_home:
                demo.append(href)
            else:
                quebrados.append(href)
        else:
            alvo = (RAIZ / href.split("#")[0]).resolve()
            (ok if alvo.is_file() else quebrados).append(href)

    return ok, pendentes, demo, quebrados


if __name__ == "__main__":
    total_quebrados = 0
    ids_home = ids_de(PAGINA_PRINCIPAL)

    for nome in PAGINAS:
        pagina = RAIZ / nome
        if not pagina.is_file():
            continue

        ok, pendentes, demo, quebrados = conferir(pagina, ids_home)
        print(f"\n{nome}")
        print(f"  {len(ok)} ok"
              + (f", {len(demo)} fora de contexto (resolvem na Home)" if demo else ""))

        for href in pendentes:
            print(f"  PENDENTE  {href}  ({PENDENTES[href]})")
        for href in quebrados:
            print(f"  QUEBRADO  {href}")

        total_quebrados += len(quebrados)

    print()
    if total_quebrados:
        sys.exit(f"{total_quebrados} link(s) quebrado(s).")
    print("Nenhum link quebrado. Pendentes sao de fases futuras, por decisao.")
