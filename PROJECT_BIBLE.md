# Project Bible — Lumina Odontologia

**Versão:** 1.0
**Data:** 2026-08-12
**Status:** Fase 0 (documento fundacional) — nenhum código ainda escrito
**Projeto fictício** — clínica odontológica premium, usado como estudo de caso de arquitetura/UX/front-end de alto padrão.

Este documento é a constituição do projeto. Nenhuma decisão de design, código ou conteúdo deve
contradizer o que está aqui sem que este documento seja atualizado primeiro. Se um agente (humano ou
Claude Code) encontrar uma decisão de implementação não coberta por este documento, a decisão deve ser
tomada com base nos princípios das seções 1–3, registrada de volta aqui, e só então implementada.

---

## 1. Visão da marca

**Frase-guia:** "Não vendemos tratamento odontológico. Vendemos confiança para sorrir."

Lumina não compete em preço nem em volume. Compete em percepção de segurança, tecnologia e cuidado
humano — o tipo de clínica em que o paciente decide confiar antes mesmo de entender o procedimento.
O site é o primeiro contato físico-digital com essa confiança: se ele parecer um template comprado, a
promessa da marca já quebrou antes da primeira consulta.

**Atributos obrigatórios em toda tela, todo componente, todo texto:**

| Atributo | O que significa na prática |
|---|---|
| Sofisticação | Menos elementos, mais qualidade por elemento. Nunca decoração gratuita. |
| Calma | Ritmo visual lento — espaço negativo generoso, transições suaves, sem elementos piscando ou competindo por atenção. |
| Limpeza | Grid rigoroso, alinhamento perfeito, zero desalinhamento "quase certo". |
| Tecnologia | Mostrada, não declarada — imagens reais de equipamentos, não ícones genéricos de "high-tech". |
| Atendimento humano | Rostos reais (da equipe fictícia), linguagem em primeira pessoa, sem jargão de call center. |
| Alto padrão | Cada escolha (tipografia, cor, espaçamento) deve parecer cara mesmo sendo simples. |

**Teste de aceitação da marca (aplicar a cada seção antes de considerá-la pronta):**
Se alguém disser "bonito", a seção falhou. O padrão é alguém dizer **"essa clínica parece cara"**.

**Referências de inspiração** (usar como calibração de sofisticação, nunca copiar layout):
Apple (clareza, uso de espaço, motion contido), Aesop (materialidade, tipografia editorial, paleta
neutra), minimalismo escandinavo (função sem ruído), clínicas suíças (precisão, confiança clínica sem
frieza), arquitetura contemporânea (luz, proporção, hierarquia por escala e não por cor).

**Proibido:** azul médico tradicional, ícones de estoque genéricos, gradientes chamativos, pop-ups
agressivos, contadores de urgência artificial ("só hoje!"), qualquer elemento que pareça geração
automática de site.

---

## 2. Persona e público-alvo

**Perfil demográfico:** Classe A/B, 25–60 anos, decisores financeiros do próprio tratamento (não
dependem de convênio popular; valorizam tempo e resultado sobre preço).

**Duas personas principais:**

1. **A Investidora em Si Mesma (30–45 anos)** — busca lentes de contato dental, clareamento,
   harmonização facial. Motivada por autoestima e presença profissional/social. Pesquisa muito antes de
   agendar; compara clínicas pelo Instagram e pelo site antes de ligar. Decide por confiança visual
   primeiro, preço depois.
2. **O Pragmático de Longo Prazo (40–60 anos)** — busca implantes, ortodontia estética, tratamentos
   restauradores maiores. Motivado por função e durabilidade, mas ainda sensível a status ("não quero
   parecer que fiz tratamento de bairro"). Decide por evidência técnica (equipamento, credenciais,
   processo claro) mais do que por estética do site — mas abandona se o site parecer amador.

**Jornada em ambas as personas:** rede social ou indicação → site (validação de confiança) → WhatsApp
ou formulário de agendamento → avaliação presencial. O site precisa vencer a etapa de validação de
confiança sozinho, sem intervenção humana.

**Procedimentos em destaque (ordem de prioridade de negócio):** Implantes → Lentes de contato dental →
Harmonização facial → Ortodontia estética → Clareamento.

---

## 3. Posicionamento

Lumina não se posiciona como "a clínica mais barata" nem "a mais tecnológica" isoladamente — ambos os
discursos já estão saturados no mercado odontológico. O posicionamento é **confiança por transparência
de processo**: o paciente vê exatamente o que vai acontecer (consulta → planejamento → tratamento →
acompanhamento) antes de agendar, e vê a tecnologia e a equipe por trás de cada etapa. Isso reduz a
principal objeção do público-alvo — medo do desconhecido e medo de resultado estético ruim — sem
recorrer a promessas exageradas ou gatilhos de urgência.

**Concorrência indireta a evitar imitar:** clínicas populares (excesso de promoção, azul genérico),
clínicas "de luxo" que investem só em interior físico e negligenciam o digital (site desatualizado
apesar da clínica ser cara — Lumina não pode cair nesse padrão).

---

## 4. Sistema de design

### 4.1 Cores

```css
:root {
  --color-primary: #F7F6F3;   /* fundo principal — quase branco, quente */
  --color-text: #202020;      /* texto principal */
  --color-gray: #666666;      /* texto secundário, legendas, metadados */
  --color-accent: #B58C5A;    /* dourado acinzentado — CTAs, detalhes, hover, linha decorativa */
  --color-success: #688B6A;   /* confirmações, estados positivos (ex: "consulta confirmada") */
  --color-white: #FFFFFF;     /* superfícies elevadas sobre o primary (cards, modais) */
}
```

Regras de uso:
- `--color-accent` é usado com moderação — CTA principal, sublinhados decorativos, ícones ativos,
  indicadores de progresso. Nunca como cor de fundo de seção inteira.
- Nunca usar azul em nenhum contexto médico (nem em ícones de "check", nem em links).
- Contraste mínimo AA: `--color-text` sobre `--color-primary` = 15.5:1 (passa). `--color-gray` sobre
  `--color-primary` = 4.6:1 (passa AA para texto normal, verificar em texto pequeno). `--color-accent`
  sobre `--color-primary` = 2.9:1 — **não usar accent como cor de texto de corpo**, apenas para
  elementos gráficos, ícones grandes (≥3:1 exigido) ou texto grande (≥24px / bold ≥19px).

### 4.2 Tipografia

- **Headings:** Instrument Serif (preferência) ou Cormorant Garamond como fallback de família —
  serifada editorial, nunca serif clássica "institucional". Peso único (400), tamanho e espaço negativo
  fazem a hierarquia, não peso.
- **Corpo/UI:** Inter ou Manrope — sans-serif neutra, alta legibilidade em tamanhos pequenos.

```css
:root {
  --font-heading: "Instrument Serif", "Cormorant Garamond", serif;
  --font-body: "Inter", "Manrope", -apple-system, sans-serif;

  /* Escala fluida via clamp() — nunca breakpoints fixos de font-size */
  --text-hero:    clamp(2.5rem, 4vw + 1rem, 5.5rem);
  --text-h1:      clamp(2rem, 2.5vw + 1rem, 3.5rem);
  --text-h2:      clamp(1.5rem, 1.5vw + 1rem, 2.5rem);
  --text-h3:      clamp(1.25rem, 1vw + 0.75rem, 1.75rem);
  --text-body-lg: clamp(1.125rem, 0.5vw + 1rem, 1.25rem);
  --text-body:    1rem;
  --text-small:   0.875rem;

  --leading-tight: 1.1;   /* headings */
  --leading-body:  1.6;   /* parágrafos */
  --tracking-heading: -0.01em;
}
```

### 4.3 Espaçamento

Escala em base 8, expressa como tokens fluidos para as seções (nunca padding fixo em desktop grande):

```css
:root {
  --space-1: 0.5rem;
  --space-2: 1rem;
  --space-3: 1.5rem;
  --space-4: 2rem;
  --space-6: 3rem;
  --space-8: 4rem;
  --space-12: 6rem;
  --space-section: clamp(4rem, 8vw, 10rem);   /* padding vertical entre seções */
  --space-container: clamp(1.5rem, 5vw, 6rem); /* padding lateral do container */
}
```

Regra: nenhuma seção deve ter menos de `--space-8` de respiro vertical. "Muito espaço" do brief é
literal — se em dúvida, aumentar o espaçamento, não diminuir.

### 4.4 Componentes (especificação mínima)

- **Botão primário:** fundo `--color-text`, texto `--color-primary`, sem sombra, hover = leve
  scale(1.02) + mudança de fundo para `--color-accent`, transição 300ms ease-out. Bordas nunca
  totalmente quadradas nem pill — `border-radius: 2px`, quase reto (referência Aesop/Apple).
- **Cards (especialidades, equipe):** fundo `--color-white` sobre `--color-primary`, sem borda visível,
  elevação apenas por sombra muito sutil (`box-shadow` com alpha ≤0.06), hover = leve elevação (translateY
  -4px) + sombra levemente mais forte. Ícones minimalistas em stroke fino (1.5px), cor `--color-text` ou
  `--color-accent`, nunca preenchidos/coloridos tipo emoji.
- **Slider antes/depois:** controle por arraste (mouse e touch), foco acessível, sem autoplay.
- **Accordion (FAQ):** um item aberto por vez opcional; ícone +/- que rotaciona 45°, altura animada via
  `grid-template-rows: 0fr → 1fr` (evita `height: auto` em transições).
- **Navbar:** transparente sobre o hero, ganha fundo `--color-primary` com leve blur ao scroll
  (>80px), transição 250ms.

---

## 5. Arquitetura das páginas

**Home (seções, em ordem):**
1. Hero — imagem grande, headline, CTA de agendamento, prova social pequena (ex: nota Google + nº de
   avaliações).
2. Sobre — quem é a clínica, valores, uma frase de posicionamento.
3. Especialidades — cards com hover, ícones minimalistas, link para detalhe (ancora ou página própria).
4. Antes e Depois — slider comparativo, 3–4 casos.
5. Tecnologia — scanner, raio-x, equipamentos, vídeo curto ou imagem em alta qualidade.
6. Depoimentos — vídeo + texto + link/selo de Google Reviews.
7. Processo — Consulta → Planejamento → Tratamento → Acompanhamento (stepper vertical/horizontal).
8. Equipe — fotos grandes, especializações, sem excesso de texto.
9. FAQ — accordion.
10. CTA final — "Agende sua avaliação".
11. Footer completo.

**Páginas internas previstas (Fase 5):** Especialidade (template reutilizável por procedimento),
Equipe (perfil individual, opcional), Sobre (expandida), Contato/Agendamento.

**Regra de navegação:** todo CTA leva ao mesmo destino de conversão (agendamento), nunca a becos sem
saída. Menos cliques até o formulário/WhatsApp é sempre melhor que mais páginas.

---

## 6. Especificação de animações (motion)

Referência de sensação: Apple — discreto, funcional, nunca decorativo por si só. Toda animação existe
para **guiar atenção ou comunicar estado**, nunca para "impressionar" isoladamente.

- **Padrões permitidos:** fade, mask reveal, slide (curto, ≤24px de deslocamento), scale (sutil, 0.98→1
  ou 1→1.02), blur-in (de 4–8px para 0), parallax discreto (≤15% de deslocamento relativo), stagger em
  listas/grids (delay 60–100ms por item, máx. 6 itens visíveis por vez).
- **Timing:** duração 300–600ms para elementos de entrada, 150–250ms para hover/estado. Easing
  `cubic-bezier(0.16, 1, 0.3, 1)` (ease-out expo suave) como padrão — nunca `linear`, nunca `ease` puro do
  browser.
- **Gatilho:** `IntersectionObserver` para reveals de scroll (threshold ~0.2, uma vez só — não repetir ao
  rolar para cima e para baixo). `ResizeObserver` para recalcular layouts que dependem de dimensão
  (ex: accordion, slider antes/depois).
- **View Transitions:** usar a API nativa quando suportada para navegação entre página Home → página de
  Especialidade, com fallback silencioso (sem quebra) em browsers sem suporte.
- **`prefers-reduced-motion`:** obrigatório. Quando ativo, todas as animações de entrada colapsam para
  fade simples ≤150ms ou aparecem instantaneamente; parallax e mask reveal são desativados por completo.
- **Proibido:** qualquer animação em loop infinito (exceto indicadores de carregamento), animação que
  atrase a leitura do conteúdo principal, bounce/elastic easing (não combina com a marca).

---

## 7. Regras de performance

**Metas Lighthouse (mobile, throttling padrão):** Performance ≥95, Accessibility 100, Best Practices
100, SEO 100.

Práticas obrigatórias:
- Imagens em `AVIF`/`WebP` com fallback, `loading="lazy"` em tudo fora do primeiro viewport,
  `fetchpriority="high"` na imagem do hero.
- Fontes: `font-display: swap`, subsetting se possível, no máximo 2 famílias × 2 pesos carregados.
- Sem frameworks de CSS (Bootstrap) nem jQuery — CSS puro com variables/tokens, JS vanilla modular.
- JS total inicial (antes de interação) deve ficar sob um orçamento explícito — alvo: <50KB
  comprimido para o bundle crítico da home.
- CLS: todo elemento com carregamento assíncrono (imagem, fonte, vídeo) reserva espaço via
  `aspect-ratio` ou dimensões explícitas antes de carregar.
- Vídeos de depoimento/tecnologia: nunca autoplay com som; poster estático leve; carregamento sob
  demanda (clique ou `IntersectionObserver`).

---

## 8. SEO

- Meta tags completas por página (title único ≤60 caracteres, description ≤155 caracteres, canonical).
- Open Graph completo (title, description, image 1200×630, type).
- JSON-LD obrigatório: `LocalBusiness` + `Dentist` na home (endereço fictício, horário, telefone,
  geolocalização), `BreadcrumbList` nas páginas internas, `FAQPage` na seção de FAQ se os itens forem
  estáticos no HTML (não gerar conteúdo só para o schema — o schema reflete o que está visível).
- Hierarquia de headings estritamente semântica: um único `<h1>` por página (o headline do hero),
  `<h2>` por seção principal, `<h3>` dentro de cards/subseções. Nunca pular nível para efeito visual —
  usar CSS para ajustar tamanho, não a tag errada.
- HTML semântico: `<header>`, `<main>`, `<section>` com `aria-label` ou heading associado, `<article>`
  para itens repetíveis (card de especialidade, depoimento), `<footer>`.

---

## 9. Acessibilidade (WCAG AA)

- Todo elemento interativo tem estado de foco visível e distinto (não depender só de mudança de cor —
  usar outline/box-shadow com espessura mínima 2px).
- Navegação 100% por teclado: ordem de tab lógica, accordion e slider operáveis sem mouse, modais (se
  houver) com focus trap e fechamento por `Esc`.
- Todo ícone decorativo com `aria-hidden="true"`; todo ícone funcional (ex: botão de play) com `aria-label`
  descritivo.
- Imagens: `alt` descritivo em fotos de conteúdo (equipe, antes/depois, equipamentos); `alt=""` em
  imagens puramente decorativas.
- Vídeos de depoimento: legendas (`<track>`) obrigatórias.
- `prefers-reduced-motion` respeitado (ver seção 6).
- Contraste conferido por combinação real de tokens (ver seção 4.1), não por inspeção visual.

---

## 10. Checklist de qualidade (aplicar antes de considerar qualquer fase "pronta")

- [ ] Lighthouse mobile: Performance ≥95, demais categorias = 100.
- [ ] Nenhuma cor fora da paleta definida na seção 4.1 usada em qualquer componente.
- [ ] Nenhuma fonte fora de `--font-heading`/`--font-body` carregada.
- [ ] Toda seção nova passa no "teste de aceitação da marca" da seção 1.
- [ ] Toda seção nova revisada com a skill `web-design-guidelines` antes de ser dada como concluída.
- [ ] Navegação completa por teclado testada manualmente (não só por inspeção de código).
- [ ] `prefers-reduced-motion` testado de fato (não só implementado).
- [ ] Nenhum componente construído sem antes checar se já existe um equivalente reutilizável
      (evitar duplicação entre Hero/CTA/Cards).
- [ ] HTML validado semanticamente (um `<h1>` por página, landmarks corretos).
- [ ] Testado em pelo menos um viewport mobile real (não só DevTools) antes de marcar a fase como concluída.

---

## 11. Instruções para o Claude Code

**Forma de trabalhar — por fases, nunca tudo de uma vez.** Seguir estritamente a ordem abaixo (seção 12).
Não avançar para a fase seguinte sem que os critérios de aceite da fase atual estejam marcados como
cumpridos neste documento (atualizar a checklist da seção 12 ao final de cada fase).

**Uso da Base de Conhecimento como constituição de princípios:**
Antes de implementar qualquer decisão não trivial de UX ou arquitetura de front-end (não apenas visual —
também estrutura de informação, hierarquia, motion, performance), consultar a Base de Conhecimento em
`C:\Users\Lucas\Documents\knowledge-base\` (repositório próprio, separado deste). Buscar os conceitos
relevantes em `knowledge/concepts/` (ex: hierarquia visual, progressive disclosure, carga cognitiva,
consistência de design, performance, progressive enhancement, graceful degradation) e justificar a
decisão citando o princípio aplicado — não apenas "porque parece bom".

**Aviso importante sobre cobertura da Base:** conforme auditoria interna da própria Base (Sprint 17,
Bloco 73), os domínios **UI, Acessibilidade e Conversão/CRO ainda são "ilhas"** — têm baixa densidade de
conexão com o restante do grafo de conceitos. Isso significa que, para decisões específicas de interface
visual desta clínica, a Base pode ter menos cobertura direta do que em outros domínios (ex: segurança,
arquitetura web). Nesses casos, tratar os princípios gerais (hierarquia, carga cognitiva, consistência)
como aplicáveis por analogia, e não inventar justificativa onde a Base não tem base real — é preferível
dizer "decisão de design sem princípio formal correspondente na Base, decidida por [critério X]" do que
forçar uma citação que não existe.

**Skills a invocar durante o projeto:**
- `frontend-design` — antes de desenhar qualquer componente visual novo (Fases 2–4), para calibrar
  direção estética e evitar default genérico.
- `web-design-guidelines` — ao final de cada fase que produza UI navegável, como gate de qualidade
  (item já presente na checklist da seção 10).
- `run` — para efetivamente abrir o site no browser e conferir visualmente antes de reportar qualquer
  fase como concluída. Nunca declarar uma fase de UI pronta sem tê-la visto renderizada.

**O que não fazer:**
- Não introduzir frameworks (React, Bootstrap, jQuery) — o brief exige HTML/CSS/JS nativos.
- Não pular a etapa de wireframe/fluxo (Fase 1) direto para código visual.
- Não usar dados ou nomes reais de clínicas/pessoas — este é um projeto fictício explícito.
- Não adicionar seções, páginas ou funcionalidades além do escopo da seção 5 sem atualizar este
  documento primeiro.

---

## 12. Fases do projeto e critérios de aceite

- [x] **Fase 0 — Project Bible** (este documento). Aceite: documento revisado e aprovado pelo usuário.
- [ ] **Fase 1 — Arquitetura, UX, wireframe, fluxo.** Aceite: wireframes de baixa fidelidade de todas as
      seções da Home + fluxo de navegação (incluindo página de Especialidade) aprovados; nenhum pixel de
      design visual final ainda.
- [ ] **Fase 2 — Sistema de Design.** Aceite: `styles/tokens.css` e `styles/typography.css` implementados
      exatamente conforme seção 4; página de estilo isolada (style guide) renderizando cores, tipos,
      espaçamentos e estados de componente-base (botão, card) sem conteúdo real.
- [ ] **Fase 3 — Componentes.** Aceite: Hero, Botões, Cards, Navbar, Footer implementados isoladamente,
      responsivos, acessíveis por teclado, revisados com `web-design-guidelines`.
- [ ] **Fase 4 — Homepage.** Aceite: todas as 11 seções da seção 5 montadas com conteúdo fictício
      realista, responsivo mobile-first, sem motion ainda (motion é Fase 6).
- [ ] **Fase 5 — Páginas internas.** Aceite: template de Especialidade funcional e reutilizável, ligado à
      navegação da Home.
- [ ] **Fase 6 — Motion.** Aceite: animações da seção 6 aplicadas, `prefers-reduced-motion` testado,
      nenhuma regressão de performance introduzida (reconferir Lighthouse).
- [ ] **Fase 7 — SEO.** Aceite: itens da seção 8 implementados e validados (rich results test equivalente,
      heading outline correto).
- [ ] **Fase 8 — Performance.** Aceite: metas da seção 7 e checklist da seção 10 100% cumpridas.

---

## 13. Organização de arquivos (referência para Fase 2 em diante)

```
components/
    Hero/
    Services/
    Team/
    Testimonials/
    CTA/
    FAQ/
    Footer/
styles/
    tokens.css
    typography.css
    layout.css
    animations.css
scripts/
    animations.js
    observers.js
    forms.js
assets/
```

Modularidade real: cada componente em sua própria pasta com seu HTML/partial, CSS e (se precisar) JS
próprios; `styles/layout.css` e `styles/animations.css` contêm apenas o que é genuinamente compartilhado
entre componentes, não um catch-all.
