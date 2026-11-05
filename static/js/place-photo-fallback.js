/* A recorded URL can still fail to load. Keep its container and actions intact. */
document.addEventListener('error', function (event) {
  const image = event.target;
  if (!(image instanceof HTMLImageElement) || !image.hasAttribute('data-place-cover')) return;

  const placeholder = document.createElement('div');
  placeholder.className = 'ek-photo-unavailable';
  placeholder.textContent = 'Photo unavailable';

  // A broken detail cover must not remain a link to the failed image.
  const galleryLink = image.closest('a[data-gallery-image]');
  const target = galleryLink || image;
  const container = target.parentElement;
  target.replaceWith(placeholder);
  if (container) {
    const sampleLabel = container.querySelector('.ea-card-sample, .ea6-sample-badge, .pd-sample-note, .ea-saved-sample, .sample-photo-label, .sample-badge');
    if (sampleLabel) sampleLabel.remove();
  }
}, true);
