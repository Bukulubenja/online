gsap.registerPlugin(ScrollTrigger);

// HERO ANIMATION
gsap.from("#heroTitle",{
    opacity:0,
    y:60,
    duration:1.2
});

gsap.from("#heroText",{
    opacity:0,
    y:30,
    delay:0.3
});

// CARD ANIMATION
gsap.utils.toArray(".card").forEach(card=>{
    gsap.to(card,{
        scrollTrigger:{
            trigger:card,
            start:"top 85%"
        },
        opacity:1,
        y:0,
        duration:0.8,
        ease:"power3.out"
    });
});

// LANGUAGE TOGGLE
function setLang(lang){
    document.querySelectorAll(".lang-toggle button")
    .forEach(b=>b.classList.remove("active"));

    event.target.classList.add("active");

    if(lang === "FR"){
        document.getElementById("heroTitle").innerHTML =
        "Maîtrisez le <span>Français</span> avec élégance et précision";

        document.getElementById("heroText").innerText =
        "Grammaire • Vocabulaire • Culture • Prononciation • Préparation DELF";
    } else {
        document.getElementById("heroTitle").innerHTML =
        "Master <span>French</span> with Elegance & Precision";

        document.getElementById("heroText").innerText =
        "Grammar • Vocabulary • Culture • Pronunciation • DELF Preparation";
    }
}