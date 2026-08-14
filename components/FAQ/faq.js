/* ==========================================================================
   FAQ — animação de abrir/fechar via Web Animations API.
   Sem dependências. Carregar com defer.

   Por que JS e não só CSS: a Fase 4 previu animar via interpolate-size
   (CSS puro), e a abertura de fato anima assim de forma confiável — testado
   e confirmado via getAnimations() nesta sessão. O fechamento não: medido
   três vezes, a altura parava no meio do caminho e nunca chegava a 0 (com
   div manual) ou não se movia (mirando ::details-content diretamente,
   embora o seletor seja aceito pelo parser). Não confiar em técnica que não
   se consegue confirmar funcionando — por isso a versão que ficou é esta,
   com WAAPI e alturas em pixel explícitas, verificável via anim.finished.

   Progressive enhancement de verdade: com JS desligado, name="faq" no HTML
   ainda garante abertura exclusiva nativa, só sem animação — nada quebra.
   -------------------------------------------------------------------------- */

(function () {
  "use strict";

  var reduzido = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (reduzido || !("animate" in Element.prototype)) return; // nativo cuida sozinho, sem animação

  var DURACAO = 300;
  var EASING = "cubic-bezier(0.16, 1, 0.3, 1)";

  // anim.finished é o sinal correto, mas não é o único que este código confia
  // nele: testado nesta sessão que o timeline de uma animação WAAPI pode não
  // avançar em certas condições (headless com tempo virtual, aba em segundo
  // plano são cenários documentados do próprio spec) — se isso acontecer de
  // verdade, "finished" nunca resolve e o item fica preso animando para
  // sempre. runOnce() garante que a limpeza roda de um jeito ou de outro.
  function runOnce(fn) {
    var executado = false;
    return function () {
      if (executado) return;
      executado = true;
      fn();
    };
  }

  // Estado de "animação em andamento" por ITEM, não por closure de clique —
  // uma versão anterior guardava isso dentro do listener de cada summary, o
  // que misturava o estado de um item com o de outro sempre que um fechava
  // o vizinho por exclusividade. Um WeakMap associa o estado ao elemento
  // certo não importa quem disparou a animação.
  var animando = new WeakMap();

  function abrir(item, conteudo) {
    animando.set(item, true);
    item.open = true;
    var alvo = conteudo.scrollHeight;
    var anim = conteudo.animate(
      [{ height: "0px", opacity: 0 }, { height: alvo + "px", opacity: 1 }],
      { duration: DURACAO, easing: EASING }
    );

    var finalizar = runOnce(function () {
      // cancel() remove o efeito da animação — sem isto, se "finished" nunca
      // resolver, o último quadro aplicado (height quase 0) continuaria
      // valendo para sempre por cima do CSS real, mesmo com item.open=true.
      anim.cancel();
      conteudo.style.height = "";
      animando.set(item, false);
    });
    anim.finished.then(finalizar).catch(finalizar);
    setTimeout(finalizar, DURACAO + 100); // rede de segurança — ver nota acima de runOnce
  }

  function fechar(item, conteudo) {
    animando.set(item, true);
    var atual = conteudo.getBoundingClientRect().height;
    var anim = conteudo.animate(
      [{ height: atual + "px", opacity: 1 }, { height: "0px", opacity: 0 }],
      { duration: DURACAO, easing: EASING }
    );

    var finalizar = runOnce(function () {
      anim.cancel();
      item.open = false;
      conteudo.style.height = "";
      animando.set(item, false);
    });
    anim.finished.then(finalizar).catch(finalizar);
    setTimeout(finalizar, DURACAO + 100);
  }

  Array.prototype.forEach.call(document.querySelectorAll(".faq__list"), function (lista) {
    var itens = Array.prototype.slice.call(lista.querySelectorAll(".faq__item"));

    // A partir daqui o JS é o único responsável pela exclusividade — remove
    // o "name" para que o navegador não feche um item por conta própria
    // (sem transição) ao mesmo tempo que nosso código anima outro.
    itens.forEach(function (item) { item.removeAttribute("name"); });

    itens.forEach(function (item) {
      var summary = item.querySelector(".faq__q");
      var conteudo = item.querySelector(".faq__a");
      if (!summary || !conteudo) return;

      summary.addEventListener("click", function (e) {
        e.preventDefault();
        if (animando.get(item)) return;

        if (item.open) {
          fechar(item, conteudo);
        } else {
          itens.forEach(function (outro) {
            if (outro !== item && outro.open && !animando.get(outro)) {
              fechar(outro, outro.querySelector(".faq__a"));
            }
          });
          abrir(item, conteudo);
        }
      });
    });
  });
})();
