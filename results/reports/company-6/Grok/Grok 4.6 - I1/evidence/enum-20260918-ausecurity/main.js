/* ===========================
   Ausecurity — Main JS
   =========================== */

// ---- Auth utilities ----

/**
 * Check with the backend whether the current session cookie is valid.
 * Returns true if authenticated, false otherwise.
 */
async function isAuthenticated() {
  try {
    const res = await fetch('/api/auth/me', { credentials: 'same-origin' });
    return res.ok;
  } catch {
    return false;
  }
}

/**
 * Redirect to /login, preserving the current page as the ?redirect= param
 * so the user is sent back after a successful login.
 */
function redirectToLogin() {
  const redirect = encodeURIComponent(window.location.pathname + window.location.search);
  window.location.href = `/login?redirect=${redirect}`;
}

// ---- Dashboard auth guard ----
// Runs on dashboard.html: redirect to /login if not authenticated.
if (document.body.closest('[data-page="dashboard"]') ||
    window.location.pathname.replace(/\/$/, '').endsWith('/dashboard') ||
    window.location.pathname.replace(/\/$/, '').endsWith('/dashboard.html')) {
  isAuthenticated().then(authed => {
    if (!authed) {
      redirectToLogin();
    } else {
      // Populate the live date in the topbar
      const dateEl = document.getElementById('dash-date');
      if (dateEl) {
        dateEl.textContent = new Date().toLocaleDateString('en-AU', {
          weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
        });
      }
    }
  });

  // Logout button
  document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', async () => {
        await fetch('/api/auth/logout', { method: 'POST', credentials: 'same-origin' });
        window.location.href = '/login';
      });
    }
  });
}

// ---- Login form ----
// Runs on login.html: handles form submit + redirect-after-login.
if (window.location.pathname.replace(/\/$/, '').endsWith('/login') ||
    window.location.pathname.replace(/\/$/, '').endsWith('/login.html')) {

  // If already logged in, skip the login page
  isAuthenticated().then(authed => {
    if (authed) {
      const params = new URLSearchParams(window.location.search);
      window.location.href = params.get('redirect') || '/dashboard';
    }
  });

  document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('login-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      // Clear previous errors
      ['username', 'password'].forEach(field => {
        const input = document.getElementById(field);
        const err   = document.getElementById(`${field}-error`);
        if (input) input.classList.remove('error');
        if (err)   { err.textContent = ''; err.classList.remove('visible'); }
      });
      const banner = document.getElementById('login-error');
      if (banner) { banner.textContent = ''; banner.classList.remove('visible'); }

      const username = form.username.value.trim();
      const password = form.password.value;
      let valid = true;

      if (!username) {
        _loginFieldError('username', 'Username is required.');
        valid = false;
      }
      if (!password) {
        _loginFieldError('password', 'Password is required.');
        valid = false;
      }
      if (!valid) return;

      const submitBtn = form.querySelector('button[type="submit"]');
      submitBtn.disabled = true;
      submitBtn.textContent = 'Signing in…';

      try {
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'same-origin',
          body: JSON.stringify({ username, password }),
        });

        if (res.ok) {
          const params = new URLSearchParams(window.location.search);
          const redirect = params.get('redirect');
          // Safety check: only allow same-origin redirects
          if (redirect) {
            window.location.href = redirect;
          } else {
            window.location.href = '/dashboard';
          }
        } else {
          const json = await res.json().catch(() => ({}));
          const msg = json.detail || 'Invalid username or password.';
          if (banner) { banner.textContent = msg; banner.classList.add('visible'); }
        }
      } catch {
        if (banner) {
          banner.textContent = 'Network error. Please check your connection and try again.';
          banner.classList.add('visible');
        }
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Sign In';
      }
    });
  });
}

function _loginFieldError(field, msg) {
  const input = document.getElementById(field);
  const err   = document.getElementById(`${field}-error`);
  if (input) input.classList.add('error');
  if (err)   { err.textContent = msg; err.classList.add('visible'); }
}

// ---- Mobile nav toggle ----
document.addEventListener('DOMContentLoaded', () => {
  const hamburger = document.querySelector('.hamburger');
  const navLinks  = document.querySelector('.nav-links');

  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
      hamburger.classList.toggle('open');
      navLinks.classList.toggle('open');
    });
  }

  // Highlight active nav link
  const currentPath = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPath || (currentPath === '' && href === 'index.html')) {
      link.classList.add('active');
    }
  });
});

// ---- Contact form ----
const contactForm = document.getElementById('contact-form');
if (contactForm) {
  contactForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearErrors();

    const data = {
      full_name:        contactForm.full_name.value.trim(),
      company_name:     contactForm.company_name.value.trim(),
      email:            contactForm.email.value.trim(),
      phone:            contactForm.phone.value.trim() || null,
      service_interest: contactForm.service_interest.value,
      message:          contactForm.message.value.trim(),
      h: "contact.ausecurity.best"
    };

    let valid = true;

    if (!data.full_name) {
      showError('full_name', 'Full name is required.');
      valid = false;
    }
    if (!data.company_name) {
      showError('company_name', 'Company name is required.');
      valid = false;
    }
    if (!data.email || !isValidEmail(data.email)) {
      showError('email', 'A valid email address is required.');
      valid = false;
    }
    if (!data.service_interest) {
      showError('service_interest', 'Please select a service.');
      valid = false;
    }
    if (!data.message) {
      showError('message', 'Please describe your needs.');
      valid = false;
    }

    if (!valid) return;

    const submitBtn = contactForm.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Sending…';

    try {
      const apiBase = window.location.origin;
      const res = await fetch(`${apiBase}/api/contact`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(data),
      });

      const json = await res.json();

      if (res.ok && json.success) {
        // If a redirect URL is provided, navigate to it
        if (json.redirect_url) {
          window.location.href = json.redirect_url;
        } else {
          // Fallback to showing inline success message
          showFeedback('success', json.message || 'Thank you! We will be in touch shortly.');
          contactForm.reset();
        }
      } else {
        const detail = json.detail || 'Something went wrong. Please try again.';
        showFeedback('error-msg', detail);
      }
    } catch {
      showFeedback('error-msg', 'Network error. Please check your connection and try again.');
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Send Enquiry';
    }
  });
}

function showError(fieldName, msg) {
  const field = document.getElementById(fieldName);
  if (field) field.classList.add('error');
  const errEl = document.getElementById(`${fieldName}-error`);
  if (errEl) { errEl.textContent = msg; errEl.classList.add('visible'); }
}

function clearErrors() {
  document.querySelectorAll('.form-control').forEach(el => el.classList.remove('error'));
  document.querySelectorAll('.form-error-msg').forEach(el => {
    el.textContent = '';
    el.classList.remove('visible');
  });
  const fb = document.getElementById('form-feedback');
  if (fb) { fb.className = ''; fb.textContent = ''; fb.style.display = 'none'; }
}

function showFeedback(type, msg) {
  const fb = document.getElementById('form-feedback');
  if (!fb) return;
  fb.className = type;
  fb.textContent = msg;
  fb.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
