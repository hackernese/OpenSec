# Setup Guide - Maps Company Insights → OpenCode

This guide will help you set up the browser extension to work with OpenCode for automated security assessments.

## Prerequisites

- **OpenCode** running on port 4096 (or your preferred port)
- **Chrome/Chromium** browser
- **ClawSec agent** configured in OpenCode (from `/home/research/Github/Thesis/OpenCode/AGENTS.md`)

## Step 1: Install the Extension

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable **Developer mode** (toggle in top-right corner)
3. Click **Load unpacked**
4. Select the `/home/research/Github/OpenSec/browser` folder
5. The extension should now appear in your extensions list

## Step 2: Configure OpenCode Endpoint

1. Click the extension icon in Chrome toolbar
2. The default endpoint should be pre-filled: `http://localhost:4096`
3. If you're running OpenCode on a different port, update the URL
4. Click **Test Connection** to verify OpenCode is running and responding
5. Click **Save Settings** to persist the configuration

## Step 3: Use the Extension

1. Navigate to [Google Maps](https://www.google.com/maps)
2. Search for any business (e.g., a restaurant, shop, or company)
3. When the business details panel opens, you'll see an **Assess** button next to "Directions" and "Share"
4. Click the **Assess** button
5. A modal will open with the business information auto-filled:
   - Business name
   - Website (if available)
   - Google Maps URL
   - Address
6. Fill in optional fields:
   - **Email Address**: Where the final report will be sent
   - **Owner Name**: Person requesting the assessment
   - **Notes**: Any special instructions or context
7. Click **Assess** to send the data to OpenCode

## Step 4: What Happens Next

Once you click "Assess", the extension:

1. Generates a Markdown document with business details
2. Creates a new session in OpenCode via POST `/session`
3. Sends the markdown message to that session via POST `/session/{id}/message`
4. Shows a success toast with the session ID
5. Saves your notes locally for future reference

## Step 5: OpenCode Processing

In OpenCode, ClawSec will:

1. **INTAKE**: Receive the business information
2. **AUTHORIZATION**: Check if the business website has the authorization header
3. **ENUMERATION**: Discover all assets belonging to the business
4. **ASSESSMENT**: Perform vulnerability scanning across all assets
5. **VALIDATION**: Confirm and document findings
6. **REPORTING**: Generate a comprehensive security report
7. **COMPLETE**: Send the final report to the provided email

## Troubleshooting

### Extension doesn't appear on Google Maps
- Make sure you're on a business detail page (not just search results)
- Check that the extension is enabled in `chrome://extensions/`
- Refresh the Google Maps page

### "OpenCode endpoint not configured" error
- Open the extension popup and configure the endpoint
- Make sure OpenCode is actually running on the specified port
- Test the connection using the "Test Connection" button

### Connection failed / timeout
- Verify OpenCode is running and check the correct endpoints exist:
  - `POST http://localhost:4096/session` (create session)
  - `POST http://localhost:4096/session/{id}/message` (send message)
- Check firewall settings aren't blocking local connections
- Try restarting OpenCode

### Session created but no assessment starts
- Check OpenCode logs for errors
- Verify ClawSec agent is properly configured in OpenCode
- Make sure the business website has proper authorization headers (see AGENTS.md)

## API Endpoint Details

The extension makes two API calls to OpenCode:

**1. Create Session:**
```javascript
POST http://localhost:4096/session
Content-Type: application/json

{
  "title": "Security Assessment: <business name>"
}
```

**2. Send Message:**
```javascript
POST http://localhost:4096/session/<sessionId>/message
Content-Type: application/json

{
  "parts": [
    {
      "type": "text",
      "text": "<markdown content with business details>"
    }
  ]
}
```

## Security Notes

- The extension only sends data when you explicitly click "Assess"
- Notes are stored locally in your browser's localStorage
- No data is sent to third parties
- All communication is with your local OpenCode instance
- Make sure to only assess businesses you have permission to test

## Advanced Configuration

### Change Default Port

Edit `content.js` and update the default value in `getApiEndpoint()`:

```javascript
return result.apiEndpoint || 'http://localhost:YOUR_PORT';
```

### Customize Markdown Format

Edit the markdown generation section in `content.js` around line 200-220:

```javascript
const markdown = [
  `# Company's detail`,
  // ... customize fields here
].join("\n");
```

### Enable Debug Logging

Open the browser console (F12) when on Google Maps. The extension logs:
- Session creation
- Message sending
- Session IDs
- Error details

Look for logs prefixed with `📋 Created session:` and `✅ Message sent to session:` to verify the flow.
