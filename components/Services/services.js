/* ==========================================================================
   Especialidades — prévia expansível
   Depende de: components/Services/services.html (o <dialog> vive lá).

   O QUE ESTE ARQUIVO FAZ
   Intercepta o clique no card e abre uma prévia da especialidade num <dialog>
   nativo, animando o card até o formato do diálogo (técnica FLIP).

   POR QUE ELE É UM ENRIQUECIMENTO, E NÃO A FUNÇÃO PRINCIPAL
   Cada card já era — e continua sendo — um <a> para a página completa da
   especialidade. Se este script não carregar, falhar, ou o navegador não
   suportar <dialog>, o clique navega para a página, que é o comportamento que
   o site tem hoje. Nada fica inalcançável. Trocar o link por um botão teria
   órfãs as cinco páginas construídas na Fase 5 — foi a primeira coisa
   verificada antes de escrever qualquer linha aqui.

   POR QUE <dialog> NATIVO
   showModal() entrega travamento de foco, tecla Esc, ::backdrop e renderização
   na top layer (sem disputa de z-index). Uma implementação manual teria que
   refazer tudo isso — e a armadilha conhecida é o travamento de foco, que
   costuma ser escrito com querySelectorAll fixo e quebra assim que o conteúdo
   do diálogo muda. Mesmo motivo pelo qual o FAQ usa <details> nativo.
   ========================================================================== */

(function () {
  "use strict";

  var secao = document.querySelector("#especialidades");
  if (!secao) return;

  var dlg = secao.querySelector(".esp-dialog");
  var cards = secao.querySelectorAll(".card--expansivel");
  if (!dlg || !cards.length) return;

  // Sem <dialog> nativo não há enriquecimento: os links seguem navegando.
  if (typeof dlg.showModal !== "function") return;

  var inner = dlg.querySelector(".esp-dialog__inner");
  var elTitulo = dlg.querySelector(".esp-dialog__titulo");
  var elTexto = dlg.querySelector(".esp-dialog__texto");
  var elCta = dlg.querySelector(".esp-dialog__cta");
  var elMedia = dlg.querySelector(".esp-dialog__media");
  var elImg = elMedia ? elMedia.querySelector("img") : null;
  var btnFechar = dlg.querySelector(".esp-dialog__fechar");

  var DURACAO = 420;
  var EASE = "cubic-bezier(0.16, 1, 0.3, 1)";

  var cardAtual = null;

  /* Animações em voo, para poderem ser interrompidas.

     A primeira versão usava uma trava booleana ("animando") que fazia abrir() e
     fechar() saírem cedo enquanto houvesse animação rodando. O verificador
     pegou o defeito: clicar em fechar antes de a abertura terminar não fazia
     nada. Não era artefato de teste — 420ms é tempo de sobra para alguém abrir
     um card sem querer e já clicar no X, e nesse intervalo o diálogo ficava
     inerte. Trava que ignora a intenção do usuário é pior que animação
     interrompida. */
  var emVoo = [];

  /* Geração: cada abertura/fechamento invalida os callbacks pendentes do
     anterior. Sem isto, a rede de segurança de um fechamento interrompido
     dispararia depois e fecharia um diálogo que o usuário acabou de reabrir. */
  var geracao = 0;

  function movimentoReduzido() {
    return window.matchMedia &&
           window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  /* Padrão obrigatório da Seção 12.3 do Bible. fill:"backwards"/"both" prende o
     elemento no primeiro quadro se o timeline nunca avançar (aba em segundo
     plano é o caso documentado no spec) — e um diálogo preso no primeiro quadro
     fica invisível ou impossível de fechar. cancel() devolve o elemento ao CSS
     de verdade, que é sempre o estado utilizável.

     Aqui a rede de segurança é mais crítica que nos outros componentes: se a
     animação de FECHAMENTO nunca concluir, o close() nunca é chamado e o
     diálogo fica aberto para sempre. Por isso o finalizar() recebe o efeito
     colateral, e não só o cancel(). */
  function garantirConclusao(anim, duracaoTotal, aoFinalizar) {
    var concluido = false;
    function finalizar() {
      if (concluido) return;
      concluido = true;
      try { anim.cancel(); } catch (e) { /* já cancelada */ }
      if (aoFinalizar) aoFinalizar();
    }
    anim.finished.then(finalizar).catch(finalizar);
    setTimeout(finalizar, duracaoTotal + 150);
  }

  function preencher(card) {
    elTitulo.textContent = card.getAttribute("data-titulo") || "";

    elTexto.textContent = "";
    var molde = card.querySelector(".card__detalhe");
    if (molde) elTexto.appendChild(molde.content.cloneNode(true));

    var link = card.querySelector(".card__link");
    elCta.setAttribute("href", link ? link.getAttribute("href") : "#");

    /* Imagem é opcional: o card só a exibe se declarar data-img. Enquanto não
       houver fotografia própria por especialidade, o diálogo roda sem mídia em
       vez de reaproveitar uma foto de outra seção — repetir a mesma imagem em
       contextos diferentes é mais denunciador que não ter imagem. */
    var img = card.getAttribute("data-img");
    if (img && elImg) {
      elImg.setAttribute("src", img);
      elImg.setAttribute("alt", card.getAttribute("data-img-alt") || "");
      elMedia.hidden = false;
    } else if (elMedia) {
      elMedia.hidden = true;
      if (elImg) elImg.removeAttribute("src");
    }
  }

  /* FLIP: mede o card (First), abre o diálogo já no tamanho final (Last),
     aplica a transformação que leva o final de volta ao inicial (Invert) e
     anima até a identidade (Play).

     O inner recebe a escala INVERSA. Sem isso, escalar a caixa escalaria o
     texto junto e o efeito viraria um zoom — o conteúdo pareceria "esticar"
     durante a transição em vez de o quadro crescer ao redor dele. */
  function geometria() {
    var c = cardAtual.getBoundingClientRect();
    var d = dlg.getBoundingClientRect();
    return {
      dx: c.left - d.left,
      dy: c.top - d.top,
      sx: d.width  ? c.width  / d.width  : 1,
      sy: d.height ? c.height / d.height : 1
    };
  }

  /* Interrompe o que estiver em voo e devolve os elementos ao estado do CSS.
     Antes de cancelar, guarda como cada um estava NAQUELE instante, para que a
     próxima animação continue de onde esta parou em vez de saltar. */
  function pararEmVoo() {
    var estado = {
      caixa: getComputedStyle(dlg).transform,
      caixaOp: getComputedStyle(dlg).opacity,
      inner: getComputedStyle(inner).transform,
      innerOp: getComputedStyle(inner).opacity
    };
    emVoo.forEach(function (a) { try { a.cancel(); } catch (e) { /* já fim */ } });
    emVoo = [];
    return estado;
  }

  function abrir(card) {
    if (dlg.open) return;

    geracao++;
    var minha = geracao;

    cardAtual = card;
    preencher(card);

    dlg.showModal();
    document.body.classList.add("tem-dialog-aberto");

    if (movimentoReduzido()) return;

    pararEmVoo();
    var g = geometria();

    var aCaixa = dlg.animate(
      [
        { transform: "translate(" + g.dx + "px," + g.dy + "px) scale(" + g.sx + "," + g.sy + ")",
          opacity: 0.5 },
        { transform: "none", opacity: 1 }
      ],
      { duration: DURACAO, easing: EASE }
    );

    var aInner = inner.animate(
      [
        { transform: "scale(" + (1 / g.sx) + "," + (1 / g.sy) + ")", opacity: 0 },
        { transform: "none", opacity: 1 }
      ],
      { duration: DURACAO, easing: EASE }
    );

    emVoo = [aCaixa, aInner];
    garantirConclusao(aCaixa, DURACAO, function () {
      if (minha === geracao) emVoo = [];
    });
    garantirConclusao(aInner, DURACAO);
  }

  function fechar() {
    if (!dlg.open) return;

    geracao++;
    var minha = geracao;

    function encerrar() {
      // Callback de uma geração anterior: o usuário já reabriu. Fechar agora
      // derrubaria o diálogo novo.
      if (minha !== geracao) return;
      emVoo = [];
      document.body.classList.remove("tem-dialog-aberto");
      if (dlg.open) dlg.close();
      // Devolve o foco ao card de origem: sem isto o foco volta para o <body>
      // e quem navega por teclado perde a posição na página.
      if (cardAtual) {
        var link = cardAtual.querySelector(".card__link");
        if (link) link.focus();
      }
    }

    if (movimentoReduzido() || !cardAtual) {
      encerrar();
      return;
    }

    // Continua de onde a abertura estava, se ela ainda estiver correndo.
    var de = pararEmVoo();
    var g = geometria();

    var aCaixa = dlg.animate(
      [
        { transform: de.caixa === "none" ? "none" : de.caixa, opacity: de.caixaOp },
        { transform: "translate(" + g.dx + "px," + g.dy + "px) scale(" + g.sx + "," + g.sy + ")",
          opacity: 0.5 }
      ],
      { duration: DURACAO, easing: EASE }
    );

    var aInner = inner.animate(
      [
        { transform: de.inner === "none" ? "none" : de.inner, opacity: de.innerOp },
        { transform: "scale(" + (1 / g.sx) + "," + (1 / g.sy) + ")", opacity: 0 }
      ],
      { duration: DURACAO, easing: EASE }
    );

    emVoo = [aCaixa, aInner];
    garantirConclusao(aCaixa, DURACAO, encerrar);
  }

  // ---- Ligações -----------------------------------------------------------

  Array.prototype.forEach.call(cards, function (card) {
    var link = card.querySelector(".card__link");
    if (!link) return;

    // Só agora o link promete abrir um diálogo. Anunciar isso no HTML estático
    // seria mentira quando o script não roda.
    link.setAttribute("aria-haspopup", "dialog");

    link.addEventListener("click", function (ev) {
      // Ctrl/Cmd/meio = intenção explícita de abrir em nova aba. Sequestrar
      // esse clique é uma das formas mais irritantes de quebrar um link.
      if (ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.button !== 0) return;
      ev.preventDefault();
      abrir(card);
    });
  });

  btnFechar.addEventListener("click", fechar);

  // Esc dispara "cancel" e fecharia o diálogo na hora, pulando a animação de
  // saída. Interceptar e delegar ao fechar() mantém um caminho de saída só.
  dlg.addEventListener("cancel", function (ev) {
    ev.preventDefault();
    fechar();
  });

  // Clique no fundo. O alvo é o próprio <dialog> apenas quando o clique cai
  // fora do .esp-dialog__inner, que ocupa toda a área visível da caixa.
  dlg.addEventListener("click", function (ev) {
    if (ev.target === dlg) fechar();
  });
})();
