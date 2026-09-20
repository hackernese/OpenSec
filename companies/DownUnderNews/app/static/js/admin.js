/* =============================================================================
   The Down Under News – Admin JavaScript (admin.js)
   ============================================================================= */

'use strict';

document.addEventListener('DOMContentLoaded', () => {
  initSidebarToggle();
  initFlashDismiss();
});

// --------------------------------------------------------------------------- //
// Sidebar toggle (mobile)
// --------------------------------------------------------------------------- //
function initSidebarToggle() {
  const toggle   = document.getElementById('sidebarToggle');
  const close    = document.getElementById('sidebarClose');
  const sidebar  = document.getElementById('adminSidebar');
  const overlay  = document.getElementById('sidebarOverlay');

  if (!toggle || !sidebar) return;

  function openSidebar() {
    sidebar.classList.add('open');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeSidebar() {
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  toggle.addEventListener('click', openSidebar);
  if (close)   close.addEventListener('click', closeSidebar);
  if (overlay) overlay.addEventListener('click', closeSidebar);
}

// --------------------------------------------------------------------------- //
// Auto-dismiss flash messages after 5 seconds
// --------------------------------------------------------------------------- //
function initFlashDismiss() {
  document.querySelectorAll('.flash').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity .4s ease';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 400);
    }, 5000);
  });
}
