document.addEventListener('DOMContentLoaded', function() {
    const btn = document.getElementById('hamburger-btn');
    const menu = document.getElementById('navbar-menu');
    btn.addEventListener('click', function() {
        menu.classList.toggle('open');
        btn.setAttribute('aria-expanded', menu.classList.contains('open'));
    });
});
