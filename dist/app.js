const toggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('#nav-links');
if (toggle && nav) {
  const closeMenu = () => {
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Otwórz menu');
    nav.classList.remove('open');
  };
  toggle.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Zamknij menu' : 'Otwórz menu');
    nav.classList.toggle('open', open);
  });
  nav.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && nav.classList.contains('open')) {
      closeMenu(); toggle.focus();
    }
  });
  document.addEventListener('click', event => {
    if (!nav.contains(event.target) && !toggle.contains(event.target)) closeMenu();
  });
  matchMedia('(min-width: 1101px)').addEventListener('change', closeMenu);
}
const year = document.querySelector('#year');
if (year) year.textContent = new Date().getFullYear();
