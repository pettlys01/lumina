/* ==========================================================================
   Carrossel de especialidades
   Depende de: components/Services/services.html

   O QUE ESTE ARQUIVO NÃO FAZ
   Não move os slides. Quem faz isso é a rolagem nativa com scroll-snap, no
   CSS — que já funciona com dedo, trackpad, roda e teclado antes de qualquer
   JavaScript. Este script só acrescenta setas e pontos, e sincroniza o estado
   deles com a posição real da rolagem.

   A consequência prática dessa divisão: se este arquivo falhar, o carrossel
   continua utilizável. Por isso os controles nascem com [hidden] no HTML e só
   aparecem aqui — botão visível que não responde é pior que botão ausente.

   POR QUE NÃO scrollIntoView NOS SLIDES
   scrollIntoView opera no elemento e, quando o alvo está dentro de um
   contêiner rolável que por sua vez está dentro da página, o navegador rola
   OS DOIS: o carrossel anda de lado e a página inteira salta na vertical
   junto. Usar scrollTo() no contêiner mantém o movimento onde ele deve estar.
   ========================================================================== */

(function () {
  "use strict";

  var raiz = document.querySelector("[data-carrossel]");
  if (!raiz) return;

  var trilho = raiz.querySelector(".carrossel__trilho");
  var slides = raiz.querySelectorAll(".carrossel__slide");
  var btnAnt = raiz.querySelector(".carrossel__seta--ant");
  var btnProx = raiz.querySelector(".carrossel__seta--prox");
  var caixaPontos = raiz.querySelector(".carrossel__pontos");
  if (!trilho || slides.length < 2) return;

  var atual = 0;

  function movimentoReduzido() {
    return window.matchMedia &&
           window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  /* A rolagem dispara dezenas de vezes por segundo; coalescer num quadro evita
     rodar sincronizar() muito mais do que a tela consegue mostrar. O segundo
     disparo, atrasado, existe para a rolagem SUAVE: ela continua depois do
     último evento de scroll, e sem esta remarcação o estado dos botões
     congelaria no valor de meio do caminho. */
  var agendado = false;
  var atrasado = null;
  function agendarSincronia() {
    // Sincroniza JÁ, antes de qualquer agendamento. Sem esta chamada imediata
    // havia um estado morto: quando a rolagem pedida coincide com a posição
    // atual (fim do carrossel, por exemplo), o navegador não dispara evento de
    // scroll — não houve mudança — e os botões ficavam congelados no valor
    // anterior. Foi assim que "próxima" continuava habilitada no último slide.
    sincronizar();

    if (!agendado) {
      agendado = true;
      requestAnimationFrame(function () {
        agendado = false;
        sincronizar();
      });
    }
    // A rolagem suave continua depois do último evento de scroll; esta
    // remarcação pega o estado final.
    clearTimeout(atrasado);
    atrasado = setTimeout(sincronizar, 260);
  }

  /* Centraliza o slide, medindo por getBoundingClientRect.

     A versão anterior usava offsetLeft e tinha dois defeitos somados. Primeiro,
     offsetLeft é medido a partir do offsetParent — que aqui é .carrossel (por
     ter position:relative), e não o trilho — enquanto scrollLeft vive no
     sistema de coordenadas do próprio trilho. Os dois só coincidem por
     acidente. Segundo, ela calculava alinhamento à ESQUERDA enquanto o CSS
     snapa ao CENTRO, então o navegador reposicionava logo depois.

     rect + scrollLeft atual não tem essa ambiguidade: mede-se a distância real
     entre o centro do slide e o centro do trilho, na tela. */
  function irPara(indice) {
    indice = Math.max(0, Math.min(slides.length - 1, indice));
    var rt = trilho.getBoundingClientRect();
    var rs = slides[indice].getBoundingClientRect();
    var delta = (rs.left + rs.width / 2) - (rt.left + rt.width / 2);
    trilho.scrollTo({
      left: trilho.scrollLeft + delta,
      behavior: movimentoReduzido() ? "auto" : "smooth"
    });
    // A rolagem suave termina depois; sem esta remarcação o estado dos botões
    // ficaria congelado no valor de antes do movimento.
    agendarSincronia();
  }

  /* Índice a partir da posição real da rolagem, e não de um contador próprio.
     Um contador interno sai de sincronia assim que o usuário arrasta com o
     dedo ou rola com o trackpad — o script acharia que está no slide 2 e a
     tela mostraria o 4. Ler a rolagem faz o arraste e os botões chegarem à
     mesma fonte de verdade. */
  function indiceVisivel() {
    var rt = trilho.getBoundingClientRect();
    var centro = rt.left + rt.width / 2;
    var melhor = 0;
    var menorDist = Infinity;
    for (var i = 0; i < slides.length; i++) {
      var r = slides[i].getBoundingClientRect();
      var d = Math.abs((r.left + r.width / 2) - centro);
      if (d < menorDist) { menorDist = d; melhor = i; }
    }
    return melhor;
  }

  function sincronizar() {
    atual = indiceVisivel();

    /* Estado dos botões vem do LIMITE DE ROLAGEM, não do índice.

       Pelo índice havia um caso morto real, medido: com snap ao centro, o
       primeiro e o último slide não conseguem centralizar — falta recuo. O
       último precisaria de scrollLeft 4032 e o máximo é 3962. Nesse ponto o
       índice fica ambíguo, o botão "anterior" continuava marcado como
       desabilitado no fim do carrossel e engolia o primeiro clique: a pessoa
       clicava para voltar e nada acontecia.

       O limite de rolagem não tem ambiguidade — ou ainda dá para rolar, ou
       não dá. A folga de 2px absorve o arredondamento subpixel que aparece
       com zoom do navegador ou tela de densidade fracionária. */
    var FOLGA = 2;
    var maximo = trilho.scrollWidth - trilho.clientWidth;
    btnAnt.disabled = trilho.scrollLeft <= FOLGA;
    btnProx.disabled = trilho.scrollLeft >= maximo - FOLGA;

    var pontos = caixaPontos.querySelectorAll(".carrossel__ponto");
    for (var i = 0; i < pontos.length; i++) {
      var ativo = i === atual;
      pontos[i].setAttribute("aria-selected", ativo ? "true" : "false");
      // Só o ponto ativo fica na ordem de tabulação: cinco paradas de teclado
      // para escolher entre cinco slides é ruído. Setas do teclado percorrem
      // os pontos, que é o padrão de um role="tablist".
      pontos[i].setAttribute("tabindex", ativo ? "0" : "-1");
    }
  }

  // ---- Pontos -------------------------------------------------------------

  for (var i = 0; i < slides.length; i++) {
    (function (indice) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "carrossel__ponto";
      b.setAttribute("role", "tab");
      b.setAttribute("aria-label", "Especialidade " + (indice + 1) +
                                   " de " + slides.length);
      b.addEventListener("click", function () { irPara(indice); });
      caixaPontos.appendChild(b);
    })(i);
  }

  caixaPontos.addEventListener("keydown", function (ev) {
    if (ev.key !== "ArrowRight" && ev.key !== "ArrowLeft") return;
    ev.preventDefault();
    var destino = atual + (ev.key === "ArrowRight" ? 1 : -1);
    if (destino < 0 || destino >= slides.length) return;
    irPara(destino);
    // Leva o foco junto: sem isto a seta seguinte do teclado partiria de um
    // ponto que não é mais o selecionado.
    setTimeout(function () {
      var p = caixaPontos.querySelectorAll(".carrossel__ponto")[destino];
      if (p) p.focus();
    }, movimentoReduzido() ? 0 : 320);
  });

  // ---- Setas --------------------------------------------------------------

  btnAnt.addEventListener("click", function () { irPara(indiceVisivel() - 1); });
  btnProx.addEventListener("click", function () { irPara(indiceVisivel() + 1); });

  // ---- Sincronia ----------------------------------------------------------

  trilho.addEventListener("scroll", agendarSincronia, { passive: true });

  // Largura do slide muda com o viewport; o índice precisa ser remedido.
  window.addEventListener("resize", sincronizar);

  // Só agora os controles existem de fato.
  btnAnt.hidden = false;
  btnProx.hidden = false;
  caixaPontos.hidden = false;
  raiz.classList.add("carrossel--com-controles");

  sincronizar();
})();
