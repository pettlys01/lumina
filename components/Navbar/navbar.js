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

    navbar.classList.add("navbar--open");
    toggle.setAttribute("aria-expanded", "true");
    if (rotulo) rotulo.textContent = "Fechar menu";

    // Impede a página de rolar por trás do painel.
    document.body.style.overflow = "hidden";

    var alvos = focaveisDoMenu();
    if (alvos.length) alvos[0].focus();
  }

  function fechar(devolverFoco) {
    if (!aberto) return;
    aberto = false;

    navbar.classList.remove("navbar--open");
    toggle.setAttribute("aria-expanded", "false");
    if (rotulo) rotulo.textContent = "Abrir menu";

    document.body.style.overflow = "";

    // O foco volta para o próprio botão, não para "o que estava focado antes":
    // o painel só pode ser aberto por este botão, então ele é sempre o ponto de
    // retorno correto. Guardar o activeElement anterior falharia quando o botão
    // é acionado sem receber foco (clique programático, e historicamente Safari).
    // Só devolve quando o fechamento partiu do teclado — devolver depois de um
    // clique em link roubaria o foco do destino navegado.
    if (devolverFoco) {
      toggle.focus();
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
