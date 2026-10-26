# API Reference - OpenCode Integration

## Overview

The Maps Company Insights extension communicates with OpenCode via REST API to create new sessions and send assessment messages.

## API Workflow

1. **Create a session** - Creates a new session and returns a session ID
2. **Send a message** - Sends the business assessment content to the session

## Endpoints

### 1. Create Session

Creates a new OpenCode session.

```
POST http://localhost:4096/session
```

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Security Assessment: Business Name"
}
```

**Response (200 OK):**
```json
{
  "id": "abc123-def456-ghi789",
  "title": "Security Assessment: Business Name",
  "createdAt": "2026-10-26T10:30:00.000Z"
}
```

### 2. Send Message

Sends a message to an existing session.

```
POST http://localhost:4096/session/{sessionId}/message
```

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "parts": [
    {
      "type": "text",
      "text": "# Company's detail\n\n- name: `Business Name`\n- website: `https://example.com`\n- googleMap: `https://www.google.com/maps/place/...`\n- address: `123 Main St`\n- ownerName: `John Doe`\n- email: `owner@example.com`\n\n# Notes\n\nCustom assessment notes..."
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "id": "message-id",
  "sessionId": "abc123-def456-ghi789",
  "status": "sent"
}
```

## Complete Flow Example (cURL)

```bash
# Step 1: Create a session
curl -X POST http://localhost:4096/session \
  -H 'Content-Type: application/json' \
  -d '{"title": "Security Assessment: ACME Corp"}'

# Returns: {"id": "session-123", "title": "...", ...}

# Step 2: Send the assessment message
curl -X POST http://localhost:4096/session/session-123/message \
  -H 'Content-Type: application/json' \
  -d '{
    "parts": [
      {
        "type": "text",
        "text": "# Company'\''s detail\n\n- name: `ACME Corp`\n- website: `https://acme.com`\n..."
      }
    ]
  }'
```

## JavaScript/Fetch Examples

### Complete Flow with Fetch API

```javascript
async function sendBusinessAssessment(businessData) {
  const baseUrl = 'http://localhost:4096';
  
  // Build the markdown message
  const markdown = `# Company's detail

- name: \`${businessData.name}\`
- website: \`${businessData.website}\`
- googleMap: \`${businessData.googleMapUrl}\`
- address: \`${businessData.address}\`
- ownerName: \`${businessData.ownerName}\`
- email: \`${businessData.email}\`

# Notes

${businessData.notes}`;

  try {
    // Step 1: Create a new session
    const createResponse = await fetch(`${baseUrl}/session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        title: `Security Assessment: ${businessData.name}`
      })
    });

    if (!createResponse.ok) {
      throw new Error(`Failed to create session: ${createResponse.status}`);
    }

    const sessionData = await createResponse.json();
    const sessionId = sessionData.id;

    console.log('Created session:', sessionId);

    // Step 2: Send the markdown message
    const messageResponse = await fetch(`${baseUrl}/session/${sessionId}/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        parts: [
          {
            type: 'text',
            text: markdown
          }
        ]
      })
    });

    if (!messageResponse.ok) {
      throw new Error(`Failed to send message: ${messageResponse.status}`);
    }

    console.log('Message sent to session:', sessionId);
    return sessionId;

  } catch (error) {
    console.error('Error sending assessment:', error);
    throw error;
  }
}

// Usage
await sendBusinessAssessment({
  name: 'ACME Corporation',
  website: 'https://acme.com',
  googleMapUrl: 'https://www.google.com/maps/place/ACME/@-33.8688,151.2093',
  address: '123 Business St, Sydney NSW 2000',
  ownerName: 'John Smith',
  email: 'john@acme.com',
  notes: 'Please focus on web application security'
});
```

### Using Async/Await with Error Handling

```javascript
async function createSessionAndSendMessage(title, messageText) {
  const baseUrl = 'http://localhost:4096';
  
  try {
    // Create session
    const createRes = await fetch(`${baseUrl}/session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title })
    });
    
    if (!createRes.ok) {
      const errorText = await createRes.text();
      throw new Error(`Create session failed: ${createRes.status} - ${errorText}`);
    }
    
    const { id: sessionId } = await createRes.json();
    
    // Send message
    const messageRes = await fetch(`${baseUrl}/session/${sessionId}/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        parts: [{ type: 'text', text: messageText }]
      })
    });
    
    if (!messageRes.ok) {
      const errorText = await messageRes.text();
      throw new Error(`Send message failed: ${messageRes.status} - ${errorText}`);
    }
    
    return { sessionId, success: true };
    
  } catch (error) {
    console.error('OpenCode API Error:', error);
    return { success: false, error: error.message };
  }
}
```

### Using Promises

```javascript
function sendToOpenCode(businessInfo) {
  const baseUrl = 'http://localhost:4096';
  const markdown = generateMarkdown(businessInfo);
  
  return fetch(`${baseUrl}/session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: `Assessment: ${businessInfo.name}` })
  })
  .then(res => {
    if (!res.ok) throw new Error('Failed to create session');
    return res.json();
  })
  .then(data => {
    const sessionId = data.id;
    return fetch(`${baseUrl}/session/${sessionId}/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        parts: [{ type: 'text', text: markdown }]
      })
    })
    .then(res => {
      if (!res.ok) throw new Error('Failed to send message');
      return sessionId;
    });
  })
  .catch(error => {
    console.error('Error:', error);
    throw error;
  });
}
```

## Request Field Details

### Create Session Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Session title (shown in OpenCode UI) |

### Send Message Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `parts` | array | Yes | Array of message parts |
| `parts[].type` | string | Yes | Part type (use "text") |
| `parts[].text` | string | Yes | The message content (Markdown) |

## Message Format for ClawSec

The `text` field should contain Markdown in this format:

```markdown
# Company's detail

- name: `Business Name`
- website: `https://company-website.com`
- googleMap: `https://www.google.com/maps/place/NAME/@coordinates`
- address: `Street, City, Country`
- ownerName: `Owner's Name`
- email: `owner@email.com`

# Notes

Any additional context, special instructions, or requirements for the assessment.
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Bad Request",
  "message": "Invalid request format"
}
```

### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "Session not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "An error occurred"
}
```

## CORS Considerations

If running the browser extension, CORS must be configured on OpenCode to allow browser requests:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

## Debugging

### Check Connection

```bash
# Test if OpenCode is running
curl http://localhost:4096/session -X POST \
  -H 'Content-Type: application/json' \
  -d '{"title": "Test"}'
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Connection refused | OpenCode not running | Start OpenCode on port 4096 |
| 404 Not Found | Wrong endpoint | Check URL: `/session` not `/sessions` |
| CORS error | Browser blocking request | Configure CORS on OpenCode |
| Session ID null | API response changed | Check response structure |

## Extension Implementation

The browser extension uses this exact flow:

1. User clicks "Assess" button on Google Maps
2. Extension extracts business information
3. Creates session with title: `"Security Assessment: {business name}"`
4. Sends markdown message with business details
5. Stores session ID in localStorage
6. Shows success notification with session ID

## Version Compatibility

- **Extension Version**: 1.0.0
- **OpenCode API**: Port 4096
- **Required Endpoints**: 
  - `POST /session`
  - `POST /session/{id}/message`
