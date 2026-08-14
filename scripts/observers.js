/* ==========================================================================
   Reveal de scroll — motor compartilhado por todas as seções.
   Depende de: nada (vanilla). Carregar com defer, em toda página com .reveal.

   Convenção de marcação, sem configuração por atributo:
     - <elemento class="reveal">           -> observado individualmente.
     - <container data-reveal-group>
         <filho class="reveal">…</filho>   -> o GRUPO é observado uma vez só;
         <filho class="reveal">…</filho>      ao entrar, todos os filhos
       </container>                           revelam juntos, com atraso
                                               escalonado entre eles (o efeito
                                               de stagger vem do delay, não de
                                               cada filho disparar sozinho).

   Por que este arquivo mora em scripts/ e não em components/<algo>/: reveal de
   scroll não pertence a um componente — a Home usa em nove seções diferentes.
   É exatamente o caso que a Seção 13 do Project Bible reservou para scripts/
   compartilhado, ao contrário de Navbar/BeforeAfter/ContactForm, que são
   comportamento de um componente só e por isso moram na própria pasta.
   ========================================================================== */

(function () {
  "use strict";

  var CAP_STAGGER = 6; // Seção 6 do Bible: "máx. 6 itens visíveis por vez"

  var reduzido = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Sem IntersectionObserver ou com movimento reduzido: mostra tudo de uma
  // vez, sem tentar animar. Degradação silenciosa, nunca conteúdo escondido.
  if (reduzido || !("IntersectionObserver" in window)) {
    Array.prototype.forEach.call(document.querySelectorAll(".reveal"), function (el) {
      el.classList.add("is-visible");
    });
    return;
  }

  // Aplica o atraso escalonado nos descendentes .reveal de cada grupo ANTES
  // de observar — o delay é propriedade do elemento, independente de quando
  // ele revela. Não há grupos aninhados neste projeto, então descendentes
  // (não só filhos diretos) é a busca certa e mais simples.
  Array.prototype.forEach.call(document.querySelectorAll("[data-reveal-group]"), function (grupo) {
    var filhos = grupo.querySelectorAll(".reveal");
    Array.prototype.forEach.call(filhos, function (filho, indice) {
      var passo = Math.min(indice, CAP_STAGGER - 1);
      filho.style.setProperty("--reveal-delay", "calc(" + passo + " * var(--stagger-step))");
    });
  });

  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;

        var alvo = entry.target;
        if (alvo.hasAttribute("data-reveal-group")) {
          Array.prototype.forEach.call(alvo.querySelectorAll(".reveal"), function (filho) {
            filho.classList.add("is-visible");
          });
        } else {
          alvo.classList.add("is-visible");
        }

        observer.unobserve(alvo); // uma vez só — não repete ao rolar para cima e para baixo
      });
    },
    { threshold: 0.2 }
  );

  var grupos = document.querySelectorAll("[data-reveal-group]");
  Array.prototype.forEach.call(grupos, function (grupo) { observer.observe(grupo); });

  // .reveal fora de qualquer grupo é observado individualmente. Filtro em JS
  // puro, não por seletor CSS composto — mais simples de garantir correto do
  // que depender de :not() com seletor complexo em qualquer navegador.
  Array.prototype.forEach.call(document.querySelectorAll(".reveal"), function (el) {
    if (!el.closest("[data-reveal-group]")) observer.observe(el);
  });
})();
