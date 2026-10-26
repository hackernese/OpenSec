/**
 * Maps Company Insights - Popup Configuration
 */

document.addEventListener('DOMContentLoaded', async () => {
  const elements = {
    statusIndicator: document.getElementById('statusIndicator'),
    statusDot: document.getElementById('statusDot'),
    statusText: document.getElementById('statusText'),
    apiEndpoint: document.getElementById('apiEndpoint'),
    testButton: document.getElementById('testButton'),
    saveButton: document.getElementById('saveButton'),
    testResults: document.getElementById('testResults'),
    testResultIcon: document.getElementById('testResultIcon'),
    testResultText: document.getElementById('testResultText'),
    testResultDetails: document.getElementById('testResultDetails'),
    openMaps: document.getElementById('openMaps'),
    clearSettings: document.getElementById('clearSettings')
  };

  // Load current settings
  await loadCurrentSettings();

  // Event listeners
  elements.apiEndpoint.addEventListener('input', handleInputChange);
  elements.testButton.addEventListener('click', testConnection);
  elements.saveButton.addEventListener('click', saveSettings);
  elements.openMaps.addEventListener('click', openGoogleMaps);
  elements.clearSettings.addEventListener('click', clearAllSettings);

  // ─── Functions ──────────────────────────────────────────────────────────────

  async function loadCurrentSettings() {
    try {
      // Try Chrome extension storage first
      const result = await new Promise((resolve) => {
        chrome.storage.sync.get(['apiEndpoint'], resolve);
      });
      
      let endpoint = result.apiEndpoint;
      
      // Fallback to localStorage for legacy settings
      if (!endpoint) {
        const tabs = await chrome.tabs.query({ url: 'https://www.google.com/maps/*' });
        if (tabs.length > 0) {
          try {
            const results = await chrome.scripting.executeScript({
              target: { tabId: tabs[0].id },
              function: () => localStorage.getItem('maps-insights-api-endpoint')
            });
            endpoint = results[0]?.result;
          } catch (e) {
            console.warn('Could not access localStorage from Maps tab:', e);
          }
        }
      }

      // Default to localhost:4096 if no endpoint configured
      if (!endpoint) {
        endpoint = 'http://localhost:4096';
      }

      if (endpoint) {
        elements.apiEndpoint.value = endpoint;
        updateStatus('configured', '✅ OpenCode endpoint configured');
        enableButtons();
      } else {
        updateStatus('error', '⚠️ No API endpoint configured');
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
      updateStatus('error', '❌ Failed to load configuration');
    }
  }

  function handleInputChange() {
    const url = elements.apiEndpoint.value.trim();
    const isValid = isValidUrl(url);
    
    if (url && isValid) {
      updateStatus('', '⏳ Ready to test and save');
      enableButtons();
    } else if (url) {
      updateStatus('error', '❌ Invalid URL format');
      disableButtons();
    } else {
      updateStatus('error', '⚠️ No API endpoint configured');
      disableButtons();
    }

    // Clear previous test results
    elements.testResults.style.display = 'none';
  }

  async function testConnection() {
    const url = elements.apiEndpoint.value.trim();
    if (!url || !isValidUrl(url)) {
      showTestResult('error', '❌ Test Failed', 'Invalid URL format');
      return;
    }

    elements.testButton.disabled = true;
    elements.testButton.innerHTML = '<span class="btn-icon">⏳</span>Testing...';
    
    showTestResult('', '⏳ Testing Connection', 'Checking OpenCode API availability...');

    try {
      // Step 1: Create a test session
      const createSessionResponse = await fetch(`${url}/session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: 'Test from Maps Company Insights Extension'
        })
      });

      if (!createSessionResponse.ok) {
        const errorText = await createSessionResponse.text();
        throw new Error(`Failed to create session: ${createSessionResponse.status} ${createSessionResponse.statusText}\n\n${errorText}`);
      }

      const sessionData = await createSessionResponse.json();
      const sessionId = sessionData.id;

      if (!sessionId) {
        throw new Error('Session created but no ID returned from OpenCode');
      }

      // Step 2: Send a test message to the session
      const testMarkdown = `# Company's detail

- name: \`Test Business\`
- website: \`https://example.com\`
- googleMap: \`https://www.google.com/maps/test\`
- address: \`123 Test Street, Test City\`
- ownerName: \`Test Owner\`
- email: \`test@example.com\`

# Notes

This is a test message from the Maps Company Insights extension to verify the connection to OpenCode.`;

      const sendMessageResponse = await fetch(`${url}/session/${sessionId}/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          parts: [
            {
              type: 'text',
              text: testMarkdown
            }
          ]
        })
      });

      if (!sendMessageResponse.ok) {
        const errorText = await sendMessageResponse.text();
        throw new Error(`Failed to send message: ${sendMessageResponse.status} ${sendMessageResponse.statusText}\n\n${errorText}`);
      }

      showTestResult(
        'success',
        '✅ Test Successful',
        `OpenCode is running and accepting requests!\n\n✓ Session created: ${sessionId}\n✓ Message sent successfully\n\nYou can now use the extension to send business assessments to OpenCode.`
      );
    } catch (error) {
      showTestResult(
        'error',
        '❌ Connection Failed',
        `Error: ${error.message}\n\nPlease check:\n✓ OpenCode is running on ${url}\n✓ Port 4096 is accessible\n✓ No firewall blocking the connection\n\nExpected endpoints:\n• POST ${url}/session\n• POST ${url}/session/<id>/message`
      );
    } finally {
      elements.testButton.disabled = false;
      elements.testButton.innerHTML = '<span class="btn-icon">🔄</span>Test Connection';
    }
  }

  async function saveSettings() {
    const url = elements.apiEndpoint.value.trim();
    if (!url || !isValidUrl(url)) {
      updateStatus('error', '❌ Cannot save invalid URL');
      return;
    }

    elements.saveButton.disabled = true;
    elements.saveButton.innerHTML = '<span class="btn-icon">⏳</span>Saving...';

    try {
      // Save to Chrome extension storage
      await new Promise((resolve, reject) => {
        chrome.storage.sync.set({ apiEndpoint: url }, () => {
          if (chrome.runtime.lastError) {
            reject(chrome.runtime.lastError);
          } else {
            resolve();
          }
        });
      });

      // Also update localStorage on any open Maps tabs for immediate effect
      try {
        const tabs = await chrome.tabs.query({ url: 'https://www.google.com/maps/*' });
        for (const tab of tabs) {
          try {
            await chrome.scripting.executeScript({
              target: { tabId: tab.id },
              function: (endpoint) => {
                localStorage.setItem('maps-insights-api-endpoint', endpoint);
              },
              args: [url]
            });
          } catch (e) {
            console.warn('Could not update localStorage on tab:', tab.id, e);
          }
        }
      } catch (e) {
        console.warn('Could not update Maps tabs:', e);
      }

      updateStatus('configured', '✅ Settings saved successfully');
      
      // Show success feedback
      elements.saveButton.innerHTML = '<span class="btn-icon">✅</span>Saved!';
      setTimeout(() => {
        elements.saveButton.innerHTML = '<span class="btn-icon">💾</span>Save Settings';
        elements.saveButton.disabled = false;
      }, 2000);

    } catch (error) {
      console.error('Failed to save settings:', error);
      updateStatus('error', '❌ Failed to save settings');
      
      elements.saveButton.innerHTML = '<span class="btn-icon">❌</span>Failed';
      setTimeout(() => {
        elements.saveButton.innerHTML = '<span class="btn-icon">💾</span>Save Settings';
        elements.saveButton.disabled = false;
      }, 2000);
    }
  }

  async function openGoogleMaps() {
    try {
      await chrome.tabs.create({ url: 'https://www.google.com/maps' });
      window.close();
    } catch (error) {
      console.error('Failed to open Google Maps:', error);
    }
  }

  async function clearAllSettings() {
    if (!confirm('Are you sure you want to clear all settings? This will remove your API endpoint configuration.')) {
      return;
    }

    try {
      // Clear Chrome extension storage
      await new Promise((resolve, reject) => {
        chrome.storage.sync.clear(() => {
          if (chrome.runtime.lastError) {
            reject(chrome.runtime.lastError);
          } else {
            resolve();
          }
        });
      });

      // Clear localStorage on Maps tabs
      try {
        const tabs = await chrome.tabs.query({ url: 'https://www.google.com/maps/*' });
        for (const tab of tabs) {
          try {
            await chrome.scripting.executeScript({
              target: { tabId: tab.id },
              function: () => {
                localStorage.removeItem('maps-insights-api-endpoint');
              }
            });
          } catch (e) {
            console.warn('Could not clear localStorage on tab:', tab.id, e);
          }
        }
      } catch (e) {
        console.warn('Could not access Maps tabs:', e);
      }

      // Reset UI
      elements.apiEndpoint.value = '';
      elements.testResults.style.display = 'none';
      updateStatus('error', '⚠️ No API endpoint configured');
      disableButtons();

    } catch (error) {
      console.error('Failed to clear settings:', error);
      updateStatus('error', '❌ Failed to clear settings');
    }
  }

  // ─── Utility Functions ──────────────────────────────────────────────────────

  function isValidUrl(string) {
    try {
      const url = new URL(string);
      return url.protocol === 'http:' || url.protocol === 'https:';
    } catch (_) {
      return false;
    }
  }

  function updateStatus(type, message) {
    elements.statusText.textContent = message;
    elements.statusIndicator.className = `status-indicator ${type}`;
  }

  function enableButtons() {
    elements.testButton.disabled = false;
    elements.saveButton.disabled = false;
  }

  function disableButtons() {
    elements.testButton.disabled = true;
    elements.saveButton.disabled = true;
  }

  function showTestResult(type, title, details) {
    elements.testResultIcon.textContent = title.split(' ')[0]; // Extract emoji
    elements.testResultText.textContent = title.substring(2); // Remove emoji
    elements.testResultDetails.textContent = details;
    
    elements.testResults.className = `test-results ${type}`;
    elements.testResults.style.display = 'block';
  }
});