#!/usr/bin/env python3
"""
LUT do projeto — correção de cor única, aplicada a TODAS as imagens.

O problema que isto resolve (medido, não suposto): as fotos do site vinham de
origens diferentes e nunca tinham passado por direção de arte. Medindo a matiz
média de cada uma em OKLCH:

    hero.png      H = 149.9°   fria-verde
    sobre.jpg     H =  96.5°   quente
    depoimento    H =  44.1°   quente (âmbar)
    equipe-3      H =  50.4°   quente (âmbar)

Uma foto a 150° ao lado de outra a 44° briga muito mais aos olhos do que
qualquer token de cor — foi essa a queixa real ("as cores não estão
combinando"), e a causa não estava na paleta. Nenhuma clínica de verdade tem
fotos de procedências diferentes na mesma página; estúdio nenhum entrega
campanha sem passar tudo pelo mesmo tratamento.

A correção é um pipeline só, com os mesmos parâmetros para todo arquivo. O
objetivo não é deixar cada foto "bonita" isoladamente — é deixar todas
parecendo fotografadas no mesmo dia, com a mesma câmera e a mesma luz.

Ordem das etapas (cada uma existe por um motivo):

  1. BALANÇO DE BRANCO (gray-world). Normaliza o dominante de cor de cada
     imagem para um ponto de partida comum. É a etapa que faz o trabalho
     pesado da consistência: sem ela, as etapas seguintes só aplicariam o
     mesmo verniz sobre dominantes diferentes, e a diferença continuaria.
     Aplicado a 85% e não 100% de propósito — gray-world puro achata a
     intenção do fotógrafo e tira o clima de janela/luz natural.

  2. CURVA TONAL, em OKLab. Pretos levemente levantados (look de filme, evita
     o preto digital "furado") e uma curva em S suave para dar densidade.
     Feito no L do OKLab, não no RGB: mexer no RGB desloca a matiz junto e
     é como as peles ficam alaranjadas.

  3. DESSATURAÇÃO. Escala o croma. A paleta do site tem croma baixo em tudo
     (nenhum token passa de C=0.07); foto saturada ao lado de interface
     contida denuncia que as duas coisas foram feitas separadamente.

  4. SPLIT TONING. Sombras puxadas para o verde da marca, luzes deixadas
     levemente quentes. É o que cria a assinatura — a "mesma luz" — e o que
     amarra a fotografia à identidade sem tingir a imagem inteira de verde
     (erro da versão anterior, que usava mix-blend-mode e colorizava tudo).

  5. PROTEÇÃO DE PELE. Pixels na faixa de matiz de pele recebem o split
     toning atenuado. Sem isto, retrato de equipe fica com cara de doente —
     e o rosto é justamente onde o olho detecta cor errada primeiro.

Originais ficam em assets/img/raw/ e nunca são alterados; este script sempre
lê de lá e escreve em assets/img/. Assim a graduação é reexecutável: mudou o
parâmetro, roda de novo, sem perda geracional de qualidade.

Uso:
    python tools/grade.py            # grada tudo
    python tools/grade.py --check    # só mede e relata, não escreve
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
ORIGEM = RAIZ / "assets" / "img" / "raw"
DESTINO = RAIZ / "assets" / "img"

# --------------------------------------------------------------------------
# Parâmetros da LUT. Estes seis números SÃO a identidade fotográfica do site:
# mudar qualquer um deles muda todas as imagens de uma vez, que é exatamente
# a propriedade que se quer de uma direção de arte.
# --------------------------------------------------------------------------
FORCA_WB = 0.92       # 1.0 = neutro absoluto; abaixo disso preserva o clima
LEVANTAR_PRETOS = 0.045
FORCA_CURVA_S = 0.22  # 0 = linear
ESCALA_CROMA = 0.62   # 1.0 = saturação original
FORCA_SPLIT = 0.030   # deslocamento em OKLab (unidades pequenas: a/b vão a ~0.1)
PROTECAO_PELE = 0.65  # quanto do split é retirado sobre pele (0 = sem proteção)

# Viés comum. O gray-world zera o dominante de CADA imagem, mas zerar não é o
# mesmo que igualar: sobra o ruído residual de cada foto, e uma página de
# imagens neutras-mas-aleatórias continua sem assinatura. Este deslocamento
# fixo é aplicado por igual em todas — é ele que faz a série parecer uma
# escolha de laboratório, e não nove arquivos coincidentemente lavados.
VIES_COMUM = 0.014
FORCA_TRIM = 0.85     # ver "trim final" em graduar()

# --------------------------------------------------------------------------
# Peças gráficas: tratamento leve, e por um motivo de princípio.
#
# Os slides de especialidade não são fotografia — são composições com título e
# parágrafos GRAVADOS em pixel sobre uma metade fotográfica. O pipeline
# completo foi desenhado para foto: levantar pretos e cortar croma a 0.62
# lavaria justamente o texto, que já é a parte mais frágil (não pode ser
# aumentado, selecionado nem relido pelo navegador).
#
# Mas ignorá-los também não serve: medidos, ficam em a≈+0.010 enquanto as
# fotos graduadas ficam em a≈-0.014 — 0.0301 de distância, acima do critério
# de 0.020 da Seção 4.5. Numa mesma página isso aparece como um bloco morno no
# meio de um conjunto frio.
#
# Solução: só balanço de branco e trim de dominante. Corrige o desvio de cor
# sem encostar no contraste do que está escrito.
# --------------------------------------------------------------------------
GRAFICOS = {
    "implantes.png", "lentes.png", "harmonizacao.png",
    "ortodontia.png", "clareamento.png",
}

# --------------------------------------------------------------------------
# Recorte dos slides: fica só a metade fotográfica.
#
# A arte veio com título, dois parágrafos e um ícone gravados na metade
# esquerda. Isso quebrava de três formas: o texto não é lido pelo Google nem
# por leitor de tela, não reflui no celular, e — a queixa que fechou a
# decisão — fica pequeno demais para ler no próprio desktop, porque foi
# composto a 1536px e exibido a menos da metade disso.
#
# Cortando fora o painel de texto, sobra fotografia limpa. O título e a
# descrição passam a ser HTML de verdade ao lado da imagem, que é onde eles
# sempre deveriam ter estado: escalam com a preferência de fonte, aceitam
# zoom, aparecem na busca e podem ser traduzidos.
#
# 48% medido, não estimado: a energia vertical por coluna (textura da foto
# contra fundo liso do painel) apontou o início da fotografia entre 38% e 48%
# em quatro das cinco. A quinta (clareamento) tem fundo claro e texturizado
# que confunde a medição, então vale o corte mais conservador do grupo.
# --------------------------------------------------------------------------
CORTE_GRAFICO = 0.48

# Depois de tirar o painel de texto sobra 799x1024 — retrato de 0.78:1. Exibido
# num espaço deitado ao lado do texto, o object-fit:cover comia topo e base e a
# foto parecia cortada errado (foi a queixa). Quadrado resolve: cabe ao lado do
# texto sem ficar alto demais e sem sofrer recorte adicional na exibição.
#
# 0.38 e não 0.5 no ancoramento vertical porque o assunto — dente, sorriso,
# rosto — fica no terço superior em todas as cinco. Centralizar cortaria a
# parte que interessa e deixaria bancada sobrando embaixo.
QUADRADO_ANCORA = 0.38

# --------------------------------------------------------------------------
# Teto de resolução na saída.
#
# As fotos de caso chegaram em 2400px e pesavam 5,6 MB no conjunto — mais que
# o resto do site inteiro. O maior espaço em que qualquer uma delas aparece é
# o comparador em tela larga, ~800px; 1600px cobre isso com folga em tela de
# alta densidade (2x) e nada além disso é visto por ninguém.
#
# O original em raw/ continua no tamanho que veio: quem manda no arquivo
# entregue é este número, e ele pode subir depois sem perda.
# --------------------------------------------------------------------------
LARGURA_MAX = 1600

VERDE_MARCA = "#285C4D"


# ---------- conversões (Björn Ottosson) -----------------------------------

def srgb_para_linear(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def linear_para_srgb(c):
    c = np.clip(c, 0.0, 1.0)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def linear_para_oklab(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = np.cbrt(l), np.cbrt(m), np.cbrt(s)
    return np.stack([
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    ], axis=-1)


def oklab_para_linear(lab):
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    return np.stack([
        +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    ], axis=-1)


def hex_para_oklab(hx):
    h = hx.lstrip("#")
    rgb = np.array([[[int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]]])
    return linear_para_oklab(srgb_para_linear(rgb))[0, 0]


# ---------- o pipeline ----------------------------------------------------

def graduar(img, leve=False):
    """Recebe e devolve array float 0..1 em sRGB.

    leve=True: só balanço de branco e trim de dominante, sem curva tonal, sem
    dessaturação e sem split toning. Ver GRAFICOS, acima."""
    lin = srgb_para_linear(img)

    # Máscara de pele medida na imagem ORIGINAL, antes de qualquer correção.
    # Tem que ser aqui: o balanço de branco abaixo já tira o calor da pele, e
    # depois dele a detecção não acha mais o que procurava. Medido num close
    # de rosto: a máscara pegava 87,3% dos pixels antes do balanço e só 36,9%
    # depois, com o croma da pele caindo de 0,069 para 0,021.
    lab0 = linear_para_oklab(lin)
    matiz0 = np.degrees(np.arctan2(lab0[..., 2], lab0[..., 1])) % 360
    croma0 = np.hypot(lab0[..., 1], lab0[..., 2])
    eh_pele = ((matiz0 > 25) & (matiz0 < 85) & (croma0 > 0.02)).astype(np.float64)
    fator_pele = 1.0 - eh_pele * PROTECAO_PELE

    # 1. Balanço de branco por gray-world, em luz linear (a média só faz
    #    sentido física aqui; feita em sRGB ela é enviesada pelo gama).
    #
    #    A média sai dos pixels SEM PELE. Gray-world parte da premissa de que a
    #    cena inteira deveria dar cinza — o que é razoável para um corredor e
    #    desastroso para um rosto, onde a cena É a pele quente. Medido, ele
    #    aplicava R×0,648 e B×1,746 e devolvia um rosto cinza-esverdeado.
    #    Medindo só o fundo, o balanço passa a corrigir a LUZ do ambiente, que
    #    é o que ele deveria fazer, sem tratar a pessoa como desvio de cor.
    peso_fundo = (1.0 - eh_pele)[..., None]
    soma_fundo = peso_fundo.sum()
    if soma_fundo > lin[..., 0].size * 0.08:   # há fundo suficiente para medir
        media = (lin * peso_fundo).reshape(-1, 3).sum(axis=0) / soma_fundo
    else:
        # Quadro quase todo pele: não há referência neutra confiável, então o
        # balanço recua em vez de inventar uma.
        media = lin.reshape(-1, 3).mean(axis=0)
        media = media + (media.mean() - media) * 0.7

    alvo = media.mean()
    ganho = np.where(media > 1e-6, alvo / media, 1.0)
    ganho = 1.0 + (ganho - 1.0) * FORCA_WB
    lin = np.clip(lin * ganho, 0.0, 1.0)

    lab = linear_para_oklab(lin)
    L = lab[..., 0]

    # Caminho leve das peças gráficas: pula tudo que mexeria no contraste do
    # texto gravado e vai direto ao trim de dominante.
    if leve:
        verde = hex_para_oklab(VERDE_MARCA)
        dv = np.array([verde[1], verde[2]])
        dv = dv / np.linalg.norm(dv)
        a = lab[..., 1] + (dv[0] * VIES_COMUM - lab[..., 1].mean()) * FORCA_TRIM
        b = lab[..., 2] + (dv[1] * VIES_COMUM - lab[..., 2].mean()) * FORCA_TRIM
        return linear_para_srgb(oklab_para_linear(np.stack([L, a, b], axis=-1)))

    # 2. Curva tonal. Pretos levantados primeiro, curva em S depois — na
    #    ordem inversa a curva desfaria parte do levantamento.
    L = LEVANTAR_PRETOS + L * (1.0 - LEVANTAR_PRETOS)
    Ln = np.clip(L, 0.0, 1.0)
    suave = Ln * Ln * (3.0 - 2.0 * Ln)          # smoothstep = S natural
    L = Ln * (1.0 - FORCA_CURVA_S) + suave * FORCA_CURVA_S

    # A máscara de pele (eh_pele / fator_pele) vem medida lá de cima, na imagem
    # original. Ela pesa QUATRO etapas: balanço de branco, dessaturação, split
    # toning e trim. Proteger só o split — como era antes — não bastava: as
    # outras três continuavam puxando a pele para o verde da marca, e as fotos
    # de rosto saíam cinza-esverdeadas.
    #
    # É o que uma sala de cor de verdade faz: grada a cena e protege o tom de
    # pele, porque o olho perdoa uma parede fora de cor e não perdoa um rosto
    # doente.

    # 3. Dessaturação, atenuada onde há pele: a cena inteira perde croma, o
    #    rosto conserva quase todo o dele.
    escala = ESCALA_CROMA + (1.0 - ESCALA_CROMA) * eh_pele * PROTECAO_PELE
    a = lab[..., 1] * escala
    b = lab[..., 2] * escala

    # 4. Split toning. Peso quadrático: concentra o verde nas sombras em vez
    #    de espalhar por toda a imagem.
    verde = hex_para_oklab(VERDE_MARCA)
    dir_verde = np.array([verde[1], verde[2]])
    dir_verde = dir_verde / np.linalg.norm(dir_verde)

    peso_sombra = (1.0 - np.clip(L, 0.0, 1.0)) ** 2
    peso_luz = np.clip(L, 0.0, 1.0) ** 2

    # 5. O split toning recua sobre pele, usando a mesma máscara medida acima.
    a = a + dir_verde[0] * FORCA_SPLIT * peso_sombra * fator_pele
    b = b + dir_verde[1] * FORCA_SPLIT * peso_sombra * fator_pele

    # Viés comum, sem peso por luminosidade: aplicado igual do preto ao
    # branco, é o que ancora todas as imagens no mesmo ponto de (a,b).
    a = a + dir_verde[0] * VIES_COMUM * fator_pele
    b = b + dir_verde[1] * VIES_COMUM * fator_pele

    # Luzes levemente quentes: o contraponto que impede o resultado de virar
    # monocromático verde. b positivo = amarelo em OKLab.
    b = b + 0.010 * peso_luz

    # ---- Trim final (o "match" da sala de cor) ----------------------------
    # O gray-world normaliza a media em RGB LINEAR, e isso nao zera a media em
    # OKLab: a conversao entre os dois espacos e nao-linear, entao cada foto
    # termina com um residuo proprio. Medido: mesmo depois de tudo acima, a
    # dispersao entre as imagens caiu so 37%.
    #
    # Este passo mede o dominante que a imagem REALMENTE tem no fim do
    # pipeline e o desloca para o alvo comum. E a diferenca entre "apliquei o
    # mesmo tratamento em todas" e "todas terminaram no mesmo lugar" — so a
    # segunda produz a sensacao de mesma camera, mesmo dia.
    #
    # A 0.85 e nao 1.0 de proposito: forcar a media exata apagaria diferencas
    # legitimas de conteudo (uma foto cheia de planta TEM mais verde que um
    # teto branco, e deve ter).
    #
    # O erro medido a partir dos pixels SEM pele. Num retrato de rosto inteiro
    # a pele domina o quadro, então incluí-la na média faria o trim tentar
    # "corrigir" o tom de pele para verde — e o resto da cena junto. Medindo só
    # o fundo, o alvo passa a ser o ambiente, que é o que precisa casar com as
    # outras fotos do site.
    alvo_a = dir_verde[0] * VIES_COMUM
    alvo_b = dir_verde[1] * VIES_COMUM

    peso_fundo = 1.0 - eh_pele
    total_fundo = peso_fundo.sum()
    if total_fundo > a.size * 0.05:      # há fundo suficiente para medir
        media_a = (a * peso_fundo).sum() / total_fundo
        media_b = (b * peso_fundo).sum() / total_fundo
    else:                                 # quadro quase todo pele: usa tudo
        media_a, media_b = a.mean(), b.mean()

    # E o deslocamento também recua sobre a pele.
    a = a + (alvo_a - media_a) * FORCA_TRIM * fator_pele
    b = b + (alvo_b - media_b) * FORCA_TRIM * fator_pele

    saida = np.stack([L, a, b], axis=-1)
    return linear_para_srgb(oklab_para_linear(saida))


def medir(caminho):
    """Devolve (L%, a, b) medios. Deliberadamente (a,b) e nao (croma, matiz):
    perto do neutro a matiz e instavel — duas fotos quase cinzas podem estar a
    100 graus uma da outra e serem indistinguiveis a olho. A distancia
    euclidiana em (a,b) e que corresponde ao dominante percebido, e foi ela
    que expos o erro da primeira versao desta medicao."""
    im = Image.open(caminho).convert("RGB").resize((80, 80))
    arr = np.asarray(im, dtype=np.float64) / 255.0
    lab = linear_para_oklab(srgb_para_linear(arr))
    return lab[..., 0].mean() * 100, lab[..., 1].mean(), lab[..., 2].mean()


def fracao_pele(caminho):
    """Quanto do quadro é pele. Separa retrato de fotografia de ambiente."""
    im = Image.open(caminho).convert("RGB").resize((80, 80))
    arr = np.asarray(im, dtype=np.float64) / 255.0
    lab = linear_para_oklab(srgb_para_linear(arr))
    matiz = np.degrees(np.arctan2(lab[..., 2], lab[..., 1])) % 360
    croma = np.hypot(lab[..., 1], lab[..., 2])
    return float(((matiz > 25) & (matiz < 85) & (croma > 0.02)).mean())


def main():
    somente_medir = "--check" in sys.argv

    arquivos = sorted(p for p in ORIGEM.iterdir()
                      if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
    if not arquivos:
        print(f"nada em {ORIGEM}")
        return 1

    print(f"{'arquivo':22}{'antes  L / a / b':>26}{'depois  L / a / b':>26}")
    print("-" * 76)

    antes, depois = [], []
    for origem in arquivos:
        destino = DESTINO / origem.name
        La, aa, ba = medir(origem)

        eh_gr = origem.name in GRAFICOS
        # Slides saem em JPEG mesmo vindo de PNG: são 1,7 MB cada como PNG
        # (8,7 MB no conjunto), e o conteúdo é fotográfico o bastante para o
        # JPEG não deixar artefato visível. O PNG original fica intacto em raw/.
        if eh_gr:
            destino = destino.with_suffix(".jpg")

        if not somente_medir:
            im = Image.open(origem).convert("RGB")
            if eh_gr:
                im = im.crop((int(im.width * CORTE_GRAFICO), 0, im.width, im.height))
                lado = im.width
                topo = int((im.height - lado) * QUADRADO_ANCORA)
                im = im.crop((0, topo, lado, topo + lado))

            if max(im.size) > LARGURA_MAX:
                escala = LARGURA_MAX / max(im.size)
                novo = (round(im.width * escala), round(im.height * escala))
                im = im.resize(novo, Image.LANCZOS)

            arr = np.asarray(im, dtype=np.float64) / 255.0
            out = np.clip(graduar(arr, leve=eh_gr), 0.0, 1.0)
            saida = Image.fromarray((out * 255.0 + 0.5).astype(np.uint8))
            if destino.suffix.lower() == ".png":
                saida.save(destino, optimize=True)
            else:
                saida.save(destino, quality=88, optimize=True,
                           progressive=True, subsampling=1)

        Ld, ad, bd = medir(destino) if destino.exists() else (La, aa, ba)
        # Retrato ou ambiente? A pele legitimamente vive noutro ponto do eixo
        # de cor, e forçá-la ao mesmo ponto das paredes foi o que produziu os
        # rostos cinzas. Os dois grupos são medidos separadamente.
        retrato = fracao_pele(destino if destino.exists() else origem) > 0.35
        antes.append((aa, ba, retrato))
        depois.append((ad, bd, retrato))
        print(f"{origem.name:22}{La:8.1f}{aa:9.3f}{ba:9.3f}"
              f"{Ld:8.1f}{ad:9.3f}{bd:9.3f}  {'retrato' if retrato else ''}")

    def dispersao(pontos):
        if len(pontos) < 2:
            return 0.0
        return max(np.hypot(p[0] - q[0], p[1] - q[1])
                   for p in pontos for q in pontos)

    def so(pontos, eh_retrato):
        return [(a, b) for a, b, r in pontos if r == eh_retrato]

    print("-" * 76)
    print("maior diferenca de dominante entre duas imagens (OKLab a/b)")
    print("medida por grupo: pele e ambiente nao devem cair no mesmo ponto.\n")

    for rotulo, flag in (("ambiente", False), ("retratos", True)):
        da = dispersao(so(antes, flag))
        dd = dispersao(so(depois, flag))
        n = len(so(depois, flag))
        if n < 2:
            print(f"  {rotulo:9} ({n} imagem) — nada a comparar")
            continue
        veredito = "OK" if dd < 0.020 else "AINDA ALTA"
        reducao = f"  reducao {(1 - dd / da) * 100:3.0f}%" if da > 0 else ""
        print(f"  {rotulo:9} ({n:2} imagens)  antes {da:.4f}  ->  "
              f"depois {dd:.4f}  ({veredito}){reducao}")

    # ---- O par antes/depois consigo mesmo -------------------------------
    # Esta é a verificação mais dura das três, e a única cujo defeito o
    # usuário veria na hora: as duas metades de um comparador ficam uma sobre
    # a outra, e qualquer diferença de dominante entre elas aparece como um
    # salto de cor no instante em que o divisor passa. Entre imagens de seções
    # diferentes uma folga passa despercebida; aqui, não.
    print()
    print("cada par antes/depois consigo mesmo (o divisor os sobrepõe):")
    piores = 0
    for origem in arquivos:
        if not origem.name.endswith("-antes.jpg"):
            continue
        par = origem.with_name(origem.name.replace("-antes.jpg", "-depois.jpg"))
        da_, db_ = DESTINO / origem.name, DESTINO / par.name
        if not (da_.exists() and db_.exists()):
            continue
        _, a1, b1 = medir(da_)
        _, a2, b2 = medir(db_)
        d = np.hypot(a1 - a2, b1 - b2)
        ok = d < 0.004
        if not ok:
            piores += 1
        rotulo = origem.name.replace("caso-", "").replace("-antes.jpg", "")
        print(f"  {rotulo:14} {d:.4f}  {'ok' if ok else 'SALTO DE COR VISIVEL'}")
    if piores:
        print(f"\n  {piores} par(es) com diferenca perceptivel entre as metades.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
