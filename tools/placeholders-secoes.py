#!/usr/bin/env python3
"""
Placeholders das seções Resultados e Nosso Espaço.

Diferente de tools/placeholders.py (Fase 4), estes SÃO rotulados de propósito.

O gerador da Fase 4 evitava carimbo porque aqueles placeholders precisavam
sobreviver a uma revisão de design sem quebrar a leitura de alto padrão. Aqui a
situação é outra: as imagens definitivas serão geradas por IA e trocadas uma a
uma, e um placeholder sem rótulo que passe despercebido vai parar no ar
parecendo conteúdo real. Rótulo visível é o que garante que ninguém esqueça.

Some no momento em que o arquivo é substituído — o nome de saída é exatamente o
nome que a imagem final precisa ter.

Uso:  python tools/placeholders-secoes.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "assets" / "img"

# Tokens atuais (Seção 4.1-ter do Bible).
FUNDO = (250, 250, 248)
BORDA = (187, 187, 184)
VERDE = (40, 92, 77)
CINZA = (107, 107, 104)

ALVOS = [
    # (arquivo, largura, altura, rótulo)
    ("caso-diastema-antes.jpg",    1200, 900, "ANTES · diastema"),
    ("caso-diastema-depois.jpg",   1200, 900, "DEPOIS · diastema"),
    ("caso-alinhamento-antes.jpg", 1200, 900, "ANTES · alinhamento"),
    ("caso-alinhamento-depois.jpg",1200, 900, "DEPOIS · alinhamento"),
    ("caso-lentes-antes.jpg",      1200, 900, "ANTES · recontorno"),
    ("caso-lentes-depois.jpg",     1200, 900, "DEPOIS · recontorno"),
    ("caso-implante-antes.jpg",    1200, 900, "ANTES · reposição"),
    ("caso-implante-depois.jpg",   1200, 900, "DEPOIS · reposição"),
    ("espaco-1.jpg", 1400, 1050, "ESPAÇO 1 · recepção"),
    ("espaco-2.jpg", 1400, 1050, "ESPAÇO 2 · corredor"),
    ("espaco-3.jpg", 1400, 1050, "ESPAÇO 3 · atendimento"),
    ("espaco-4.jpg", 1400, 1050, "ESPAÇO 4 · planejamento"),
    ("espaco-5.jpg", 1400, 1050, "ESPAÇO 5 · esterilização"),
    ("espaco-6.jpg", 1900, 815, "ESPAÇO 6 · vista ampla"),
]


def fonte(tamanho):
    for nome in ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(nome, tamanho)
        except OSError:
            continue
    return ImageFont.load_default()


def gerar(arquivo, largura, altura, rotulo):
    im = Image.new("RGB", (largura, altura), FUNDO)
    d = ImageDraw.Draw(im)

    # Grade fina: deixa claro que é esquema, não fotografia. Mesma decisão do
    # plano-digital.svg — estética que nunca se confunde com captura real.
    passo = largura // 16
    for x in range(passo, largura, passo):
        d.line([(x, 0), (x, altura)], fill=(238, 240, 237), width=1)
    for y in range(passo, altura, passo):
        d.line([(0, y), (largura, y)], fill=(238, 240, 237), width=1)

    m = largura // 22
    d.rectangle([m, m, largura - m, altura - m], outline=BORDA, width=2)

    f1 = fonte(max(20, largura // 26))
    f2 = fonte(max(13, largura // 52))

    cx, cy = largura // 2, altura // 2
    d.text((cx, cy - largura // 40), rotulo, font=f1, fill=VERDE, anchor="mm")
    d.text((cx, cy + largura // 32), "substituir por imagem definitiva",
           font=f2, fill=CINZA, anchor="mm")
    d.text((cx, altura - m - largura // 34), arquivo,
           font=f2, fill=CINZA, anchor="mm")

    im.save(SAIDA / arquivo, quality=86, optimize=True)
    return arquivo


if __name__ == "__main__":
    for alvo in ALVOS:
        print("  gerado:", gerar(*alvo))
    print(f"\n{len(ALVOS)} placeholders em assets/img/")
    print("Trocar cada arquivo pelo definitivo, mantendo o mesmo nome.")
