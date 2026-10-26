(function () {
  "use strict";

  const BUTTON_ID = "maps-insights-btn";

  // ─── Helpers ────────────────────────────────────────────────────────────────

  /**
   * Returns the place name shown in the current Maps side-panel, or null if
   * no business panel is open.
   *
   * Google Maps renders the place name inside an <h1> that lives inside the
   * main side-panel container (role="main").
   */
  function getPlaceName() {
    const panel = document.querySelector('[role="main"]');
    if (!panel) return null;

    const h1 = panel.querySelector("h1");
    return h1 ? h1.innerText.trim() : null;
  }

  /**
   * Attempts to extract the business address from the Maps side-panel.
   * Looks for address-like text in the panel structure.
   */
  function getPlaceAddress() {
    const panel = document.querySelector('[role="main"]');
    if (!panel) return null;

    // Try to find address in various common selectors
    const addressSelectors = [
      '[data-value="Address"]',
      '[aria-label*="Address"]',
      'button[jsaction*="address"]'
    ];

    for (const selector of addressSelectors) {
      const element = panel.querySelector(selector);
      if (element) {
        const text = element.textContent || element.innerText;
        if (text && text.trim()) return text.trim();
      }
    }

    // Fallback: look for any button that contains comma-separated text (likely an address)
    const buttons = panel.querySelectorAll('button');
    for (const button of buttons) {
      const text = button.textContent || button.innerText;
      if (text && text.includes(',') && text.length > 10 && text.length < 200) {
        // Skip if it looks like a phone number or other non-address content
        if (!/^\+?[\d\s\-\(\)]+$/.test(text)) {
          return text.trim();
        }
      }
    }

    return null;
  }

  /**
   * Attempts to extract the business website from the Maps side-panel.
   * Looks for website links in the business information.
   */
  function getBusinessWebsite() {
    const panel = document.querySelector('[role="main"]');
    if (!panel) return null;

    // Try to find website link in various common selectors
    const websiteSelectors = [
      'a[href*="http"]:not([href*="google.com"]):not([href*="maps.google"])',
      '[data-value*="http"]:not([data-value*="google.com"])',
      'button[jsaction*="website"]',
      '[aria-label*="Website"]',
      '[aria-label*="website"]'
    ];

    for (const selector of websiteSelectors) {
      const element = panel.querySelector(selector);
      if (element) {
        // Try to get URL from href attribute first
        const href = element.getAttribute('href');
        if (href && isValidBusinessUrl(href)) {
          return href;
        }
        
        // Try to get URL from data-value attribute
        const dataValue = element.getAttribute('data-value');
        if (dataValue && isValidBusinessUrl(dataValue)) {
          return dataValue;
        }
        
        // Try to extract URL from text content
        const text = element.textContent || element.innerText;
        if (text && isValidBusinessUrl(text.trim())) {
          return text.trim();
        }
      }
    }

    // Fallback: look for any link that looks like a business website
    const allLinks = panel.querySelectorAll('a[href]');
    for (const link of allLinks) {
      const href = link.getAttribute('href');
      if (href && isValidBusinessUrl(href)) {
        return href;
      }
    }

    return null;
  }

  /**
   * Checks if a URL looks like a business website (not Google/Maps related)
   */
  function isValidBusinessUrl(url) {
    try {
      const urlObj = new URL(url);
      const domain = urlObj.hostname.toLowerCase();
      
      // Skip Google-related domains
      if (domain.includes('google.com') || 
          domain.includes('maps.google') || 
          domain.includes('goo.gl') ||
          domain.includes('googleusercontent.com')) {
        return false;
      }
      
      // Must be http/https
      if (!['http:', 'https:'].includes(urlObj.protocol)) {
        return false;
      }
      
      return true;
    } catch (_) {
      return false;
    }
  }

  /**
   * Finds the action-button bar (the row with Directions / Save / Share …).
   * Google Maps uses a <div> whose direct children are the action buttons.
   * We look for the container that holds at least a "Directions" button as a
   * reliable anchor.
   */
  function findActionBar() {
    // The action buttons share a common wrapper; each button is an <button>
    // element with an aria-label. We locate any button labelled "Directions"
    // and return its parent container.
    const directionsBtn = document.querySelector(
      '[aria-label="Directions"], [data-value="Directions"]'
    );
    return directionsBtn ? directionsBtn.closest("div") : null;
  }

  // ─── Button injection ────────────────────────────────────────────────────────

  function removeExistingButton() {
    const existing = document.getElementById(BUTTON_ID);
    if (existing) existing.remove();
  }

  function createInsightsButton(placeName) {
    const btn = document.createElement("button");
    btn.id = BUTTON_ID;
    btn.className = "maps-insights-btn";
    btn.setAttribute("aria-label", "Company Insights");
    btn.setAttribute("title", `View insights for "${placeName}"`);

    // Icon + label layout (mirrors the Maps action-button style)
    btn.innerHTML = `
      <span class="maps-insights-btn__icon" aria-hidden="true">

<svg fill="#014f5a" width="20px" height="20px" viewBox="0 0 35 35" data-name="Layer 2" id="Layer_2" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"><path d="M17.5,34.44A3.07,3.07,0,0,1,15.89,34L9.82,30.45A14.79,14.79,0,0,1,2.25,17.7V8A3.2,3.2,0,0,1,4.34,5L16.4.57a3.2,3.2,0,0,1,2.2,0L30.66,5a3.2,3.2,0,0,1,2.09,3V17.7a14.79,14.79,0,0,1-7.57,12.75L19.11,34A3.07,3.07,0,0,1,17.5,34.44Zm0-31.56a.67.67,0,0,0-.24,0L5.2,7.33A.69.69,0,0,0,4.75,8V17.7a12.3,12.3,0,0,0,6.33,10.59l6.07,3.56a.73.73,0,0,0,.7,0l6.07-3.56h0A12.3,12.3,0,0,0,30.25,17.7V8a.69.69,0,0,0-.45-.65L17.74,2.92A.67.67,0,0,0,17.5,2.88Z"></path><path d="M16.4,22.35a1.3,1.3,0,0,1-.81-.29l-4.27-3.6a1.25,1.25,0,0,1,1.61-1.92l3.35,2.82L22,13.06a1.25,1.25,0,0,1,1.86,1.68l-6.48,7.2A1.27,1.27,0,0,1,16.4,22.35Z"></path></g></svg>

      </span>
      <span class="maps-insights-btn__label">Assess</span>
    `;

    btn.addEventListener("click", () => onInsightsClick(placeName));
    return btn;
  }

  function injectButton(placeName) {
    removeExistingButton();

    const bar = findActionBar();
    if (!bar) return; // panel not fully rendered yet – observer will retry

    const btn = createInsightsButton(placeName);
    bar.appendChild(btn);
  }

  // ─── Button click handler ────────────────────────────────────────────────────

  function onInsightsClick(placeName) {
    showModal(placeName);
  }

  // ─── Modal ───────────────────────────────────────────────────────────────────

  function showModal(placeName) {
    // Remove any stale modal
    const stale = document.getElementById("maps-insights-modal");
    if (stale) stale.remove();

    const overlay = document.createElement("div");
    overlay.id = "maps-insights-modal";
    overlay.className = "maps-insights-modal";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.setAttribute("aria-label", `Insights for ${placeName}`);

    overlay.innerHTML = `
      <div class="maps-insights-modal__box">
        <div class="maps-insights-modal__header">
          <h2 class="maps-insights-modal__title">
<svg fill="#014f5a" width="20px" height="20px" viewBox="0 0 35 35" data-name="Layer 2" id="Layer_2" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"><path d="M17.5,34.44A3.07,3.07,0,0,1,15.89,34L9.82,30.45A14.79,14.79,0,0,1,2.25,17.7V8A3.2,3.2,0,0,1,4.34,5L16.4.57a3.2,3.2,0,0,1,2.2,0L30.66,5a3.2,3.2,0,0,1,2.09,3V17.7a14.79,14.79,0,0,1-7.57,12.75L19.11,34A3.07,3.07,0,0,1,17.5,34.44Zm0-31.56a.67.67,0,0,0-.24,0L5.2,7.33A.69.69,0,0,0,4.75,8V17.7a12.3,12.3,0,0,0,6.33,10.59l6.07,3.56a.73.73,0,0,0,.7,0l6.07-3.56h0A12.3,12.3,0,0,0,30.25,17.7V8a.69.69,0,0,0-.45-.65L17.74,2.92A.67.67,0,0,0,17.5,2.88Z"></path><path d="M16.4,22.35a1.3,1.3,0,0,1-.81-.29l-4.27-3.6a1.25,1.25,0,0,1,1.61-1.92l3.35,2.82L22,13.06a1.25,1.25,0,0,1,1.86,1.68l-6.48,7.2A1.27,1.27,0,0,1,16.4,22.35Z"></path></g></svg>

            Security Assessment
          </h2>
          <button class="maps-insights-modal__close" aria-label="Close insights panel">✕</button>
        </div>

        <div class="maps-insights-modal__body">
          <p class="maps-insights-modal__company-name">${escapeHtml(placeName)}</p>
          <p class="maps-insights-modal__purpose">The purpose of this extension is to quickly evaluate the general security poture of your business.</p>

          <div class="maps-insights-modal__section">
            <h3>Email Address</h3>
            <input class="maps-insights-modal__email-input"
                   type="email"
                   placeholder="your@email.com" />
            <p class="maps-insights-modal__help-text">When everything is done, the report will be sent back to this email</p>
          </div>

          <div class="maps-insights-modal__section">
            <h3>Owner Name <span class="maps-insights-modal__optional">(optional)</span></h3>
            <input class="maps-insights-modal__owner-input"
                   type="text"
                   placeholder="e.g. John Smith" />
          </div>

          <div class="maps-insights-modal__section">
            <h3>Notes</h3>
            <textarea class="maps-insights-modal__notes"
                      placeholder="Add your notes about this company…"
                      rows="4"></textarea>
            <button class="maps-insights-modal__save-btn">Assess</button>
          </div>

          <div class="maps-insights-modal__saved-note" style="display:none;">
            <strong>Saved note:</strong>
            <p class="maps-insights-modal__saved-text"></p>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(overlay);
    bindModalEvents(overlay, placeName);
  }

  function bindModalEvents(overlay, placeName) {
    // Close on backdrop click
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) overlay.remove();
    });

    // Close button
    overlay
      .querySelector(".maps-insights-modal__close")
      .addEventListener("click", () => overlay.remove());

    // Keyboard: Escape closes
    document.addEventListener(
      "keydown",
      function escHandler(e) {
        if (e.key === "Escape") {
          overlay.remove();
          document.removeEventListener("keydown", escHandler);
        }
      }
    );

    // Save note → send to API
    overlay
      .querySelector(".maps-insights-modal__save-btn")
      .addEventListener("click", async () => {
        const textarea = overlay.querySelector(".maps-insights-modal__notes");
        const ownerInput = overlay.querySelector(".maps-insights-modal__owner-input");
        const emailInput = overlay.querySelector(".maps-insights-modal__email-input");
        const saveBtn = overlay.querySelector(".maps-insights-modal__save-btn");
        const notes = textarea.value.trim();
        const ownerName = ownerInput ? ownerInput.value.trim() : "";
        const email = emailInput ? emailInput.value.trim() : "";

        // Validate email if provided
        if (email && !isValidEmail(email)) {
          showToast("❌ Please enter a valid email address", "error");
          return;
        }

        // Build Markdown output
        const googleMapUrl = window.location.href;
        const address = getPlaceAddress();
        const owner = ownerName || "AAA's customer";
        const website = getBusinessWebsite() || "N/A";

        const markdown = [
          `# Company's detail`,
          ``,
          `- name: \`${placeName}\``,
          `- website: \`${website}\``,
          `- googleMap: \`${googleMapUrl}\``,
          `- address: \`${address || "N/A"}\``,
          `- ownerName: \`${owner}\``,
          `- email: \`${email || "N/A"}\``,
          ``,
          `# Notes`,
          ``,
          notes || "",
        ].join("\n");

        // Log markdown to console for debugging/verification
        console.log("📋 Generated Markdown for:", placeName);
        console.log("━".repeat(50));
        console.log(markdown);
        console.log("━".repeat(50));

        // Show loading state
        const originalText = saveBtn.textContent;
        saveBtn.textContent = "Sending...";
        saveBtn.disabled = true;

        try {
          // Send to API endpoint (configurable)
          const apiEndpoint = await getApiEndpoint();
          
          if (!apiEndpoint) {
            throw new Error("API endpoint not configured. Please set it in extension options.");
          }

          const response = await fetch(apiEndpoint, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              placeName,
              website: website,
              googleMapUrl: googleMapUrl,
              address: address || "N/A",
              ownerName: owner,
              email: email || null,
              notes,
              markdown,
              timestamp: new Date().toISOString()
            })
          });

          if (!response.ok) {
            throw new Error(`API request failed: ${response.status} ${response.statusText}`);
          }

          // Persist to localStorage keyed by place name
          const key = `maps-insights-note::${placeName}`;
          localStorage.setItem(key, JSON.stringify({ notes, ownerName, email }));

          // Show success toast and close modal
          showToast("✅ Successfully saved and sent to API!", "success");
          setTimeout(() => overlay.remove(), 1000);

        } catch (error) {
          console.error('Failed to send to API:', error);
          
          // Show error toast
          showToast(`❌ Failed to send to API: ${error.message}`, "error");

          saveBtn.textContent = originalText;
          saveBtn.disabled = false;
        }
      });

    // Load existing note
    const key = `maps-insights-note::${placeName}`;
    const saved = localStorage.getItem(key);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        const textarea = overlay.querySelector(".maps-insights-modal__notes");
        const ownerInput = overlay.querySelector(".maps-insights-modal__owner-input");
        const emailInput = overlay.querySelector(".maps-insights-modal__email-input");
        if (textarea && parsed.notes) textarea.value = parsed.notes;
        if (ownerInput && parsed.ownerName) ownerInput.value = parsed.ownerName;
        if (emailInput && parsed.email) emailInput.value = parsed.email;
      } catch (_) {
        // Legacy plain-text note — load into textarea only
        const textarea = overlay.querySelector(".maps-insights-modal__notes");
        if (textarea) textarea.value = saved;
      }
    }
  }

  // ─── Utility ─────────────────────────────────────────────────────────────────

  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  function showToast(message, type = "success") {
    // Remove any existing toast
    const existingToast = document.getElementById("maps-insights-toast");
    if (existingToast) existingToast.remove();

    const toast = document.createElement("div");
    toast.id = "maps-insights-toast";
    toast.className = `maps-insights-toast maps-insights-toast--${type}`;
    toast.textContent = message;

    document.body.appendChild(toast);

    // Trigger animation
    setTimeout(() => toast.classList.add("maps-insights-toast--show"), 10);

    // Auto-remove after 4 seconds
    setTimeout(() => {
      toast.classList.remove("maps-insights-toast--show");
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  /**
   * Gets the API endpoint from storage. Returns null if not configured.
   * You can set this by running in console: 
   * localStorage.setItem('maps-insights-api-endpoint', 'https://your-api.com/endpoint')
   */
  async function getApiEndpoint() {
    // Try localStorage first (for quick setup)
    const fromStorage = localStorage.getItem('maps-insights-api-endpoint');
    if (fromStorage) return fromStorage;

    // Try Chrome extension storage (for proper extension options)
    try {
      const result = await new Promise((resolve) => {
        chrome.storage.sync.get(['apiEndpoint'], resolve);
      });
      return result.apiEndpoint || null;
    } catch (error) {
      console.warn('Chrome storage not available, using localStorage only');
      return null;
    }
  }

  // ─── MutationObserver – watches for panel changes ────────────────────────────

  let lastPlaceName = null;
  let debounceTimer = null;

  function checkAndInject() {
    const placeName = getPlaceName();

    if (!placeName) {
      // No panel open – clean up
      removeExistingButton();
      lastPlaceName = null;
      return;
    }

    if (placeName === lastPlaceName && document.getElementById(BUTTON_ID)) {
      // Same place, button already present
      return;
    }

    lastPlaceName = placeName;
    injectButton(placeName);
  }

  function scheduledCheck() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(checkAndInject, 400);
  }

  const observer = new MutationObserver(scheduledCheck);

  observer.observe(document.body, {
    childList: true,
    subtree: true,
    attributes: false,
    characterData: false,
  });

  // Initial check in case the page already shows a place
  checkAndInject();
})();
