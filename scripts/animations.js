/* ==========================================================================
   Sequência de entrada do Hero — o único "momento orquestrado" do site.
   Depende de: nada (vanilla, Web Animations API). Carregar com defer.

   Fica em scripts/, não em components/Hero/, porque não é comportamento do
   componente Hero em si (que não muda), é orquestração de página — a mesma
   razão pela qual observers.js mora aqui e não em nenhum componente.

   Por que só um momento e não vários: a Seção 6 do Bible pede "referência de
   sensação: Apple... nunca decorativo por si só". Um só load orquestrado
   pesa mais que efeitos espalhados pela página — o resto do site usa o
   mesmo reveal simples e uniforme (scripts/observers.js). O Hero é onde a
   marca aposta a ficha, então é o único lugar com um tratamento a mais.
   ========================================================================== */

(function () {
  "use strict";

  var reduzido = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var hero = document.querySelector(".hero");
  if (!hero || reduzido) return; // sem Hero nesta página, ou motion desligado: nada a fazer

  var imagem = hero.querySelector(".hero__image");
  var itens = hero.querySelectorAll(".hero__panel > *");

  if (!("animate" in Element.prototype)) return; // sem WAAPI, o conteúdo já está visível por padrão — sem regressão

  // fill:"backwards" mantém o PRIMEIRO quadro (opacity 0 / clip total) até a
  // animação começar a valer — necessário para o delay do stagger não
  // mostrar um flash do conteúdo final antes da vez de cada item. O preço:
  // se o timeline da animação nunca avançar por qualquer motivo real (aba em
  // segundo plano é o caso documentado no próprio spec — mesma condição já
  // registrada em components/FAQ/faq.js e components/Navbar/navbar.js), o
  // elemento fica PRESO nesse primeiro quadro para sempre — invisível, não
  // só "sem animação". Confirmado visualmente nesta sessão: a imagem do Hero
  // ficou com clip-path travado em "totalmente oculta" numa renderização
  // real. cancel() depois da duração é o que evita isso — devolve ao valor
  // do CSS de verdade (sem clip-path, sem opacity/transform), que é sempre
  // "visível", independente de a animação ter progredido ou não.
  function garantirConclusao(anim, duracaoTotal) {
    var concluido = false;
    var finalizar = function () {
      if (concluido) return;
      concluido = true;
      anim.cancel();
    };
    anim.finished.then(finalizar).catch(finalizar);
    setTimeout(finalizar, duracaoTotal + 150);
  }

  // Painel de texto: cada item entra em sequência, ordem de leitura natural
  // (sobrelinha -> título -> lead -> ações -> prova social). O DOM já reflete
  // essa ordem, então o índice do NodeList é o próprio índice do stagger.
  itens.forEach(function (item, indice) {
    var atraso = indice * 80;
    var duracao = 500;
    var anim = item.animate(
      [
        { opacity: 0, transform: "translateY(14px)" },
        { opacity: 1, transform: "translateY(0)" },
      ],
      {
        duration: duracao,
        delay: atraso,
        easing: "cubic-bezier(0.16, 1, 0.3, 1)",
        fill: "backwards",
      }
    );
    garantirConclusao(anim, atraso + duracao);
  });

  // Imagem de fundo: revelação por máscara (clip-path), de baixo para cima —
  // o padrão "mask reveal" da Seção 6, reservado aqui porque é a única
  // imagem da página grande o suficiente para o efeito valer a pena.
  if (imagem) {
    var duracaoImagem = 700;
    var animImagem = imagem.animate(
      [{ clipPath: "inset(0 0 100% 0)" }, { clipPath: "inset(0 0 0% 0)" }],
      { duration: duracaoImagem, easing: "cubic-bezier(0.16, 1, 0.3, 1)", fill: "backwards" }
    );
    garantirConclusao(animImagem, duracaoImagem);
  }
})();
