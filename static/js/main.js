const btn = document.getElementById("btn-menu");
const nav = document.querySelector("nav");

btn.addEventListener("click", ()=>{
  nav.classList.toggle("active");
});

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

