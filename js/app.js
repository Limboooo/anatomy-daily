(function () {
  const dialog = document.querySelector("dialog.lb");
  if (!dialog) return;
  const img = dialog.querySelector("img");
  document.querySelectorAll("button.shot").forEach((btn) => {
    btn.addEventListener("click", () => {
      const src = btn.getAttribute("data-full") || btn.querySelector("img").src;
      const alt = btn.querySelector("img") ? btn.querySelector("img").alt : "";
      img.src = src;
      img.alt = alt;
      if (typeof dialog.showModal === "function") dialog.showModal();
    });
  });
  dialog.addEventListener("click", (e) => {
    if (e.target === dialog) dialog.close();
  });
})();
