const toggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('#nav-links');
const metalsToggle = document.querySelector('.metals-toggle');
const metalsMenu = document.querySelector('#metals-links');
function closeMetals() {
  if (!metalsToggle || !metalsMenu) return;
  metalsToggle.setAttribute('aria-expanded', 'false');
  metalsMenu.hidden = true;
}
function closeMenu() {
  if (!toggle || !nav) return;
  toggle.setAttribute('aria-expanded', 'false');
  toggle.setAttribute('aria-label', 'Otwórz menu');
  nav.classList.remove('open');
  document.body.classList.remove('navigation-open');
  closeMetals();
}
if (toggle && nav) {
  toggle.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    if (!open) { closeMenu(); return; }
    toggle.setAttribute('aria-expanded', 'true');
    toggle.setAttribute('aria-label', 'Zamknij menu');
    nav.classList.add('open');
    document.body.classList.add('navigation-open');
  });
  nav.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    if (metalsToggle?.getAttribute('aria-expanded') === 'true') {
      closeMetals(); metalsToggle.focus();
    } else if (nav.classList.contains('open')) {
      closeMenu(); toggle.focus();
    }
  });
  document.addEventListener('click', event => {
    if (!nav.contains(event.target) && !toggle.contains(event.target)) closeMenu();
  });
  matchMedia('(min-width: 1101px)').addEventListener('change', closeMenu);
}
if (metalsToggle && metalsMenu) {
  metalsToggle.addEventListener('click', () => {
    const open = metalsToggle.getAttribute('aria-expanded') !== 'true';
    metalsToggle.setAttribute('aria-expanded', String(open));
    metalsMenu.hidden = !open;
  });
}
const year = document.querySelector('#year');
if (year) year.textContent = new Date().getFullYear();
