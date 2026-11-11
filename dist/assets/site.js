(() => {
  'use strict';
  const bar = document.querySelector('.filter-bar');
  if (bar) {
    bar.hidden = false;
    bar.addEventListener('click', event => {
      const button = event.target.closest('button[data-filter]');
      if (!button) return;
      bar.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
      let count = 0;
      document.querySelectorAll('.meeting-card').forEach(card => {
        card.hidden = button.dataset.filter !== 'all' && !card.dataset.tags.includes(button.dataset.filter);
        if (!card.hidden) count++;
      });
      document.querySelector('#filter-status').textContent = `显示 ${count} 期会议记录`;
    });
  }
  const details = document.querySelector('.toc details');
  if (details) {
    const narrow = matchMedia('(max-width: 900px)');
    const sync = () => { details.open = !narrow.matches; };
    sync(); narrow.addEventListener('change', sync);
    details.querySelectorAll('a').forEach(a => a.addEventListener('click', () => { if (narrow.matches) details.open = false; }));
  }
  const dialog = document.querySelector('#lightbox');
  if (dialog && typeof dialog.showModal === 'function') {
    let opener;
    document.querySelectorAll('a.zoom').forEach(link => link.addEventListener('click', event => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault(); opener = link;
      const original = link.querySelector('img');
      const img = dialog.querySelector('img');
      img.src = link.href; img.alt = original.alt;
      dialog.querySelector('p').textContent = link.closest('figure').querySelector('figcaption')?.textContent || original.alt;
      dialog.showModal(); document.body.classList.add('modal-open');
    }));
    dialog.querySelector('button').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => { if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close(); } });
    dialog.addEventListener('close', () => { document.body.classList.remove('modal-open'); opener?.focus(); });
  }
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) if (entry.isIntersecting) {
        document.querySelectorAll('.toc a[href^="#"]').forEach(a => {
          if (a.hash === `#${entry.target.id}`) a.setAttribute('aria-current', 'true');
          else a.removeAttribute('aria-current');
        });
      }
    }, {rootMargin: '-100px 0px -55% 0px'});
    document.querySelectorAll('.prose h2[id],.prose h3[id]').forEach(h => observer.observe(h));
  }
})();
