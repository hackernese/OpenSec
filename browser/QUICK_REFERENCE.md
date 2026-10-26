# Quick Reference - Maps Company Insights → OpenCode

## 🚀 One-Minute Setup

```bash
# 1. Load extension
chrome://extensions/ → Developer mode → Load unpacked → select browser/

# 2. Test API (optional)
Open: file:///home/research/Github/OpenSec/browser/test-api.html

# 3. Configure
Click extension icon → Verify endpoint: http://localhost:4096 → Test → Save

# 4. Use it
Google Maps → Search business → Click "Assess" → Fill form → Submit
```

## 📡 API Calls Made

```javascript
// 1. Create Session
POST http://localhost:4096/session
Body: {"title": "Security Assessment: Business Name"}
Returns: {"id": "session-123"}

// 2. Send Message
POST http://localhost:4096/session/session-123/message
Body: {"parts": [{"type": "text", "text": "# Company's detail..."}]}
```

## 📝 Markdown Format Sent

```markdown
# Company's detail

- name: `Business Name`
- website: `https://business-site.com`
- googleMap: `https://www.google.com/maps/place/...`
- address: `123 Street, City, Country`
- ownerName: `Owner Name`
- email: `owner@email.com`

# Notes

Custom notes and instructions...
```

## 🔧 Files Modified

| File | Change |
|------|--------|
| `content.js` | Use `/session` and `/session/{id}/message` |
| `popup.js` | Test connection with correct API |
| `popup.html` | Update labels for OpenCode |
| `README.md` | Document OpenCode integration |

## 🧪 Quick Test Commands

```bash
# Test create session
curl -X POST http://localhost:4096/session \
  -H 'Content-Type: application/json' \
  -d '{"title": "Test"}'

# Test send message (replace SESSION_ID)
curl -X POST http://localhost:4096/session/SESSION_ID/message \
  -H 'Content-Type: application/json' \
  -d '{"parts":[{"type":"text","text":"Hello"}]}'
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection refused | Start OpenCode on port 4096 |
| 404 Not Found | Check endpoint: `/session` not `/sessions` |
| CORS error | Configure CORS on OpenCode server |
| No button on Maps | Refresh page, check console for errors |
| Test fails | Verify OpenCode is running and accessible |

## 📂 Project Structure

```
browser/
├── content.js           # Main extension logic (API calls here)
├── popup.js            # Configuration UI logic
├── popup.html          # Configuration UI
├── manifest.json       # Extension manifest
├── test-api.html       # API test page
├── README.md           # Overview
├── SETUP.md            # Detailed setup guide
├── API_REFERENCE.md    # Complete API docs
└── QUICK_REFERENCE.md  # This file
```

## 💡 Key Points

- **Default endpoint**: `http://localhost:4096`
- **Two API calls**: Create session → Send message
- **Message format**: Parts array with text type
- **Session title**: `"Security Assessment: {name}"`
- **Storage**: localStorage (notes), Chrome sync (config)

## 🎯 Success Indicators

✅ Extension loads without errors  
✅ Popup shows localhost:4096  
✅ Test connection succeeds  
✅ "Assess" button appears on Maps  
✅ Submission shows success with session ID  
✅ Session appears in OpenCode  

## 🔗 Integration Flow

```
Google Maps Business
       ↓
Extract Info (name, website, address)
       ↓
User Adds (email, owner, notes)
       ↓
POST /session (create session)
       ↓
POST /session/{id}/message (send markdown)
       ↓
OpenCode Session Created
       ↓
ClawSec Processes Message
       ↓
Assessment Workflow Begins
```

## 🎨 Customization Quick Hits

```javascript
// Change endpoint (content.js ~line 402)
return result.apiEndpoint || 'http://localhost:YOUR_PORT';

// Change session title (content.js ~line 250)
title: `Custom Title: ${placeName}`

// Modify markdown (content.js ~line 200-220)
const markdown = [`# Your Format`, ...].join("\n");
```

## 📞 Where to Look

- **Extension not loading**: Check `chrome://extensions/` for errors
- **API not working**: Open `test-api.html` and run tests
- **Button not showing**: Open DevTools console on Google Maps
- **Session not created**: Check Network tab for failed requests
- **OpenCode not responding**: Verify it's running on correct port

## ⚡ Quick Debug

```javascript
// In browser console on Google Maps:
localStorage.getItem('maps-insights-api-endpoint')
// Should return: "http://localhost:4096" or null

// Check if session was saved:
Object.keys(localStorage).filter(k => k.startsWith('maps-insights-note'))
// Shows all saved assessments
```

## 📋 Checklist Before First Use

- [ ] OpenCode running on port 4096
- [ ] Extension loaded in Chrome
- [ ] Test page shows all tests pass
- [ ] Extension popup opens correctly
- [ ] Test connection succeeds
- [ ] Settings saved

## 🎉 You're Ready!

Open Google Maps → Search any business → Click "Assess" → Submit → Check OpenCode!
