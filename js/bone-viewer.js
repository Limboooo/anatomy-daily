(function () {
  var viewers = document.querySelectorAll("model-viewer.bone");
  if (!viewers.length) return;

  function showError(el) {
    var section = el.closest("section");
    var note = section && section.querySelector(".viewer-error");
    if (note) note.hidden = false;
  }

  viewers.forEach(function (el) {
    el.addEventListener("error", function () {
      showError(el);
    });
  });

  window.setTimeout(function () {
    if (!window.customElements || !window.customElements.get("model-viewer")) {
      viewers.forEach(showError);
    }
  }, 6000);
})();
