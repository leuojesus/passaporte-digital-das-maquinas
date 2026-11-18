(function () {
  "use strict";
  const botao = document.getElementById("alternar-contraste");
  if (!botao) return;
  const chave = "passaporte-digital:alto-contraste";
  let ativo = false;
  try { ativo = window.localStorage.getItem(chave) === "sim"; } catch (erro) { /* storage pode estar indisponível */ }
  function atualizar(valor) {
    ativo = valor;
    document.documentElement.classList.toggle("alto-contraste", ativo);
    botao.setAttribute("aria-pressed", String(ativo));
    botao.setAttribute("aria-label", ativo ? "Desativar alto contraste" : "Ativar alto contraste");
    botao.textContent = ativo ? "◐ Contraste ativo" : "◐ Alto contraste";
  }
  atualizar(ativo);
  botao.addEventListener("click", function () {
    atualizar(!ativo);
    try { window.localStorage.setItem(chave, ativo ? "sim" : "nao"); } catch (erro) { /* continua funcional */ }
  });
}());
