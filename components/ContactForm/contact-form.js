/* ==========================================================================
   ContactForm — compõe um link de WhatsApp a partir dos campos preenchidos.
   Sem dependências. Carregar com defer.

   Sem backend, o "envio" real e honesto disponível a um site estático é abrir
   uma conversa de WhatsApp já preenchida — a pessoa confirma e manda ela
   mesma, do próprio número dela. Nada trafega por este site.
   ========================================================================== */

(function () {
  "use strict";

  var NUMERO_WHATSAPP = "5511300000000"; // mesmo número do rodapé, formato E.164 sem "+"

  var form = document.querySelector("[data-contact-form]");
  if (!form) return;

  var campos = {
    nome: form.querySelector("#cf-nome"),
    telefone: form.querySelector("#cf-telefone"),
  };

  function erroDe(campo) {
    return form.querySelector('[data-error-for="' + campo.id + '"]');
  }

  function limpaErro(campo) {
    campo.removeAttribute("aria-invalid");
    var el = erroDe(campo);
    if (el) { el.hidden = true; el.textContent = ""; }
  }

  function marcaErro(campo, mensagem) {
    campo.setAttribute("aria-invalid", "true");
    var el = erroDe(campo);
    if (el) { el.hidden = false; el.textContent = mensagem; }
  }

  // Telefone brasileiro: 10 ou 11 dígitos depois de remover tudo que não é
  // número (aceita qualquer formatação que a pessoa digitar).
  function telefoneValido(valor) {
    var digitos = valor.replace(/\D/g, "");
    return digitos.length === 10 || digitos.length === 11;
  }

  function validar() {
    limpaErro(campos.nome);
    limpaErro(campos.telefone);

    var primeiroInvalido = null;

    if (!campos.nome.value.trim()) {
      marcaErro(campos.nome, "Informe seu nome.");
      primeiroInvalido = primeiroInvalido || campos.nome;
    }

    if (!telefoneValido(campos.telefone.value)) {
      marcaErro(campos.telefone, "Informe um WhatsApp válido, com DDD.");
      primeiroInvalido = primeiroInvalido || campos.telefone;
    }

    // Foco no primeiro campo com erro — a pessoa não precisa caçar o problema.
    if (primeiroInvalido) {
      primeiroInvalido.focus();
      return false;
    }
    return true;
  }

  function montaMensagem() {
    var dados = new FormData(form);
    var linhas = [
      "Olá! Vim pelo site da Lumina e gostaria de agendar uma avaliação.",
      "",
      "Nome: " + dados.get("nome"),
      "Especialidade de interesse: " + dados.get("especialidade"),
    ];
    var mensagem = (dados.get("mensagem") || "").trim();
    if (mensagem) linhas.push("Mensagem: " + mensagem);
    return linhas.join("\n");
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (!validar()) return;

    var texto = encodeURIComponent(montaMensagem());
    var url = "https://wa.me/" + NUMERO_WHATSAPP + "?text=" + texto;
    window.open(url, "_blank", "noopener");
  });

  // Corrige o próprio erro assim que a pessoa começa a digitar de novo —
  // não espera um novo submit para tirar a mensagem de erro que já resolveu.
  [campos.nome, campos.telefone].forEach(function (campo) {
    campo.addEventListener("input", function () {
      if (campo.getAttribute("aria-invalid") === "true") limpaErro(campo);
    });
  });
})();
