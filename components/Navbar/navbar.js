/* ==========================================================================
   Componente: Navbar — comportamento
   Sem dependências. Carregar com defer.

   Duas responsabilidades:
     1. estado "rolado" da barra;
     2. painel de menu em telas estreitas, acessível por teclado.
   ========================================================================== */

(function () {
  "use strict";

  var navbar = document.querySelector("[data-navbar]");
  if (!navbar) return;

  /* ------------------------------------------------------------------------
     1. Estado rolado
     Uma sentinela de 1px no topo do documento é observada pelo
     IntersectionObserver: quando ela sai do viewport, a página rolou. Isso
     evita um handler de scroll, que dispararia dezenas de vezes por segundo.
     ------------------------------------------------------------------------ */
  var sentinela = document.createElement("div");
  sentinela.setAttribute("aria-hidden", "true");
  sentinela.style.cssText = "position:absolute;top:80px;left:0;width:1px;height:1px;pointer-events:none";
  document.body.prepend(sentinela);

  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      navbar.classList.toggle("navbar--scrolled", !entries[0].isIntersecting);
    }).observe(sentinela);
  } else {
    // Sem suporte, a barra fica permanentemente no estado com fundo: legível
    // em qualquer posição da página, apenas sem a transição.
    navbar.classList.add("navbar--scrolled");
  }

  /* ------------------------------------------------------------------------
     2. Painel de menu
     ------------------------------------------------------------------------ */
  var toggle = navbar.querySelector("[data-navbar-toggle]");
  var menu = document.getElementById("navbar-menu");
  var rotulo = navbar.querySelector("[data-navbar-toggle-label]");
  if (!toggle || !menu) return;

  var FOCAVEIS = 'a[href], button:not(:disabled), input, select, textarea, [tabindex]:not([tabindex="-1"])';
  var aberto = false;

  // Referência única, compartilhada entre abrir() e fechar(), para a
  // animação em andamento no painel. Sem isso, um toque rápido demais no
  // botão (abrir→fechar→abrir antes dos 220ms terminarem) deixa duas
  // instâncias de menu.animate() competindo pelo mesmo elemento ao mesmo
  // tempo — cada uma com seu próprio finished/setTimeout mexendo em opacity
  // e na classList do navbar de forma fora de ordem. O sintoma real (visto
  // em dispositivo): o painel "abre" mas sem fundo aplicado direito,
  // deixando o conteúdo da página por trás aparecer através dele.
  var animAtual = null;

  // Abrir/fechar o painel via WAAPI, não via transição de display em CSS.
  // Testado nesta sessão (Fase 6): a combinação interpolate-size +
  // @starting-style + transition-behavior:allow-discrete para animar um
  // display:none<->flex ficou com a opacidade travada em 0 em dois testes
  // isolados neste motor — mesma classe de instabilidade encontrada ao tentar
  // animar o fechamento do FAQ só em CSS. WAAPI com keyframes explícitos é a
  // técnica que se confirmou funcionando nos dois casos.
  var reduzido = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var podeAnimar = !reduzido && "animate" in Element.prototype;
  var DURACAO_PAINEL = 220;
  var EASING_PAINEL = "cubic-bezier(0.16, 1, 0.3, 1)";

  // getClientRects() é o teste confiável de "está renderizado": offsetParent
  // retorna null para qualquer elemento position:fixed, o que daria falso
  // negativo se um focável do painel viesse a ser fixo.
  function focaveisDoMenu() {
    return Array.prototype.filter.call(
      menu.querySelectorAll(FOCAVEIS),
      function (el) { return el.getClientRects().length > 0; }
    );
  }

  function abrir() {
    if (aberto) return;
    aberto = true;

    // A classe entra ANTES da animação: é ela que faz display:flex via CSS
    // (regra já existente, responsiva). O WAAPI assume a partir daí — ele não
    // precisa da classe para saber que o elemento está com display não-none,
    // só para poder medir/animar opacity e transform de verdade.
    navbar.classList.add("navbar--open");
    toggle.setAttribute("aria-expanded", "true");
    if (rotulo) rotulo.textContent = "Fechar menu";
    document.body.style.overflow = "hidden";

    if (podeAnimar) {
      // Cancela a animação de fechamento anterior, se ainda estiver em
      // andamento — ver comentário de animAtual, acima.
      if (animAtual) animAtual.cancel();

      var animAbertura = menu.animate(
        [
          { opacity: 0, transform: "translateY(-8px)" },
          { opacity: 1, transform: "translateY(0)" },
        ],
        { duration: DURACAO_PAINEL, easing: EASING_PAINEL }
      );
      animAtual = animAbertura;

      // Sem isto, se o timeline da animação nunca avançar (mesma condição
      // documentada em components/FAQ/faq.js), o painel ficaria com
      // opacity:0 congelada para sempre — visível no layout (display:flex),
      // mas invisível de verdade. cancel() devolve ao valor real do CSS.
      // cancel() em cima de uma animação já finalizada não tem efeito
      // colateral — não precisa de guard contra chamada dupla aqui.
      var jaCancelou = false;
      var cancelarAbertura = function () {
        if (jaCancelou) return;
        jaCancelou = true;
        if (animAtual === animAbertura) animAtual = null;
        animAbertura.cancel();
      };
      animAbertura.finished.then(cancelarAbertura).catch(cancelarAbertura);
      setTimeout(cancelarAbertura, DURACAO_PAINEL + 100);
    }

    var alvos = focaveisDoMenu();
    if (alvos.length) alvos[0].focus();
  }

  function fechar(devolverFoco) {
    if (!aberto) return;
    aberto = false;

    toggle.setAttribute("aria-expanded", "false");
    if (rotulo) rotulo.textContent = "Abrir menu";

    // O foco volta para o próprio botão, não para "o que estava focado antes":
    // o painel só pode ser aberto por este botão, então ele é sempre o ponto de
    // retorno correto. Guardar o activeElement anterior falharia quando o botão
    // é acionado sem receber foco (clique programático, e historicamente Safari).
    // Só devolve quando o fechamento partiu do teclado — devolver depois de um
    // clique em link roubaria o foco do destino navegado.
    if (devolverFoco) {
      toggle.focus();
    }

    // A classe (display:none) e o overflow só voltam ao normal DEPOIS da
    // animação terminar — removê-los antes cortaria o fade pela metade e
    // deixaria o fundo rolar por trás de um painel ainda visível.
    //
    // O "if (aberto) return" existe por causa de um clique rápido
    // fechar->abrir: se a pessoa reabrir o painel antes desta animação de
    // fechamento antiga terminar, `aberto` já voltou a `true` quando esta
    // callback disparar. Sem o guard, ela removeria a classe do painel
    // recém-reaberto e fecharia por engano o que deveria continuar aberto.
    var anim; // atribuída abaixo quando podeAnimar; fica undefined no fallback sem animação

    function finalizarFechamento() {
      if (aberto) return;
      // cancel() evita que o efeito da animação de fechar (congelado no
      // primeiro quadro se "finished" nunca resolver — mesmo caso do FAQ,
      // ver components/FAQ/faq.js) fique competindo com a próxima animação
      // de abrir, na próxima vez que o painel abrir.
      if (anim) anim.cancel();
      if (animAtual === anim) animAtual = null;
      navbar.classList.remove("navbar--open");
      document.body.style.overflow = "";
    }

    if (podeAnimar) {
      // Cancela a animação de abertura anterior, se ainda estiver em
      // andamento — ver comentário de animAtual, acima.
      if (animAtual) animAtual.cancel();

      anim = menu.animate(
        [
          { opacity: 1, transform: "translateY(0)" },
          { opacity: 0, transform: "translateY(-8px)" },
        ],
        { duration: DURACAO_PAINEL, easing: EASING_PAINEL }
      );
      animAtual = anim;
      anim.finished.then(finalizarFechamento).catch(finalizarFechamento);
      // Rede de segurança: mesmo raciocínio do FAQ (components/FAQ/faq.js) —
      // "finished" pode nunca resolver em certas condições reais (aba em
      // segundo plano, entre outras do próprio spec). finalizarFechamento já
      // é seguro para rodar duas vezes, graças ao "if (aberto) return".
      setTimeout(finalizarFechamento, DURACAO_PAINEL + 100);
    } else {
      finalizarFechamento();
    }
  }

  toggle.addEventListener("click", function () {
    if (aberto) fechar(true); else abrir();
  });

  // Esc fecha — User Control and Freedom: toda entrada em um estado precisa de
  // uma saída óbvia e barata.
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && aberto) {
      e.preventDefault();
      fechar(true);
    }
  });

  // Armadilha de foco: com o painel aberto, Tab circula dentro dele. Sem isso,
  // o foco escaparia para o conteúdo atrás, que está visualmente oculto.
  menu.addEventListener("keydown", function (e) {
    if (e.key !== "Tab" || !aberto) return;

    var alvos = focaveisDoMenu();
    if (!alvos.length) return;

    var primeiro = alvos[0];
    var ultimo = alvos[alvos.length - 1];

    if (e.shiftKey && document.activeElement === primeiro) {
      e.preventDefault();
      ultimo.focus();
    } else if (!e.shiftKey && document.activeElement === ultimo) {
      e.preventDefault();
      primeiro.focus();
    }
  });

  // Navegar para uma âncora fecha o painel.
  menu.addEventListener("click", function (e) {
    if (e.target.closest("a[href]") && aberto) fechar(false);
  });

  // Ao alargar a janela, o painel deixa de existir como painel: o estado
  // precisa ser desfeito, senão o overflow do body ficaria travado.
  if ("matchMedia" in window) {
    var largo = window.matchMedia("(min-width: 48.0625rem)");
    var aoMudar = function (e) { if (e.matches) fechar(false); };

    if (largo.addEventListener) largo.addEventListener("change", aoMudar);
    else if (largo.addListener) largo.addListener(aoMudar);
  }
})();
