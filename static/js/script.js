/* =========================
   DARK MODE TOGGLE
========================= */
const darkToggle = document.getElementById("darkToggle");

darkToggle?.addEventListener("click", () => {
    document.body.classList.toggle("dark");

    if (document.body.classList.contains("dark")) {
        localStorage.setItem("theme", "dark");
    } else {
        localStorage.setItem("theme", "light");
    }
});

// Load saved theme
window.addEventListener("load", () => {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "dark") {
        document.body.classList.add("dark");
    }
});


/* =========================
   SMOOTH SCROLL NAVIGATION
========================= */
document.querySelectorAll("a[href^='#']").forEach(anchor => {
    anchor.addEventListener("click", function (e) {
        e.preventDefault();

        const target = document.querySelector(this.getAttribute("href"));
        if (target) {
            target.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        }
    });
});


/* =========================
   FAQ ACCORDION SYSTEM
========================= */
const faqItems = document.querySelectorAll(".faq-item");

faqItems.forEach(item => {
    item.addEventListener("click", () => {
        item.classList.toggle("active");

        const answer = item.querySelector("p");
        if (answer) {
            answer.style.maxHeight =
                answer.style.maxHeight ? null : answer.scrollHeight + "px";
        }
    });
});


/* =========================
   COUNTER ANIMATION (STATS)
========================= */
const counters = document.querySelectorAll(".stat h2");

const animateCounters = () => {
    counters.forEach(counter => {
        const updateCount = () => {
            const target = +counter.innerText.replace(/[^0-9]/g, "");
            let count = 0;

            const speed = 200;
            const increment = target / speed;

            const timer = setInterval(() => {
                count += increment;

                if (count >= target) {
                    counter.innerText = counter.innerText;
                    clearInterval(timer);
                } else {
                    counter.innerText = Math.floor(count) + "+";
                }
            }, 10);
        };

        updateCount();
    });
};


/* =========================
   TRIGGER COUNTERS ON SCROLL
========================= */
let counterTriggered = false;

window.addEventListener("scroll", () => {
    const heroStats = document.querySelector(".hero-stats");

    if (!heroStats) return;

    const position = heroStats.getBoundingClientRect().top;

    if (position < window.innerHeight && !counterTriggered) {
        animateCounters();
        counterTriggered = true;
    }
});


/* =========================
   SIMPLE TESTIMONIAL CAROUSEL
========================= */
let currentIndex = 0;

const testimonials = document.querySelectorAll(".testimonial");

function showTestimonial(index) {
    testimonials.forEach((t, i) => {
        t.style.display = i === index ? "block" : "none";
    });
}

function startCarousel() {
    if (testimonials.length === 0) return;

    showTestimonial(currentIndex);

    setInterval(() => {
        currentIndex = (currentIndex + 1) % testimonials.length;
        showTestimonial(currentIndex);
    }, 4000);
}

startCarousel();


/* =========================
   SEARCH FUNCTIONALITY (BASIC FILTER)
========================= */
const searchInput = document.querySelector(".hero-search input");

searchInput?.addEventListener("keyup", function () {
    const query = this.value.toLowerCase();
    const cards = document.querySelectorAll(".card");

    cards.forEach(card => {
        const text = card.innerText.toLowerCase();

        if (text.includes(query)) {
            card.style.display = "block";
        } else {
            card.style.display = "none";
        }
    });
});


/* =========================
   SCROLL ANIMATIONS (FALLBACK)
========================= */
const animateOnScroll = () => {
    const elements = document.querySelectorAll(".card, .section-title, .teacher");

    elements.forEach(el => {
        const position = el.getBoundingClientRect().top;
        const screenHeight = window.innerHeight;

        if (position < screenHeight - 100) {
            el.style.opacity = 1;
            el.style.transform = "translateY(0)";
            el.style.transition = "all 0.6s ease-out";
        } else {
            el.style.opacity = 0;
            el.style.transform = "translateY(20px)";
        }
    });
};

window.addEventListener("scroll", animateOnScroll);


/* =========================
   INITIALIZE ON LOAD
========================= */
window.addEventListener("load", () => {
    animateOnScroll();
});


/* =========================
   BOOKMARK SYSTEM (LOCAL STORAGE)
========================= */
function toggleBookmark(title) {
    let bookmarks = JSON.parse(localStorage.getItem("bookmarks")) || [];

    if (bookmarks.includes(title)) {
        bookmarks = bookmarks.filter(item => item !== title);
    } else {
        bookmarks.push(title);
    }

    localStorage.setItem("bookmarks", JSON.stringify(bookmarks));
}




/* =========================
   DARK MODE SMOOTH TRANSITION
========================= */
document.body.style.transition = "background 0.5s ease, color 0.5s ease";

// DARK MODE
document.getElementById("darkToggle").onclick = () => {
  document.body.classList.toggle("dark");
};

// MOBILE MENU
document.getElementById("toggleMenu").onclick = () => {
  document.getElementById("menu").classList.toggle("active");
};


AOS.init({ duration: 800, offset: 120 });
const menuToggle = document.getElementById('menuToggle');
const navMenuWrapper = document.getElementById('navMenuWrapper');
menuToggle.addEventListener('click', () => {menuToggle.classList.toggle('is-active');navMenuWrapper.classList.toggle('is-active');});

