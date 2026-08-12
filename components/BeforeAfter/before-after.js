/* ==========================================================================
   Antes e Depois — sincroniza a posição do recorte com o input nativo.
   Sem dependências. Carregar com defer.

   Todo o comportamento de arraste, teclado e toque vem do próprio
   <input type="range">; este script só transporta o valor para o CSS.
   ========================================================================== */

(function () {
  "use strict";

  var palcos = document.querySelectorAll("[data-ba]");

  Array.prototype.forEach.call(palcos, function (palco) {
    var range = palco.querySelector("[data-ba-range]");
    if (!range) return;

    function aplicar() {
      palco.style.setProperty("--pos", range.value + "%");
    }

    range.addEventListener("input", aplicar);
    aplicar();   // respeita o valor inicial da marcação, inclusive se restaurado pelo navegador
  });
})();
