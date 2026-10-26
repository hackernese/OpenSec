# Changelog - OpenCode Integration

## Changes Made for OpenCode Integration

### Modified Files

#### 1. `content.js` - Main Content Script
**Changes:**
- Updated API flow to use two separate endpoints:
  1. Create session: `POST /session` with `{title: "..."}`
  2. Send message: `POST /session/{id}/message` with `{parts: [{type: "text", text: "..."}]}`
- Changed request payload to match OpenCode's actual API format
- Extracts session ID from create session response
- Sends markdown content as a message part
- Updated success messages to include session ID
- Changed default endpoint to `http://localhost:4096`
- Updated error messages to be more OpenCode-specific

**Key Changes:**
```javascript
// Old: Single API call (incorrect)
fetch(apiEndpoint, { method: 'POST', body: JSON.stringify({...}) })

// New: Two-step process (correct)
// Step 1: Create session
fetch(`${apiEndpoint}/session`, {
  method: 'POST',
  body: JSON.stringify({ title: "Security Assessment: ..." })
})
// Step 2: Send message
fetch(`${apiEndpoint}/session/${sessionId}/message`, {
  method: 'POST',
  body: JSON.stringify({
    parts: [{ type: 'text', text: markdown }]
  })
})
```

#### 2. `popup.js` - Configuration Popup
**Changes:**
- Updated default endpoint to `http://localhost:4096` instead of requiring manual configuration
- Modified test connection logic to use OpenCode's actual API:
  1. Create test session: `POST /session`
  2. Send test message: `POST /session/{id}/message`
- Updated test payload to use correct message format with `parts` array
- Enhanced error messages with correct endpoint paths

#### 3. `popup.html` - Configuration UI
**Changes:**
- Updated page title from "Configure your API endpoint" to "Configure OpenCode integration"
- Changed input label from "API Endpoint URL" to "OpenCode Endpoint URL"
- Updated placeholder from generic URL to `http://localhost:4096`
- Modified help text to mention OpenCode and sessions

#### 4. `README.md` - Documentation
**Changes:**
- Rewrote entire README to focus on OpenCode integration
- Added OpenCode features section
- Documented expected Markdown format for ClawSec
- Added requirements section mentioning OpenCode and ClawSec
- Updated configuration instructions for OpenCode

#### 5. `SETUP.md` - New File
**Created comprehensive setup guide covering:**
- Prerequisites (OpenCode, Chrome, ClawSec)
- Step-by-step installation instructions
- Configuration walkthrough
- Usage guide
- OpenCode workflow explanation (INTAKE → AUTHORIZED → ... → COMPLETE)
- Troubleshooting section
- API endpoint details
- Security notes
- Advanced configuration options

### What the Extension Now Does

1. **Extracts business information from Google Maps:**
   - Business name
   - Website URL
   - Google Maps URL
   - Physical address
   
2. **Collects additional assessment details:**
   - Owner name (optional)
   - Email for report delivery (optional)
   - Custom notes

3. **Generates ClawSec-compatible Markdown:**
   ```markdown
   # Company's detail
   
   - name: `Business Name`
   - website: `https://example.com`
   - googleMap: `https://www.google.com/maps/...`
   - address: `123 Main St`
   - ownerName: `John Doe`
   - email: `john@example.com`
   
   # Notes
   
   Custom notes here...
   ```

4. **Creates new OpenCode session:**
   - POST request to `http://localhost:4096/session` (creates session)
   - POST request to `http://localhost:4096/session/{id}/message` (sends markdown)
   - Sends Markdown in `parts` array with type "text"
   - Uses session title: "Security Assessment: {business name}"

5. **Provides feedback:**
   - Success toast with session ID
   - Error messages with troubleshooting hints
   - Saves notes locally for reference

### Integration with ClawSec Workflow

The extension output format matches ClawSec's INTAKE requirements:

```text
# Company's detail

- name: `Business Name`
- website: `https://business-website.com`
- googleMap: `https://www.google.com/maps/place/...`
- address: `Physical address`
- ownerName: `Owner Name`
- email: `owner@email.com`

# Notes

Additional context or instructions
```

This triggers ClawSec's assessment workflow:
1. **INTAKE** - Parse business information
2. **AUTHORIZED** - Check authorization header on website
3. **ENUMERATED** - Discover all assets
4. **ASSESSING** - Run vulnerability scans
5. **VALIDATING** - Confirm findings
6. **REPORTING** - Generate report
7. **COMPLETE** - Deliver to email

### Testing the Integration

1. **Start OpenCode:**
   ```bash
   cd /home/research/Github/Thesis/OpenCode
   # Start OpenCode on port 4096
   ```

2. **Install extension:**
   - Chrome → `chrome://extensions/`
   - Enable Developer mode
   - Load unpacked → select `/home/research/Github/OpenSec/browser`

3. **Configure:**
   - Click extension icon
   - Verify endpoint: `http://localhost:4096`
   - Test connection
   - Save settings

4. **Test:**
   - Go to Google Maps
   - Search for a business
   - Click "Assess" button
   - Fill in details
   - Click "Assess"
   - Check OpenCode for new session

### Default Configuration

- **Default Endpoint:** `http://localhost:4096`
- **API Endpoints Used:**
  - `POST /session` - Create new session
  - `POST /session/{id}/message` - Send message to session
- **Message Format:** Parts array with text type
- **Storage:** localStorage for notes, Chrome sync storage for endpoint config

### Backward Compatibility

The extension maintains backward compatibility:
- Still supports custom API endpoints
- Can be configured to different ports
- Test connection works with any OpenCode instance
- Settings sync across browser profiles
