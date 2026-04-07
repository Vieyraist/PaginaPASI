<<<<<<< HEAD
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
=======
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
>>>>>>> 8687b47acec3e56a20ba149794975bbe32bc5030
