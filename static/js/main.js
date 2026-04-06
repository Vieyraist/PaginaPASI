const btnMenu = document.getElementById("btn-menu");
const overlay = document.querySelector(".menu-overlay");
const links = document.querySelectorAll(".mobile-menu a");

btnMenu.addEventListener("click", () => {
  document.body.classList.toggle("menu-open");
});

overlay.addEventListener("click", () => {
  document.body.classList.remove("menu-open");
});

links.forEach(link => {
  link.addEventListener("click", () => {
    document.body.classList.remove("menu-open");
  });
});

window.addEventListener("scroll", ()=>{
  document.getElementById("header").classList.toggle("scrolled", window.scrollY > 50);
});
