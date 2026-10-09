/* =============================================================================
   The Down Under News – Main JavaScript (main.js)
   ============================================================================= */

'use strict';

// --------------------------------------------------------------------------- //
// DOM Ready
// --------------------------------------------------------------------------- //
document.addEventListener('DOMContentLoaded', () => {
  initDate();
  initMobileNav();
  initBackToTop();
  initBreakingNews();
  initFooterYear();
});

// --------------------------------------------------------------------------- //
// Date in header
// --------------------------------------------------------------------------- //
function initDate() {
  const el = document.getElementById('headerDate');
  if (!el) return;
  const now = new Date();
  el.textContent = now.toLocaleDateString('en-AU', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
  });
}

// --------------------------------------------------------------------------- //
// Mobile navigation toggle
// --------------------------------------------------------------------------- //
function initMobileNav() {
  const toggle = document.getElementById('mobileMenuToggle');
  const nav    = document.getElementById('mainNav');
  if (!toggle || !nav) return;

  toggle.addEventListener('click', () => {
    const isOpen = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(isOpen));
    toggle.classList.toggle('active', isOpen);
  });

  // Close when a nav link is tapped
  nav.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      nav.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    });
  });
}

// --------------------------------------------------------------------------- //
// Back to top
// --------------------------------------------------------------------------- //
function initBackToTop() {
  const btn = document.getElementById('backToTop');
  if (!btn) return;

  window.addEventListener('scroll', () => {
    btn.classList.toggle('visible', window.scrollY > 400);
  }, { passive: true });

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

// --------------------------------------------------------------------------- //
// Breaking news ticker – fetches latest headline from API
// --------------------------------------------------------------------------- //
function initBreakingNews() {
  const el = document.getElementById('breakingText');
  if (!el) return;

  fetch('/api/articles?limit=5')
    .then(r => r.json())
    .then(data => {
      const arts = data.articles || [];
      if (!arts.length) {
        document.getElementById('breakingBar').style.display = 'none';
        return;
      }
      const headlines = arts.map(a => a.title).join('   •   ');
      el.textContent = headlines;
    })
    .catch(() => {
      document.getElementById('breakingBar').style.display = 'none';
    });
}

// --------------------------------------------------------------------------- //
// Footer year
// --------------------------------------------------------------------------- //
function initFooterYear() {
  const el = document.getElementById('footerYear');
  if (el) el.textContent = new Date().getFullYear();
}
