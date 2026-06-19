window.addEventListener('scroll',()=>{

const nav=document.querySelector('nav');

if(window.scrollY>50){
nav.style.background='rgba(255,255,255,.95)';
}
else{
nav.style.background='rgba(255,255,255,.75)';
}

});

document.querySelector('.newsletter-form')
.addEventListener('submit',function(e){

e.preventDefault();

alert('Merci! Welcome to French Fluency Journal.');

});
const menuToggle = document.getElementById("menuToggle");
const navLinks = document.getElementById("navLinks");

menuToggle.addEventListener("click", () => {
    navLinks.classList.toggle("active");

    // change icon
    menuToggle.innerHTML = navLinks.classList.contains("active")
        ? '<i class="fa-solid fa-xmark"></i>'
        : '<i class="fa-solid fa-bars"></i>';
});

/* CLOSE MENU WHEN CLICKING A LINK */
document.querySelectorAll("#navLinks a").forEach(link => {
    link.addEventListener("click", () => {
        navLinks.classList.remove("active");
        menuToggle.innerHTML = '<i class="fa-solid fa-bars"></i>';
    });
});



