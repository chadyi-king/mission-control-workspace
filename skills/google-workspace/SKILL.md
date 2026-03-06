# google-workspace

Use the Google Workspace CLI (`gws`) to interact with Gmail, Drive, Calendar, Docs, and Sheets.

## Description

The Google Workspace CLI provides command-line access to Google Workspace services including Gmail, Google Drive, Google Calendar, Google Docs, and Google Sheets. This skill enables agents to read emails, manage files, create calendar events, and work with documents programmatically.

## Installation

### Prerequisites

1. **Node.js 16+** must be installed
2. **Google Cloud Project** with Workspace APIs enabled
3. **OAuth 2.0 credentials** configured

### Install CLI

```bash
# Install via npm
npm install -g @googleworkspace/cli

# Verify installation
gws --version
```

### Authentication Setup

**Step 1: Create Google Cloud Project**
1. Go to https://console.cloud.google.com/
2. Create new project or select existing
3. Enable APIs:
   - Gmail API
   - Google Drive API
   - Google Calendar API
   - Google Docs API
   - Google Sheets API

**Step 2: Configure OAuth Consent Screen**
1. APIs & Services → OAuth consent screen
2. Select "External" (or Internal if G Suite)
3. Fill in app name, user support email, developer contact
4. Add scopes:
   - `https://www.googleapis.com/auth/gmail.modify`
   - `https://www.googleapis.com/auth/drive`
   - `https://www.googleapis.com/auth/calendar`
   - `https://www.googleapis.com/auth/documents`
   - `https://www.googleapis.com/auth/spreadsheets`
5. Add test users (your email)

**Step 3: Create OAuth Credentials**
1. APIs & Services → Credentials
2. Create Credentials → OAuth client ID
3. Application type: "Desktop app"
4. Download JSON (save as `client_secret.json`)

**Step 4: Authenticate CLI**
```bash
# Set credentials path
export GWS_CREDENTIALS="/path/to/client_secret.json"

# Login (opens browser)
gws auth login

# Verify
gws auth status
```

## Configuration

Store credentials path in environment:

```bash
# Add to ~/.bashrc or ~/.zshrc
export GWS_CREDENTIALS="$HOME/.config/googleworkspace/client_secret.json"
```

## Usage

### Gmail

**List recent emails:**
```bash
# List last 10 emails
gws gmail list --limit 10

# List unread emails
gws gmail list --label UNREAD

# List from specific sender
gws gmail list --from "sender@example.com"

# Output as JSON
gws gmail list --limit 5 --json
```

**Read email:**
```bash
# Read by ID (get ID from list command)
gws gmail get MESSAGE_ID

# Read and output raw
gws gmail get MESSAGE_ID --raw
```

**Send email:**
```bash
# Simple email
gws gmail send --to "recipient@example.com" --subject "Hello" --body "Message text"

# With HTML body
gws gmail send --to "recipient@example.com" --subject "Hello" --body "<h1>HTML</h1>" --html

# With attachment
gws gmail send --to "recipient@example.com" --subject "File" --body "See attached" --attach "/path/to/file.pdf"
```

**Manage labels:**
```bash
# List labels
gws gmail labels list

# Add label to message
gws gmail labels add MESSAGE_ID "Label Name"

# Archive (remove inbox label)
gws gmail archive MESSAGE_ID
```

### Google Drive

**List files:**
```bash
# List files in My Drive
gws drive list

# List files in specific folder
gws drive list --folder "FOLDER_ID"

# Search files
gws drive list --query "name contains 'report'"

# List with details
gws drive list --details
```

**Upload file:**
```bash
# Upload to root
gws drive upload "/path/to/local/file.pdf"

# Upload to specific folder
gws drive upload "/path/to/file.pdf" --folder "FOLDER_ID"

# Upload with custom name
gws drive upload "/path/to/file.pdf" --name "Custom Name.pdf"
```

**Download file:**
```bash
# Download by file ID
gws drive download "FILE_ID" --output "/path/to/save/"

# Download by name (searches Drive)
gws drive download --name "document.pdf" --output "/path/to/save/"
```

**Create folder:**
```bash
gws drive folder create "New Folder Name"

# Create in specific parent folder
gws drive folder create "Subfolder" --parent "PARENT_FOLDER_ID"
```

### Google Calendar

**List calendars:**
```bash
gws calendar list
```

**List events:**
```bash
# Today's events
gws calendar events list

# Specific date range
gws calendar events list --start "2026-03-01" --end "2026-03-07"

# Specific calendar
gws calendar events list --calendar "Calendar Name"
```

**Create event:**
```bash
# Simple event
gws calendar events create "Meeting Title" --start "2026-03-10T14:00:00" --end "2026-03-10T15:00:00"

# With attendees
gws calendar events create "Team Meeting" --start "2026-03-10T14:00:00" --end "2026-03-10T15:00:00" --attendees "person1@example.com,person2@example.com"

# With description and location
gws calendar events create "Project Review" --start "2026-03-10T14:00:00" --end "2026-03-10T15:00:00" --description "Review Q1 progress" --location "Conference Room A"
```

### Google Docs

**Create document:**
```bash
# Blank document
gws docs create "Document Title"

# From template
gws docs create "Project Proposal" --template "TEMPLATE_ID"
```

**Get document content:**
```bash
# Export as text
gws docs get "DOCUMENT_ID" --format text

# Export as HTML
gws docs get "DOCUMENT_ID" --format html

# Export as PDF
gws docs get "DOCUMENT_ID" --format pdf --output "/path/to/save.pdf"
```

**Append text:**
```bash
gws docs append "DOCUMENT_ID" --text "New content to add at end"
```

### Google Sheets

**Create spreadsheet:**
```bash
gws sheets create "Spreadsheet Name"
```

**Read data:**
```bash
# Read entire sheet
gws sheets get "SPREADSHEET_ID"

# Read specific range
gws sheets get "SPREADSHEET_ID" --range "Sheet1!A1:D10"

# Output as CSV
gws sheets get "SPREADSHEET_ID" --range "Sheet1!A1:D10" --csv
```

**Write data:**
```bash
# Update range with values
gws sheets update "SPREADSHEET_ID" --range "Sheet1!A1" --values "Value1,Value2,Value3"

# Update multiple rows
gws sheets update "SPREADSHEET_ID" --range "Sheet1!A1:C2" --values "A1,B1,C1|A2,B2,C2"
```

**Append rows:**
```bash
gws sheets append "SPREADSHEET_ID" --sheet "Sheet1" --values "New,Row,Data"
```

## Examples

### Daily Email Summary

```bash
# Get unread emails from today
gws gmail list --label UNREAD --after "$(date +%Y/%m/%d)" --json | jq '.[] | {from: .from, subject: .subject}'
```

### Backup Important Files

```bash
# Download specific folder
gws drive list --folder "IMPORTANT_FOLDER_ID" | while read file_id file_name; do
  gws drive download "$file_id" --output "/backup/location/"
done
```

### Create Meeting Notes

```bash
# Create doc for meeting
gws docs create "Meeting Notes - $(date +%Y-%m-%d)"

# Add attendees from calendar event
gws calendar events get "EVENT_ID" --json | jq '.attendees[].email'
```

### Track Tasks in Sheets

```bash
# Add task to tracking sheet
gws sheets append "TASKS_SHEET_ID" --sheet "Tasks" --values "$(date +%Y-%m-%d),New Task,Pending,High"
```

## Authentication Issues

**Token expired:**
```bash
# Re-authenticate
gws auth login
```

**Permission denied:**
- Check OAuth scopes include required APIs
- Verify user is added as test user in OAuth consent screen
- Try `gws auth revoke` then `gws auth login`

## Rate Limits

Google Workspace APIs have rate limits:
- Gmail: 1 billion quota units per day
- Drive: 1 billion quota units per day
- Calendar: 1 million requests per day

If you hit limits:
- Add delays between requests
- Use batch operations where available
- Request quota increase in Google Cloud Console

## Security Notes

- OAuth tokens stored in `~/.googleworkspace/`
- Never commit credentials to version control
- Use environment variables for sensitive paths
- Revoke access with `gws auth revoke` if needed

## Troubleshooting

**"Command not found":**
```bash
# Check npm global bin is in PATH
which gws || npm bin -g
# Add to PATH if needed: export PATH="$PATH:$(npm bin -g)"
```

**"Authentication required":**
- Run `gws auth login`
- Check `GWS_CREDENTIALS` environment variable
- Verify client_secret.json exists and is valid

**"API not enabled":**
- Go to Google Cloud Console
- Enable the specific API (Gmail, Drive, etc.)
- Wait 5-10 minutes for propagation

## See Also

- [Google Workspace CLI GitHub](https://github.com/googleworkspace/cli)
- [Google API Documentation](https://developers.google.com/workspace)
- [OAuth 2.0 Setup Guide](https://developers.google.com/identity/protocols/oauth2)
