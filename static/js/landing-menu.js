/* Native details keeps navigation usable without JavaScript. */
(() => {
  const menu = document.querySelector('.landing-menu');
  if (!menu) return;
  const summary = menu.querySelector('summary');
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menu.open) {
      menu.open = false;
      summary.focus();
    }
  });
  document.addEventListener('click', event => {
    if (menu.open && !menu.contains(event.target)) menu.open = false;
  });
  menu.querySelectorAll('nav a').forEach(link => link.addEventListener('click', () => { menu.open = false; }));
})();
