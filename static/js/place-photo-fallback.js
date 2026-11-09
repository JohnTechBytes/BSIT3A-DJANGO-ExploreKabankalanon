/* A recorded cover can fail even when a database reference exists. */
document.addEventListener('error', function (event) {
  const image = event.target;
  if (!(image instanceof HTMLImageElement) || !image.hasAttribute('data-place-cover')) return;

  const fallback = image.dataset.sampleSrc;
  const fallbackUrl = fallback ? new URL(fallback, document.baseURI).href : '';
  const isSample = image.dataset.sampleAttempted === 'true' || image.src === fallbackUrl;
  const galleryLink = image.closest('a[data-gallery-image]');

  if (fallback && !isSample) {
    // Never link a generated sample to the failed real photo's gallery.
    const target = galleryLink || image;
    const wrapper = document.createElement('div');
    wrapper.className = 'ek-fallback-image';
    target.replaceWith(wrapper);
    wrapper.appendChild(image);
    const label = document.createElement('span');
    label.className = 'ek-fallback-label';
    label.textContent = 'Photo unavailable · Illustrative sample · Not an actual photo';
    wrapper.appendChild(label);
    image.dataset.sampleAttempted = 'true';
    image.alt = 'Illustrative sample, not an actual photo of ' + (image.dataset.placeTitle || 'this place');
    // Photo credit belongs to the unavailable cover, not to this illustration.
    const detail = wrapper.closest('.pd-main');
    if (detail) {
      const credit = detail.querySelector('.pd-photo-meta');
      if (credit) credit.hidden = true;
    }
    const savedCard = wrapper.closest('.ea-saved-item');
    if (savedCard) {
      const credit = savedCard.querySelector('.ea-saved-photo-attribution');
      if (credit) credit.hidden = true;
    }
    image.src = fallback;
    return;
  }

  // If even the local illustration fails, avoid a retry loop and say so.
  const placeholder = document.createElement('div');
  placeholder.className = 'ek-photo-unavailable';
  placeholder.textContent = 'Photo unavailable';
  const target = galleryLink || image;
  const container = target.parentElement;
  target.replaceWith(placeholder);
  if (container) {
    const sampleLabel = container.querySelector('.ea-card-sample, .ea6-sample-badge, .pd-sample-note, .ea-saved-sample, .sample-photo-label, .sample-badge, .ek-fallback-label');
    if (sampleLabel) sampleLabel.remove();
  }
}, true);
