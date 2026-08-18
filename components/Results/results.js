/* ==========================================================================
   Resultados — revelação progressiva dos casos extras.
   Depende de: components/Results/results.html. Carregar com defer.

   O comparador de cada caso NÃO é responsabilidade deste arquivo: quem move o
   divisor é o before-after.js, que percorre todos os [data-ba] da página.
   Aqui só existe o "ver mais".

   Contrato de enriquecimento, na mesma linha do carrossel: o HTML entregue
   traz os quatro casos VISÍVEIS e o botão com [hidden]. É este script que
   esconde os dois extras e revela o botão. Escrito ao contrário — marcação já
   com [hidden] — dois casos sumiriam de vez para quem não executa JavaScript,
   e o botão que os traria de volta também não funcionaria.
   ========================================================================== */

(function () {
  "use strict";

  var secao = document.querySelector("#resultados");
  if (!secao) return;

  var botao = secao.querySelector("[data-ver-mais]");
  var extras = secao.querySelectorAll("[data-caso-extra]");
  if (!botao || !extras.length) return;

  var lista = secao.querySelector(".resultados__lista");
  if (lista && !lista.id) lista.id = "resultados-lista";
  botao.setAttribute("aria-controls", lista ? lista.id : "");

  function definir(oculto) {
    Array.prototype.forEach.call(extras, function (item) {
      item.hidden = oculto;
    });
    botao.setAttribute("aria-expanded", oculto ? "false" : "true");
    botao.textContent = oculto ? "Ver os outros dois casos" : "Ver menos";
  }

  definir(true);
  botao.hidden = false;

  botao.addEventListener("click", function () {
    var vaiAbrir = botao.getAttribute("aria-expanded") === "false";
    definir(!vaiAbrir);

    /* Ao recolher, leva o foco de volta para o botão e a página para a altura
       dele. Sem isso, quem estava lendo o quarto caso é jogado para um ponto
       que não existe mais — a página encurta sob os pés e a posição de rolagem
       fica num lugar aleatório. */
    if (!vaiAbrir) {
      botao.scrollIntoView({
        block: "center",
        behavior: window.matchMedia &&
                  window.matchMedia("(prefers-reduced-motion: reduce)").matches
                    ? "auto" : "smooth"
      });
      botao.focus();
    }
  });
})();
