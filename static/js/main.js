// Toggle mobile navigation
document.addEventListener('DOMContentLoaded', function() {
    const toggle = document.querySelector('[data-mobile-navigation-toggle]');
    const mobileNav = document.querySelector('[data-mobile-navigation]');
    if (toggle && mobileNav) {
        toggle.addEventListener('click', function() {
            const expanded = toggle.getAttribute('aria-expanded') === 'true';
            toggle.setAttribute('aria-expanded', !expanded);
            mobileNav.hidden = expanded;
        });
    }
});