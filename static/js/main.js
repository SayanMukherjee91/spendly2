// main.js — students will add JavaScript here as features are built

(function () {
    var hamburger = document.getElementById('navHamburger');
    var navLinks  = document.getElementById('navLinks');
    if (!hamburger) return;

    hamburger.addEventListener('click', function () {
        var open = navLinks.classList.toggle('nav-open');
        hamburger.classList.toggle('nav-open', open);
        hamburger.setAttribute('aria-expanded', String(open));
    });

    document.addEventListener('click', function (e) {
        if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
            navLinks.classList.remove('nav-open');
            hamburger.classList.remove('nav-open');
            hamburger.setAttribute('aria-expanded', 'false');
        }
    });
}());
