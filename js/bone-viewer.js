(function () {
  var viewers = document.querySelectorAll("model-viewer.bone");
  if (!viewers.length) return;
  var failed = new WeakSet();

  function noteFor(el) {
    var section = el.closest("section");
    return section && section.querySelector(".viewer-error");
  }

  function showError(el) {
    var note = noteFor(el);
    if (note) note.hidden = false;
  }

  function hideError(el) {
    var note = noteFor(el);
    if (note) note.hidden = true;
  }

  viewers.forEach(function (el) {
    el.addEventListener("error", function () {
      failed.add(el);
      showError(el);
    });
    el.addEventListener("load", function () {
      failed.delete(el);
      hideError(el);
    });
  });

  window.setTimeout(function () {
    if (!window.customElements || !window.customElements.get("model-viewer")) {
      viewers.forEach(showError);
    }
  }, 6000);

  if (window.customElements && window.customElements.whenDefined) {
    window.customElements.whenDefined("model-viewer").then(function () {
      viewers.forEach(function (el) {
        if (!failed.has(el)) hideError(el);
      });
    });
  }
})();
