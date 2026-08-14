#!/usr/bin/env python3
"""
Gera os placeholders de imagem da Fase 4.

Por que um gerador e não oito SVGs escritos à mão: escritos um a um, eles
divergiriam em paleta e em linguagem visual, e a página inteira pareceria
remendada. Saindo todos do mesmo sistema — mesma paleta quente do Hero, mesma
luz suave, mesmo grão —, a Home lê como um conjunto coerente mesmo antes de
existir fotografia real.

Nenhum deles tem rótulo "placeholder" impresso: um carimbo desses apareceria na
revisão e derrubaria a leitura de alto padrão que o brief exige. A pendência
está registrada no Project Bible e na folha de revisão, não na imagem.

Uso:  python tools/placeholders.py
Saída: assets/img/*.svg
"""

from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "assets" / "img"

# Paleta derivada dos tokens da marca, em tons de ambiente.
TONS = {
    "claro":  ("#F1ECE2", "#DED6C8", "#B9AE9B"),
    "medio":  ("#E4DACA", "#C9BCA6", "#9C8F7C"),
    "quente": ("#EFE2CE", "#D4BE9C", "#A88E6A"),
    "frio":   ("#E6E4DE", "#C7C4BA", "#96938A"),
    "fundo":  ("#D8CFC0", "#B4A692", "#7E7364"),
}


def base(w, h, tom, titulo, corpo, vinheta=0.22):
    """Moldura comum: gradiente de parede, piso, bloom de luz, vinheta, grão."""
    c1, c2, c3 = TONS[tom]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">
  <title>{titulo}</title>
  <defs>
    <linearGradient id="g1" x1="0" y1="0" x2="0.35" y2="1">
      <stop offset="0" stop-color="{c1}"/>
      <stop offset="0.6" stop-color="{c2}"/>
      <stop offset="1" stop-color="{c3}"/>
    </linearGradient>
    <radialGradient id="luz" cx="0.3" cy="0.22" r="0.7">
      <stop offset="0" stop-color="#FFFBF2" stop-opacity="0.9"/>
      <stop offset="0.5" stop-color="#FFF6E8" stop-opacity="0.3"/>
      <stop offset="1" stop-color="#FFF6E8" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="vin" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#3A3123" stop-opacity="0"/>
      <stop offset="1" stop-color="#3A3123" stop-opacity="{vinheta}"/>
    </linearGradient>
    <filter id="grao">
      <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="3" stitchTiles="stitch"/>
      <feColorMatrix type="saturate" values="0"/>
    </filter>
  </defs>
  <rect width="{w}" height="{h}" fill="url(#g1)"/>
{corpo}
  <rect width="{w}" height="{h}" fill="url(#luz)"/>
  <rect width="{w}" height="{h}" fill="url(#vin)"/>
  <rect width="{w}" height="{h}" filter="url(#grao)" opacity="0.05"/>
</svg>
'''


def ambiente(w, h, tom, titulo):
    """Interior amplo: janela alta à esquerda, feixe de luz, mobiliário baixo."""
    hz = int(h * 0.72)
    corpo = f'''  <rect y="{hz}" width="{w}" height="{h - hz}" fill="#A2947F" opacity="0.55"/>
  <rect x="{int(w*0.07)}" y="{int(h*0.09)}" width="{int(w*0.19)}" height="{int(h*0.58)}" fill="#FCF8EF" opacity="0.7"/>
  <rect x="{int(w*0.07)}" y="{int(h*0.09)}" width="{int(w*0.19)}" height="{int(h*0.58)}" fill="none" stroke="#9C8F7C" stroke-width="2" opacity="0.45"/>
  <polygon points="{int(w*0.26)},{int(h*0.15)} {int(w*0.62)},{hz} {int(w*0.26)},{hz}" fill="#FFFDF7" opacity="0.28"/>
  <rect x="{int(w*0.68)}" y="0" width="{int(w*0.22)}" height="{hz}" fill="#C9B79C" opacity="0.45"/>
  <rect x="{int(w*0.12)}" y="{int(h*0.63)}" width="{int(w*0.24)}" height="{max(6, int(h*0.012))}" rx="3" fill="#8E8271" opacity="0.7"/>'''
    return base(w, h, tom, titulo, corpo)


def detalhe(w, h, tom, titulo):
    """Close de equipamento: formas cilíndricas e um arco de metal escovado."""
    cx, cy = int(w * 0.55), int(h * 0.55)
    corpo = f'''  <circle cx="{cx}" cy="{cy}" r="{int(min(w,h)*0.3)}" fill="#FBF6EC" opacity="0.5"/>
  <circle cx="{cx}" cy="{cy}" r="{int(min(w,h)*0.3)}" fill="none" stroke="#8E8271" stroke-width="2" opacity="0.4"/>
  <rect x="{int(w*0.12)}" y="{int(h*0.42)}" width="{int(w*0.3)}" height="{int(h*0.1)}" rx="{int(h*0.05)}" fill="#B9AE9B" opacity="0.75"/>
  <path d="M {int(w*0.3)} {int(h*0.78)} Q {int(w*0.55)} {int(h*0.58)} {int(w*0.82)} {int(h*0.76)}"
        fill="none" stroke="#FDFAF3" stroke-width="{max(3,int(h*0.012))}" opacity="0.55"/>'''
    return base(w, h, tom, titulo, corpo)


def retrato(w, h, tom, titulo):
    """Retrato: silhueta suave contra parede iluminada, sem feições."""
    cx = int(w * 0.5)
    corpo = f'''  <ellipse cx="{cx}" cy="{int(h*0.34)}" rx="{int(w*0.17)}" ry="{int(w*0.2)}" fill="#9C8F7C" opacity="0.5"/>
  <path d="M {int(w*0.16)} {h} Q {int(w*0.2)} {int(h*0.6)} {cx} {int(h*0.57)}
           Q {int(w*0.8)} {int(h*0.6)} {int(w*0.84)} {h} Z" fill="#8E8271" opacity="0.55"/>
  <rect x="{int(w*0.04)}" y="{int(h*0.06)}" width="{int(w*0.2)}" height="{int(h*0.5)}" fill="#FCF8EF" opacity="0.45"/>'''
    return base(w, h, tom, titulo, corpo, vinheta=0.3)


def plano_digital(w, h, titulo):
    """
    Metade "digital" da comparação de método na seção que antes se chamava
    Antes e Depois (ver Project Bible, Seção 12.2: para clínica — pessoa
    jurídica —, antes/depois de resultado de paciente é vedado pelo CROSP; a
    seção virou comparação de MÉTODO, moldagem física × plano digital, e o
    lado físico já é fotografia real).

    Deliberadamente estilizada, não fotorrealista: uma grade fina e
    marcadores ao longo do arco leem como plano/visualização, nunca como
    screenshot de um software real. Uma foto de tela de verdade exigiria ou
    inventar dado de paciente, ou usar uma captura real — a primeira tentativa
    de fonte encontrou exatamente isso, nome e ID de paciente real visíveis
    numa foto de banco de imagem. A saída é não fingir a captura.
    """
    arco = f'M {int(w*0.26)} {int(h*0.48)} Q {int(w*0.5)} {int(h*0.74)} {int(w*0.74)} {int(h*0.48)}'
    marcadores = "\n".join(
        f'  <rect x="{x-5}" y="{y-5}" width="10" height="10" fill="none" '
        f'stroke="#A88E6A" stroke-width="1.2" transform="rotate(45 {x} {y})"/>'
        for x, y in [
            (int(w*0.34), int(h*0.565)), (int(w*0.42), int(h*0.615)),
            (int(w*0.50), int(h*0.635)), (int(w*0.58), int(h*0.615)),
            (int(w*0.66), int(h*0.565)),
        ]
    )
    grade = "\n".join(
        f'  <line x1="0" y1="{int(h*f)}" x2="{w}" y2="{int(h*f)}" stroke="#96938A" stroke-width="1" opacity="0.14"/>'
        for f in (0.28, 0.5, 0.72)
    ) + "\n" + "\n".join(
        f'  <line x1="{int(w*f)}" y1="0" x2="{int(w*f)}" y2="{h}" stroke="#96938A" stroke-width="1" opacity="0.14"/>'
        for f in (0.3, 0.5, 0.7)
    )
    corpo = f'''{grade}
  <ellipse cx="{int(w*0.5)}" cy="{int(h*0.5)}" rx="{int(w*0.32)}" ry="{int(h*0.34)}" fill="#EEF1F0" opacity="0.5"/>
  <path d="{arco}" fill="none" stroke="#FFFFFF" stroke-width="{int(h*0.055)}" stroke-linecap="round" opacity="0.65"/>
  <path d="{arco}" fill="none" stroke="#7E7364" stroke-width="1.5" opacity="0.35"/>
{marcadores}'''
    return base(w, h, "frio", titulo, corpo, vinheta=0.16)


# Ambiente, equipamento, equipe e depoimento passaram a usar fotografia real.
# A metade física da comparação de método também (assets/img/moldagem.jpg).
# Só a metade digital continua gerada — ver a nota da função acima.
ARQUIVOS = [
    ("plano-digital.svg", lambda: plano_digital(1200, 675, "Ilustração esquemática do plano digital do sorriso")),
]


if __name__ == "__main__":
    SAIDA.mkdir(parents=True, exist_ok=True)
    for nome, fabrica in ARQUIVOS:
        destino = SAIDA / nome
        destino.write_text(fabrica(), encoding="utf-8")
        print(f"  {nome} ({destino.stat().st_size // 1024 or 1} KB)")
    print(f"{len(ARQUIVOS)} placeholders gerados em assets/img/")
