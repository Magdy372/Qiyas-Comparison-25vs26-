const buttons = document.querySelectorAll(".tab-button");
const panels = document.querySelectorAll(".tab-panel");

buttons.forEach((button) => {
  button.addEventListener("click", () => {
    const target = button.dataset.tab;

    buttons.forEach((item) => item.classList.remove("active"));
    panels.forEach((panel) => panel.classList.remove("active"));

    button.classList.add("active");
    document.querySelector(`.tab-panel[data-panel="${target}"]`)?.classList.add("active");
  });
});
