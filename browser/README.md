# Maps Company Insights – Chrome Extension

A Chrome extension that injects an **Assess** button into the Google Maps side-panel for businesses, allowing you to quickly send business information to OpenCode for automated security assessments.

## Features

| Feature | Description |
|---|---|
| **Assess button** | Appears next to Directions / Share in the Maps action bar |
| **Business extraction** | Automatically extracts business name, website, address, and Google Maps URL |
| **OpenCode integration** | Sends business data as a new session to OpenCode running on localhost:4096 |
| **Custom notes** | Add owner name, email, and notes before assessment |
| **Persistent storage** | Saves notes per-company in localStorage |

## OpenCode Integration

This extension is designed to work with **OpenCode**, an AI-powered security assessment platform. When you click the "Assess" button on a business in Google Maps:

1. The extension extracts business information (name, website, address, etc.)
2. You can add owner details and notes
3. Clicking "Assess" sends formatted Markdown to OpenCode as a new session
4. OpenCode's ClawSec agent performs an authorized vulnerability assessment

### Expected Markdown Format

The extension generates Markdown in the format expected by ClawSec:

```markdown
# Company's detail

- name: `Business Name`
- website: `https://business-website.com`
- googleMap: `https://www.google.com/maps/place/...`
- address: `123 Business St, City, Country`
- ownerName: `Owner Name`
- email: `owner@email.com`

# Notes

Additional notes or special instructions
```

## How to load in Chrome (unpacked)

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (top-right toggle)
3. Click **Load unpacked**
4. Select the `browser/` folder
5. Click the extension icon to configure the OpenCode endpoint (defaults to `http://localhost:4096`)
6. Navigate to [Google Maps](https://www.google.com/maps) and search for any business
7. The **Assess** button will appear in the action bar

## Configuration

Click the extension icon in Chrome to:
- Set the OpenCode endpoint URL (default: `http://localhost:4096`)
- Test the connection to OpenCode
- Save settings across all Maps tabs

## File structure

```
browser/
├── manifest.json   # Extension manifest (MV3)
├── content.js      # DOM injection + modal logic + OpenCode API calls
├── popup.js        # Extension popup configuration UI
├── popup.html      # Configuration popup interface
├── popup.css       # Popup styles
├── styles.css      # Button + modal styles
├── icons/
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md
```

## Customizing

- To change the default OpenCode endpoint, update the default value in `content.js` `getApiEndpoint()` function
- To modify the Markdown format, edit the markdown generation in `content.js` `onInsightsClick()` handler
- To change button styling, update `styles.css`
- Notes are stored under the key `maps-insights-note::<place name>` in `localStorage`

## Requirements

- Chrome/Chromium browser with extension support
- OpenCode running on localhost:4096 (or custom endpoint)
- ClawSec agent configured in OpenCode
