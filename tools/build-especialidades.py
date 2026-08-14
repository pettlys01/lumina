#!/usr/bin/env python3
"""
Gera as cinco páginas de especialidade a partir de um template único.

Duas etapas separadas de propósito:
  1. Este script preenche components/SpecialtyPage/template.html com o
     conteúdo de cada especialidade (abaixo) e escreve em src/especialidades/.
  2. tools/build.py resolve os <!-- include: ... --> que sobraram no
     resultado (Navbar, CTA, Footer) e ajusta os caminhos pela profundidade.

Rodar antes de tools/build.py:
    python tools/build-especialidades.py && python tools/build.py

O conteúdo abaixo é intencionalmente específico por especialidade — nenhuma
das cinco reaproveita frase da outra — porque cinco páginas quase idênticas
seriam o mesmo problema de monotonia da Seção 4 do Bible, um nível abaixo.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "components" / "SpecialtyPage" / "template.html"
SAIDA = ROOT / "src" / "especialidades"

SLUGS_ORDEM = [
    "implantes",
    "lentes-de-contato-dental",
    "harmonizacao-facial",
    "ortodontia-estetica",
    "clareamento",
]

ESPECIALIDADES = {
    "implantes": {
        "titulo": "Implantes",
        "meta_title": "Implantes dentários em Pinheiros — Lumina Odontologia",
        "meta_desc": "Implante unitário ou total, planejado em tomografia e cirurgia guiada, com prótese provisória no mesmo dia em casos indicados.",
        "eyebrow": "Reabilitação oral",
        "lead": "Reposição de um ou mais dentes com raiz artificial de titânio, planejada em tomografia antes do primeiro corte.",
        "overview": [
            "O implante substitui a raiz do dente por um parafuso de titânio inserido no osso, que depois recebe uma coroa. É a alternativa que preserva o osso da região — um espaço vazio por muito tempo tende a reabsorver o osso ao redor, o que dificulta uma reposição futura.",
            "Antes de qualquer cirurgia, uma tomografia de feixe cônico mostra o volume ósseo disponível em três dimensões. É esse exame que decide se o caso é direto ou se precisa de enxerto antes do implante — decisão tomada na tela, não durante o procedimento.",
        ],
        "indicado": [
            "Perda de um dente por trauma, cárie extensa ou fratura",
            "Perda de múltiplos dentes, com prótese removível instável ou desconfortável",
            "Volume ósseo suficiente na região, confirmado por tomografia",
            "Ausência de doenças que impeçam cicatrização óssea normal",
        ],
        "etapas": [
            ("Avaliação e tomografia", "Exame clínico e tomografia de feixe cônico, para medir o osso disponível na região."),
            ("Planejamento cirúrgico digital", "A posição exata do implante é definida em software, antes da cirurgia."),
            ("Cirurgia guiada", "Inserção do implante seguindo o plano digital, com guia impresso quando o caso indica."),
            ("Prótese final", "Após a osseointegração — em geral de 8 a 16 semanas — a coroa definitiva é instalada."),
        ],
        "faq": [
            ("O implante dói?", "A cirurgia é feita com anestesia local, e o desconforto do pós-operatório costuma ser controlado com os analgésicos prescritos. A maioria dos pacientes retoma a rotina no dia seguinte."),
            ("Quanto tempo até colocar o dente definitivo?", "Depende da osseointegração do implante ao osso, que varia de pessoa para pessoa — normalmente entre 2 e 4 meses. Em casos selecionados, uma coroa provisória é instalada no mesmo dia da cirurgia."),
        ],
    },
    "lentes-de-contato-dental": {
        "titulo": "Lentes de Contato Dental",
        "meta_title": "Lentes de Contato Dental em Pinheiros — Lumina Odontologia",
        "meta_desc": "Laminados cerâmicos ultrafinos, com simulação digital do resultado antes de qualquer desgaste no dente.",
        "eyebrow": "Estética do sorriso",
        "lead": "Lâminas de porcelana de 0,2 a 0,5 mm cimentadas sobre o dente, para corrigir cor, forma ou pequenos desalinhamentos.",
        "overview": [
            "Lentes de contato dental são laminados cerâmicos muito finos, fabricados em laboratório a partir do escaneamento digital dos dentes e cimentados sobre o esmalte. Em boa parte dos casos, o desgaste do dente é mínimo — às vezes inexistente.",
            "O escaneamento também gera um ensaio virtual do sorriso: você vê o formato e a proporção antes de qualquer laminado ser fabricado, e pode pedir ajuste ainda nessa fase, sem custo de refazer peça pronta.",
        ],
        "indicado": [
            "Manchas ou escurecimento que o clareamento não resolve sozinho",
            "Diastemas (espaços entre os dentes) de pequena e média extensão",
            "Dentes com forma irregular, desgastados ou levemente rotacionados",
            "Esmalte com espessura suficiente para receber o laminado sem fragilizar o dente",
        ],
        "etapas": [
            ("Escaneamento e simulação", "Escaneamento intraoral e simulação digital do resultado final do sorriso."),
            ("Ensaio no próprio sorriso", "Impressão de um modelo de prova, posicionado na boca antes de qualquer desgaste."),
            ("Preparo mínimo", "Ajuste no esmalte apenas onde o caso exige — muitos casos dispensam essa etapa."),
            ("Cimentação", "As lentes, fabricadas em laboratório a partir da simulação aprovada, são cimentadas uma a uma."),
        ],
        "faq": [
            ("As lentes de contato dental desgastam o dente?", "Depende do caso. Quando o dente já está bem posicionado e proporcional, o laminado costuma ser aplicado com desgaste mínimo ou nenhum. Isso só é confirmado depois do escaneamento — e você é avisado antes de autorizar, não durante o preparo."),
            ("Quanto tempo dura uma lente de contato dental?", "Com higiene adequada e acompanhamento regular, a expectativa é de 10 a 15 anos. O maior risco não é o material, é hábito de hábito — como roer unha ou abrir embalagem com o dente, que fragiliza qualquer laminado."),
        ],
    },
    "harmonizacao-facial": {
        "titulo": "Harmonização Facial",
        "meta_title": "Harmonização Facial em Pinheiros — Lumina Odontologia",
        "meta_desc": "Procedimentos não cirúrgicos para equilíbrio do terço inferior da face, planejados junto do tratamento odontológico.",
        "eyebrow": "Equilíbrio facial",
        "lead": "Toxina botulínica e preenchedores para equilibrar o terço inferior da face — tratados junto do sorriso, não como procedimento isolado.",
        "overview": [
            "Harmonização facial reúne procedimentos não cirúrgicos — toxina botulínica, preenchedores de ácido hialurônico e bioestimuladores — usados para equilibrar proporções faciais. O objetivo é equilíbrio, não alterar a identidade do rosto.",
            "Na Lumina, a harmonização é planejada junto com o tratamento odontológico quando os dois se relacionam — sustentação labial após reabilitação com implantes, por exemplo, ou suavização de sulcos que mudam com o novo posicionamento dos dentes.",
        ],
        "indicado": [
            "Assimetrias leves a moderadas na região da boca, queixo ou mandíbula",
            "Perda de sustentação labial associada a tratamento odontológico",
            "Sulcos e marcas de expressão na região perioral",
            "Ausência de gestação, doenças autoimunes ativas ou uso de anticoagulantes que contraindiquem o procedimento",
        ],
        "etapas": [
            ("Avaliação facial", "Análise de proporção e simetria, com plano específico para a queixa apresentada."),
            ("Plano de aplicação", "Definição de pontos, produto e quantidade — registrado antes da aplicação."),
            ("Aplicação", "Procedimento ambulatorial, sem necessidade de afastamento da rotina."),
            ("Retorno de ajuste", "Reavaliação entre 15 e 21 dias, quando o resultado final já está estabilizado."),
        ],
        "faq": [
            ("Harmonização facial tem contraindicação?", "Tem. Gestação, algumas doenças autoimunes e uso de determinados anticoagulantes entram na avaliação inicial. Casos nessas condições são recusados ou adiados — a avaliação existe justamente para identificar isso antes de qualquer aplicação."),
            ("O resultado é definitivo?", "Não. Toxina botulínica dura em média de 4 a 6 meses, e preenchedores de 8 a 18 meses, dependendo do produto e da região. É esse caráter reversível que torna o procedimento mais seguro para ajustes graduais."),
        ],
    },
    "ortodontia-estetica": {
        "titulo": "Ortodontia Estética",
        "meta_title": "Ortodontia Estética em Pinheiros — Lumina Odontologia",
        "meta_desc": "Alinhadores transparentes e aparelhos cerâmicos, com simulação do resultado final antes do início do tratamento.",
        "eyebrow": "Alinhamento",
        "lead": "Alinhadores transparentes ou aparelhos cerâmicos, com o resultado final simulado digitalmente antes de você decidir começar.",
        "overview": [
            "A ortodontia estética corrige o posicionamento dos dentes com recursos menos visíveis que o aparelho metálico tradicional: alinhadores transparentes removíveis ou brackets cerâmicos, na cor do dente.",
            "O escaneamento inicial gera uma simulação de todas as etapas do movimento dentário até o resultado final — você vê a posição final antes de decidir começar, e o número de alinhadores ou o tempo estimado de aparelho já sai dessa simulação, não de uma estimativa genérica.",
        ],
        "indicado": [
            "Apinhamento leve a moderado",
            "Diastemas a fechar por movimentação, não por lente de contato dental",
            "Mordida cruzada ou aberta de grau leve a moderado",
            "Disponibilidade para manter os alinhadores pelo tempo diário indicado (em geral 20 a 22 horas)",
        ],
        "etapas": [
            ("Escaneamento e simulação", "Escaneamento digital e simulação de todas as etapas do movimento, até a posição final."),
            ("Confecção", "Fabricação da série de alinhadores ou instalação do aparelho cerâmico."),
            ("Acompanhamento mensal", "Troca de alinhadores ou ajuste do aparelho, com fotos comparadas à simulação original."),
            ("Contenção", "Uso de contenção após o tratamento, para manter o resultado alcançado."),
        ],
        "faq": [
            ("Alinhador transparente funciona para qualquer caso?", "Não. Casos de apinhamento severo ou problemas esqueléticos maiores costumam exigir aparelho fixo, às vezes combinado com outras intervenções. Isso é avaliado no escaneamento inicial, antes de qualquer orçamento."),
            ("Preciso usar o alinhador o dia inteiro?", "Sim — a indicação é de 20 a 22 horas por dia, retirando apenas para comer e escovar os dentes. Uso abaixo disso atrasa o resultado previsto na simulação, porque o movimento depende do tempo de uso contínuo."),
        ],
    },
    "clareamento": {
        "titulo": "Clareamento",
        "meta_title": "Clareamento Dental em Pinheiros — Lumina Odontologia",
        "meta_desc": "Clareamento em consultório ou supervisionado em casa, com protocolo definido pela sensibilidade e pelo tom de partida de cada paciente.",
        "eyebrow": "Estética do sorriso",
        "lead": "Protocolo em consultório ou supervisionado em casa, ajustado pela sensibilidade e pelo tom de partida de cada paciente — não um produto padrão para todos.",
        "overview": [
            "O clareamento usa peróxido de hidrogênio ou de carbamida para oxidar pigmentos dentro do esmalte e da dentina, clareando o dente de dentro para fora. O protocolo — concentração, tempo de aplicação e número de sessões — muda de pessoa para pessoa.",
            "Restaurações, coroas e facetas existentes não clareiam junto com o dente natural: se você tem trabalhos visíveis na região que vai clarear, isso entra na avaliação antes de começar, para não terminar com tom desigual.",
        ],
        "indicado": [
            "Escurecimento por pigmentação alimentar, tabaco ou envelhecimento natural do esmalte",
            "Ausência de cáries ou restaurações com infiltração na região a clarear",
            "Sensibilidade dentária controlável com dessensibilizante durante o protocolo",
            "Expectativa de resultado compatível com a cor de partida — não todo escurecimento clareia igual",
        ],
        "etapas": [
            ("Avaliação e cor de partida", "Registro fotográfico da cor atual e checagem de sensibilidade e restaurações existentes."),
            ("Escolha do protocolo", "Sessão em consultório, moldeira personalizada para uso em casa, ou combinação dos dois."),
            ("Execução", "Aplicação em consultório ou uso supervisionado da moldeira, conforme o protocolo definido."),
            ("Acompanhamento", "Comparação com a foto inicial e ajuste de sensibilidade, se necessário."),
        ],
        "faq": [
            ("Clareamento estraga o esmalte?", "Feito com acompanhamento profissional e concentração adequada ao caso, não há evidência de dano permanente ao esmalte. O risco aumenta com produtos de venda livre sem supervisão, que não ajustam a concentração à sua sensibilidade."),
            ("O clareamento é permanente?", "Não — o tom volta a escurecer gradualmente, em geral entre 1 e 3 anos, dependendo de hábitos como café, vinho tinto e cigarro. Um retoque periódico mantém o resultado."),
        ],
    },
}


def li(texto: str, indent: str = " " * 8) -> str:
    return f"{indent}<li>{texto}</li>"


def montar_overview(paragrafos: list[str]) -> str:
    return "\n".join(f"        <p>{p}</p>" for p in paragrafos)


def montar_indicado(itens: list[str]) -> str:
    return "\n".join(li(item) for item in itens)


def montar_etapas(etapas: list[tuple[str, str]]) -> str:
    blocos = []
    for i, (titulo, texto) in enumerate(etapas, start=1):
        blocos.append(
            f'        <li class="specialty__step">\n'
            f'          <span class="specialty__step-num" aria-hidden="true">{i}</span>\n'
            f'          <h3 class="specialty__step-title">{titulo}</h3>\n'
            f'          <p class="specialty__step-text">{texto}</p>\n'
            f'        </li>'
        )
    return "\n".join(blocos)


def montar_faq(perguntas: list[tuple[str, str]], slug: str) -> str:
    blocos = []
    for pergunta, resposta in perguntas:
        blocos.append(
            f'        <details class="faq__item" name="faq-{slug}">\n'
            f'          <summary class="faq__q">\n'
            f'            <span>{pergunta}</span>\n'
            f'            <span class="faq__icon" aria-hidden="true"></span>\n'
            f'          </summary>\n'
            f'          <div class="faq__a"><p>{resposta}</p></div>\n'
            f'        </details>'
        )
    return "\n".join(blocos)


def montar_related(slug_atual: str) -> str:
    blocos = []
    for slug in SLUGS_ORDEM:
        if slug == slug_atual:
            continue
        titulo = ESPECIALIDADES[slug]["titulo"]
        blocos.append(
            f'        <li>\n'
            f'          <a class="specialty__related-link" href="especialidades/{slug}.html">{titulo}</a>\n'
            f'        </li>'
        )
    return "\n".join(blocos)


def gerar(slug: str) -> None:
    dados = ESPECIALIDADES[slug]
    template = TEMPLATE.read_text(encoding="utf-8")

    saida = (
        template
        .replace("{{META_TITLE}}", dados["meta_title"])
        .replace("{{META_DESC}}", dados["meta_desc"])
        .replace("{{EYEBROW}}", dados["eyebrow"])
        .replace("{{TITLE_LOWER}}", dados["titulo"].lower())
        .replace("{{TITLE}}", dados["titulo"])
        .replace("{{LEAD}}", dados["lead"])
        .replace("{{OVERVIEW_HTML}}", montar_overview(dados["overview"]))
        .replace("{{INDICADO_HTML}}", montar_indicado(dados["indicado"]))
        .replace("{{STEPS_HTML}}", montar_etapas(dados["etapas"]))
        .replace("{{FAQ_HTML}}", montar_faq(dados["faq"], slug))
        .replace("{{RELATED_HTML}}", montar_related(slug))
    )

    if "{{" in saida:
        sobrou = set(__import__("re").findall(r"\{\{[A-Z_]+\}\}", saida))
        raise ValueError(f"{slug}: token(s) não preenchido(s): {sobrou}")

    destino = SAIDA / f"{slug}.html"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(saida, encoding="utf-8")
    print(f"  especialidades/{slug}.html")


if __name__ == "__main__":
    print("gerando páginas de especialidade:")
    for slug in SLUGS_ORDEM:
        gerar(slug)
    print(f"{len(SLUGS_ORDEM)} páginas geradas em src/especialidades/")
