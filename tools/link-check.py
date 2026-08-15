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
# Os 5 templates de especialidade e contato.html saíram daqui na Fase 5 — as
# páginas passaram a existir de verdade.
PENDENTES = {
    "#instagram": "perfil externo",
    "#facebook": "perfil externo",
    "#youtube": "perfil externo",
    "privacidade.html": "página legal — fora do escopo do Bible",
    "termos.html": "página legal — fora do escopo do Bible",
}

PAGINA_PRINCIPAL = "index.html"

# Folhas técnicas internas. Elas demonstram Navbar e Footer fora da Home, então
# uma âncora de seção que não tenha sido corrigida para "index.html#..." não
# resolveria ali — o componente está correto, o contexto é que é outro. Isso é
# informação, não defeito; o que seria defeito é a âncora não existir nem na Home.
PAGINAS_DEMO = {"componentes.html", "styleguide.html"}

PAGINAS = [
    PAGINA_PRINCIPAL,
    "componentes.html",
    "styleguide.html",
    "contato.html",
    "especialidades/implantes.html",
    "especialidades/lentes-de-contato-dental.html",
    "especialidades/harmonizacao-facial.html",
    "especialidades/ortodontia-estetica.html",
    "especialidades/clareamento.html",
]


def ids_de(nome: str) -> set:
    pagina = RAIZ / nome
    if not pagina.is_file():
        return set()
    return set(re.findall(r'id="([^"]+)"', pagina.read_text(encoding="utf-8")))


def conferir(pagina: Path, ids_home: set):
    html = pagina.read_text(encoding="utf-8")

    # Comentários HTML saem antes da extração. Sem isto, um href citado dentro
    # de um comentário — explicando justamente por que aquele href NÃO deve
    # existir — é lido como link de verdade e acusado como quebrado. Aconteceu:
    # o comentário do molde de CTA em Services/services.html derrubou o
    # link-check com um "#" que não existe em lugar nenhum da página renderizada.
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)

    ids = set(re.findall(r'id="([^"]+)"', html))
    hrefs = re.findall(r'href="([^"]+)"', html)
    ehDemo = pagina.name in PAGINAS_DEMO

    ok, pendentes, demo, quebrados = [], [], [], []

    for href in dict.fromkeys(hrefs):
        if href.startswith(("http://", "https://", "mailto:", "tel:", "data:")):
            continue
        # PENDENTES é declarado com caminhos relativos à raiz; em página
        # aninhada o href já foi reescrito com "../" na frente pelo build.py.
        # Normaliza antes de comparar, senão "../privacidade.html" não bate
        # com a chave "privacidade.html" e vira falso QUEBRADO.
        href_normalizado = re.sub(r"^(\.\./)+", "", href)
        if href_normalizado in PENDENTES:
            pendentes.append(href)
        elif href.startswith("#"):
            if href[1:] in ids:
                ok.append(href)
            elif ehDemo and href[1:] in ids_home:
                demo.append(href)
            else:
                quebrados.append(href)
        else:
            # Relativo à PASTA da página, não à raiz do projeto — necessário
            # desde a Fase 5, quando páginas passaram a existir fora da raiz
            # (especialidades/*.html) e seus links vêm prefixados com "../".
            # Resolver sempre contra RAIZ fazia "../index.html" apontar para
            # fora do projeto em vez de para o índice real.
            alvo = (pagina.parent / href.split("#")[0]).resolve()
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
            chave = re.sub(r"^(\.\./)+", "", href)
            print(f"  PENDENTE  {href}  ({PENDENTES[chave]})")
        for href in quebrados:
            print(f"  QUEBRADO  {href}")

        total_quebrados += len(quebrados)

    print()
    if total_quebrados:
        sys.exit(f"{total_quebrados} link(s) quebrado(s).")
    print("Nenhum link quebrado. Pendentes sao de fases futuras, por decisao.")
