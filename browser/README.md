# Maps Company Insights – Chrome Extension

A lightweight Chrome extension that injects an **Insights** button into the
Google Maps side-panel whenever a business or place is displayed.

## Features

| Feature | Description |
|---|---|
| **Insights button** | Appears next to Directions / Share in the Maps action bar |
| **Quick actions** | One-click links to Google Search, LinkedIn, and Google News |
| **Copy name** | Copies the company name to the clipboard |
| **Notes** | Write and save per-company notes (stored in `localStorage`) |

## How to load in Chrome (unpacked)

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (top-right toggle)
3. Click **Load unpacked**
4. Select this `extension/` folder
5. Navigate to [Google Maps](https://www.google.com/maps) and search for any
   business — the **Insights** button will appear in the action bar

## File structure

```
extension/
├── manifest.json   # Extension manifest (MV3)
├── content.js      # DOM injection + modal logic
├── styles.css      # Button + modal styles
├── icons/
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md
```

## Customising

- To add more quick-action links, edit the `urls` map inside `handleQuickAction()` in `content.js`.
- To change the button colour, update the `color` property on `#maps-insights-btn` in `styles.css`.
- Notes are stored under the key `maps-insights-note::<place name>` in `localStorage`.
