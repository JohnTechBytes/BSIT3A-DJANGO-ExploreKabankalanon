/* A failed recorded cover must not credit its labeled replacement illustration. */
document.addEventListener('error', function (event) {
  const image = event.target;
  if (!(image instanceof HTMLImageElement) || !image.hasAttribute('data-place-cover')) return;
  const card = image.closest('.place-card, .ea-card, .ea6-card, .eainfo-card, .ea-saved-item');
  if (card) card.querySelectorAll('.card-credit, .ea-card-credit, .ea6-photo-attribution, .eainfo-credit, .ea-saved-photo-attribution').forEach(credit => { credit.hidden = true; });
  const detail = image.closest('.pd-main');
  if (detail) {
    const credit = detail.querySelector('.pd-photo-meta');
    if (credit) credit.hidden = true;
  }
}, true);
