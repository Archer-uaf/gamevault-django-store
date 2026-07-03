document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.querySelector("[data-nav-toggle]");
    const navigation = document.querySelector("[data-navigation]");

    if (toggle && navigation) {
        toggle.addEventListener("click", () => {
            const isOpen = toggle.getAttribute("aria-expanded") === "true";
            toggle.setAttribute("aria-expanded", String(!isOpen));
            navigation.classList.toggle("is-open", !isOpen);
        });

        navigation.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", () => {
                toggle.setAttribute("aria-expanded", "false");
                navigation.classList.remove("is-open");
            });
        });
    }

    const year = document.querySelector("[data-current-year]");
    if (year) {
        year.textContent = String(new Date().getFullYear());
    }
});
