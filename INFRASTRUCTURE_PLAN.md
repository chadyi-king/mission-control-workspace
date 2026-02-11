# INFRASTRUCTURE PROJECTS TECHNICAL PLAN
## Real-Time Dashboard + Full Computer Control

**Date:** 2026-02-11  
**Prepared for:** OpenClaw Infrastructure Upgrade  
**Status:** Planning Phase

---

# PROJECT 1: REAL-TIME DASHBOARD WITH WEBSOCKETS

## Current State Analysis

```
┌─────────────────────────────────────────────────────────────┐
│                    CURRENT ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────┐      ┌──────────────┐      ┌────────────┐  │
│   │  GitHub  │──────│ GitHub Pages │──────│  Static    │  │
│   │  Repo    │      │   (Free)     │      │  Website   │  │
│   └──────────┘      └──────────────┘      └────────────┘  │
│        │                                           │       │
│        │         data.json (loaded once)           │       │
│        │◄──────────────────────────────────────────┤       │
│        │              On page load only            │       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Problem:** Data updates require manual page refresh. No real-time capability.

---

## 1. WebSocket Architecture Overview

### What Are WebSockets?
WebSockets provide a **full-duplex, persistent TCP connection** between client and server over a single, long-lived connection. After an initial HTTP handshake, the connection upgrades to the WebSocket protocol (`ws://` or `wss://`).

```
┌─────────────────────────────────────────────────────────────┐
│                 WEBSOCKET HANDSHAKE FLOW                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Client                              Server                 │
│    │                                    │                   │
│    │───── HTTP GET with Upgrade header ─►│                   │
│    │     Connection: Upgrade            │                   │
│    │     Upgrade: websocket             │                   │
│    │                                    │                   │
│    │◄───────── 101 Switching Protocols ─│                   │
│    │                                    │                   │
│    │◄═══════════════════════════════════►│                   │
│    │      PERSISTENT WEBSOCKET           │                   │
│    │      CONNECTION ESTABLISHED         │                   │
│    │      (Full-duplex, low latency)     │                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Key Characteristics:**
- **Bidirectional:** Both client and server can send messages anytime
- **Low latency:** No HTTP overhead after handshake
- **Persistent:** Single connection stays open
- **Binary + UTF-8:** Can send any data format

---

## 2. Hosting Options Comparison

### Option A: Render (Recommended for Beginners)

| Feature | Free Tier | Paid (Starter $7/mo) |
|---------|-----------|----------------------|
| **WebSocket Support** | ✅ Yes | ✅ Yes |
| **Uptime** | Spins down after 15 min idle | Always on |
| **Bandwidth** | 100 GB/month | 100 GB/month |
| **Build Pipeline** | 500 min/month | Unlimited |
| **Custom Domains** | ✅ Yes | ✅ Yes |
| **Auto-deploy** | ✅ Git push | ✅ Git push |
| **SSL/HTTPS** | ✅ Automatic | ✅ Automatic |

**Pros:**
- Native WebSocket support
- Simple Git-based deployment
- Free tier for testing
- Built-in log streaming

**Cons:**
- Free tier spins down (cold start ~30 seconds)
- Ephemeral filesystem (data lost on restart)

---

### Option B: Railway

| Feature | Free Trial | Hobby ($5+/mo) |
|---------|------------|----------------|
| **WebSocket Support** | ✅ Yes | ✅ Yes |
| **Uptime** | 24/7 during trial | Always on |
| **Compute** | 1 vCPU / 0.5 GB RAM | Up to 48 vCPU/GB |
| **Storage** | 0.5 GB volume | Up to 5 GB |
| **Pricing Model** | Usage-based | Usage-based |
| **Auto-deploy** | ✅ Git push | ✅ Git push |

**Pros:**
- Generous free trial ($5 credits for 30 days)
- Excellent developer experience
- Automatic HTTPS
- Private networking

**Cons:**
- Free plan limited to $1/month after trial
- More complex pricing calculations

---

### Option C: Cloudflare Workers + Durable Objects

| Feature | Free Tier | Paid ($5+/mo) |
|---------|-----------|---------------|
| **WebSocket Support** | ✅ Durable Objects | ✅ Durable Objects |
| **Requests** | 100K/day | 10M/month + $0.30/M |
| **CPU Time** | 10ms/invocation | 30M ms included |
| **Durable Objects** | 100K req/day | 1M req/month |
| **Latency** | <50ms global | <50ms global |
| **Auto-deploy** | ✅ Wrangler CLI/Git | ✅ Wrangler CLI/Git |

**Pros:**
- Edge deployment (330+ cities)
- Excellent for WebSockets (Durable Objects)
- Massive scale potential
- Very low latency globally

**Cons:**
- Steeper learning curve
- Requires Durable Objects for WebSocket state
- Different programming model (event-driven)

---

### Option D: VPS (DigitalOcean, Linode, Hetzner)

| Provider | Price | Specs |
|----------|-------|-------|
| **DigitalOcean** | $6/mo | 1 GB RAM, 1 vCPU, 25 GB SSD |
| **Linode** | $5/mo | 1 GB RAM, 1 vCPU, 25 GB SSD |
| **Hetzner** | €4.51/mo | 2 GB RAM, 1 vCPU, 20 GB SSD |
| **AWS Lightsail** | $5/mo | 512 MB RAM, 1 vCPU, 20 GB SSD |

**Pros:**
- Full control
- Always on
- Predictable pricing
- Can run multiple services

**Cons:**
- Requires server management
- Manual SSL setup
- Security responsibility on you

---

## 3. Implementation Approaches

### OPTION A: WebSocket Server (Full Real-Time)

```
┌─────────────────────────────────────────────────────────────────┐
│              WEBSOCKET ARCHITECTURE (OPTION A)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────┐      ┌──────────────────┐      ┌────────────┐   │
│   │  GitHub  │──────│   Render/Railway  │──────│  Static    │   │
│   │  Repo    │      │  WebSocket Server │      │  Frontend  │   │
│   └──────────┘      └──────────────────┘      └────────────┘   │
│                            │                           │       │
│                            │    WebSocket (wss://)    │       │
│                            │◄────────────────────────►│       │
│                            │                          │       │
│                            │  ┌────────────────┐      │       │
│                            └──┤  File Watch    │      │       │
│                               │  or Database   │      │       │
│                               └────────────────┘      │       │
│                                                                 │
│   FLOW:                                                         │
│   1. Server watches data.json for changes                       │
│   2. On change, broadcasts to all connected clients             │
│   3. Client receives update instantly (<100ms)                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Tech Stack:**
- **Server:** Node.js + Socket.IO or ws library
- **File Watching:** chokidar (Node.js)
- **Frontend:** Native WebSocket API or Socket.IO client

**Code Example (Server):**
```javascript
const WebSocket = require('ws');
const chokidar = require('chokidar');
const fs = require('fs');

const wss = new WebSocket.Server({ port: 8080 });

// Watch data.json for changes
chokidar.watch('data.json').on('change', async () => {
  const data = await fs.promises.readFile('data.json', 'utf8');
  const parsed = JSON.parse(data);
  
  // Broadcast to all clients
  wss.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify({ type: 'update', data: parsed }));
    }
  });
});
```

**Pros:**
- True real-time (<100ms updates)
- Efficient (only sends when data changes)
- Scalable with proper architecture

**Cons:**
- Requires persistent server
- More complex to implement
- Need reconnection logic

---

### OPTION B: Server-Sent Events (SSE) - RECOMMENDED

```
┌─────────────────────────────────────────────────────────────────┐
│            SERVER-SENT EVENTS ARCHITECTURE (OPTION B)           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────┐      ┌──────────────────┐      ┌────────────┐   │
│   │  GitHub  │──────│   Render/Railway  │──────│  Static    │   │
│   │  Repo    │      │    HTTP Server    │      │  Frontend  │   │
│   └──────────┘      └──────────────────┘      └────────────┘   │
│                            │                           │       │
│                            │    HTTP Stream (SSE)     │       │
│                            │◄─────────────────────────│       │
│                            │   text/event-stream      │       │
│                            │                          │       │
│   FLOW:                                                    │   │
│   1. Client connects to /events endpoint                    │   │
│   2. Server keeps connection open                           │   │
│   3. Server sends events as they occur                      │   │
│   4. Auto-reconnect built into browser                      │   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Tech Stack:**
- **Server:** Node.js + Express + express-sse
- **Frontend:** Native EventSource API

**Code Example (Server):**
```javascript
const express = require('express');
const SSE = require('express-sse');
const chokidar = require('chokidar');

const app = express();
const sse = new SSE();

// SSE endpoint
app.get('/events', sse.init);

// Watch file and broadcast changes
chokidar.watch('data.json').on('change', async () => {
  const data = await fs.promises.readFile('data.json', 'utf8');
  sse.send(JSON.parse(data), 'data-update');
});

app.listen(3000);
```

**Code Example (Client):**
```javascript
const evtSource = new EventSource('/events');

evtSource.addEventListener('data-update', (e) => {
  const data = JSON.parse(e.data);
  updateDashboard(data);
});

// Auto-reconnect is built-in!
```

**Pros:**
- Simpler than WebSockets (uses HTTP)
- Auto-reconnect built-in
- Works through most corporate firewalls
- No special libraries needed

**Cons:**
- One-way only (server → client)
- UTF-8 only (no binary)
- 6 connection limit per browser

**Why SSE for this use case?**
- You only need server → client updates
- Simpler implementation
- No reconnection logic needed
- Works better with Render/Railway free tiers

---

### OPTION C: Smart Polling with Diff Detection

```
┌─────────────────────────────────────────────────────────────────┐
│              SMART POLLING ARCHITECTURE (OPTION C)              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────┐      ┌──────────────────┐      ┌────────────┐   │
│   │  GitHub  │──────│  Any Static Host  │──────│  Static    │   │
│   │  Repo    │      │ (GitHub Pages/etc)│      │  Frontend  │   │
│   └──────────┘      └──────────────────┘      └────────────┘   │
│         │                                            │          │
│         │                                            │          │
│         │         data.json + etag/last-modified    │          │
│         │◄───────────────────────────────────────────│          │
│         │              Every 30 seconds              │          │
│                                                                 │
│   FLOW:                                                         │
│   1. Client polls every 30 seconds                              │
│   2. Server returns 304 if unchanged (no bandwidth)             │
│   3. Client compares content with previous                      │
│   4. Only updates DOM if data actually changed                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Code Example (Client):**
```javascript
let lastData = null;
let lastEtag = null;

async function poll() {
  const headers = lastEtag ? { 'If-None-Match': lastEtag } : {};
  const res = await fetch('/data.json', { headers });
  
  if (res.status === 304) return; // Not modified
  
  const data = await res.json();
  const etag = res.headers.get('ETag');
  
  if (JSON.stringify(data) !== JSON.stringify(lastData)) {
    updateDashboard(data);
    lastData = data;
    lastEtag = etag;
  }
}

setInterval(poll, 30000); // 30 second polling
```

**Pros:**
- Works with static hosting (GitHub Pages)
- Very simple to implement
- No server needed
- Uses HTTP caching efficiently

**Cons:**
- 30-second delay maximum
- Still uses polling (inefficient)
- No true real-time

---

## 4. Database vs File-Based Storage

### Current: File-Based (data.json)

```
┌────────────────────┐
│    data.json       │
│  (Git repository)  │
└────────────────────┘
```

**Pros:**
- Simple to edit
- Version controlled
- No database to manage

**Cons:**
- Not suitable for concurrent writes
- Must read entire file to get data
- No query capabilities

---

### Recommended: SQLite (Server-Side)

```
┌─────────────────────────────────────────┐
│         SQLite Database                 │
│  ┌─────────────────────────────────┐   │
│  │  dashboard_data                 │   │
│  │  ─────────────                  │   │
│  │  id | key | value | updated_at  │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  update_log                     │   │
│  │  ─────────                      │   │
│  │  id | change | timestamp        │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

**Migration Strategy:**
1. Keep data.json as source of truth initially
2. Create admin API to update database
3. Eventually migrate completely to DB

**Why SQLite for this use case:**
- Serverless (just a file)
- Zero configuration
- Perfect for read-heavy workloads
- Can still edit directly if needed
- Render/Railway have persistent storage options

---

### Alternative: Key-Value Store

| Service | Type | Pricing |
|---------|------|---------|
| **Upstash Redis** | Managed Redis | Free tier: 10K commands/day |
| **Cloudflare KV** | Edge KV | Free: 100K reads/day |
| **Render Key Value** | Redis-compatible | Free tier (in-memory only) |

---

## 5. Auto-Deployment Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    CI/CD PIPELINE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────┐ │
│   │  Push to │───►│  GitHub  │───►│  Render  │───►│  Live  │ │
│   │  main    │    │ Actions  │    │  Deploy  │    │  Site  │ │
│   └──────────┘    └──────────┘    └──────────┘    └────────┘ │
│        │                               │                       │
│        │    Optional: Run tests        │                       │
│        │    - Validate JSON            │                       │
│        │    - Check dashboard          │                       │
│        │      renders correctly        │                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### GitHub Actions Workflow
```yaml
name: Deploy Dashboard

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Validate JSON
        run: |
          python -m json.tool data.json > /dev/null
          
      - name: Deploy to Render
        uses: johnbeynon/render-deploy-action@v0.0.8
        with:
          service-id: ${{ secrets.RENDER_SERVICE_ID }}
          api-key: ${{ secrets.RENDER_API_KEY }}
```

### Render Deploy Configuration (render.yaml)
```yaml
services:
  - type: web
    name: dashboard-server
    runtime: node
    buildCommand: npm install
    startCommand: node server.js
    envVars:
      - key: NODE_ENV
        value: production
```

---

## PROJECT 1: RECOMMENDED IMPLEMENTATION

### Phase 1: Quick Win (Smart Polling) - 2 hours
1. Implement Option C (Smart Polling) on current GitHub Pages
2. 30-second polling with ETag support
3. Immediate improvement with zero infrastructure change

### Phase 2: Real-Time (SSE) - 4-6 hours
1. Deploy to Render free tier
2. Implement SSE server with file watching
3. Update frontend to use EventSource
4. Keep GitHub Pages as backup

### Phase 3: Enhanced (WebSocket + SQLite) - 1-2 days
1. Migrate to SQLite database
2. Implement proper WebSocket server
3. Add admin panel for data updates
4. Move to paid Render tier for reliability

---

# PROJECT 2: FULL COMPUTER CONTROL (VNC/RDP)

## Current State Analysis

```
┌─────────────────────────────────────────────────────────────┐
│                    CURRENT STATE                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────────┐      ┌──────────────┐                   │
│   │   OpenClaw   │──────│   Chrome     │                   │
│   │   (You)      │      │  Extension   │                   │
│   └──────────────┘      └──────────────┘                   │
│                                │                            │
│                                │ Limited to:                │
│                                │ - Browser tabs             │
│                                │ - Page content             │
│                                │ - Cannot see desktop       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Goal:** Full screen view + mouse/keyboard control

---

## 1. VNC Server Options Comparison

### Option A: RustDesk (RECOMMENDED)

```
┌─────────────────────────────────────────────────────────────┐
│                    RUSTDESK ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────┐         ┌──────────────┐        ┌────────┐  │
│   │ OpenClaw │◄───────►│  Relay Server │◄──────►│  You   │  │
│   │  (WSL2)  │         │  (Self-hosted)│        │(Client)│  │
│   └──────────┘         └──────────────┘        └────────┘  │
│        │                                                    │
│        │  Direct connection (if on same network)           │
│        │◄─────────────────────────────────────────────────►│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- **Open source** (AGPLv3)
- **Self-hosted relay server** available
- **End-to-end encryption** (RustDesk uses own encryption)
- **Cross-platform** (Windows, Linux, macOS)
- **No port forwarding required** (uses relay)
- **File transfer** built-in

**Security:**
- Client-side encryption
- Password + permanent password options
- 2FA support
- Audit logs (with self-hosted server)

**Pricing:**
- **Free** for personal use
- Self-hosted: **Free** (you run the server)
- Pro: $9.90/month for commercial use

**Pros:**
- Modern, actively maintained
- Easy setup
- Works through NAT/firewalls
- No cloud dependency (fully self-hosted option)

**Cons:**
- Relatively new project
- Self-hosted server requires Docker

---

### Option B: TigerVNC

**Features:**
- Open source (GPL)
- High performance
- Cross-platform
- Traditional VNC protocol

**Security:**
- TLS encryption (optional)
- Password authentication
- No built-in relay

**Pros:**
- Mature, stable
- Very fast
- Lightweight

**Cons:**
- Requires port forwarding or VPN
- More complex setup
- Older authentication methods

---

### Option C: TightVNC

**Features:**
- Free version available
- "Tight" encoding for slow connections
- Cross-platform

**Security:**
- Password only (limited encryption in free version)
- No built-in encryption

**Pros:**
- Good compression
- Simple

**Cons:**
- Weak security in free version
- Requires port forwarding
- Windows-focused

---

### Option D: RealVNC

**Features:**
- Free for personal use (limited)
- Cloud relay service
- Enterprise features

**Pricing:**
- Personal: Free (5 computers, 3 users)
- Professional: $4.99/month per computer
- Enterprise: Custom pricing

**Pros:**
- Established company
- Good support
- Cloud relay

**Cons:**
- Limited free tier
- Proprietary
- Expensive for multiple computers

---

## 2. Security Implications

### Threat Model

```
┌─────────────────────────────────────────────────────────────┐
│                    ATTACK VECTORS                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. MAN-IN-THE-MIDDLE                                       │
│     └── Encrypt all traffic (TLS/VPN)                      │
│                                                             │
│  2. UNAUTHORIZED ACCESS                                     │
│     └── Strong passwords + 2FA                             │
│                                                             │
│  3. RELAY SERVER COMPROMISE                                 │
│     └── Self-host or use reputable provider                │
│                                                             │
│  4. CLIENT-SIDE MALWARE                                     │
│     └── Limit access time + audit logs                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Security Checklist

| Control | Implementation | Priority |
|---------|---------------|----------|
| **Encryption** | E2E encryption or TLS | CRITICAL |
| **Authentication** | Strong password + 2FA | CRITICAL |
| **Network** | VPN or relay server | HIGH |
| **Access Control** | Time-limited sessions | HIGH |
| **Audit Logging** | Log all connections | MEDIUM |
| **IP Whitelisting** | Limit source IPs | MEDIUM |
| **Screen Blanking** | Blank local screen | LOW |

### Recommended Security Setup (RustDesk)

```bash
# 1. Generate strong permanent password
openssl rand -base64 32

# 2. Configure RustDesk with:
#    - Permanent password (not one-time)
#    - Enable 2FA if available
#    - Whitelist specific client IDs

# 3. Run self-hosted relay server with:
#    - TLS termination
#    - Behind firewall
#    - Limited to your client IPs
```

---

## 3. Network Setup Options

### Option 1: Direct Connection (Same Network)

```
┌──────────────┐         ┌──────────────┐
│   OpenClaw   │◄───────►│     You      │
│   (WSL2)     │  Local  │   (Client)   │
└──────────────┘ Network └──────────────┘
```

**Requirements:**
- Same local network
- WSL2 has Windows host IP access
- Direct VNC connection

**Pros:**
- Fastest (local network)
- No internet required
- Most secure

**Cons:**
- Limited to same network

---

### Option 2: Port Forwarding (NOT RECOMMENDED)

```
┌──────────────┐    Internet    ┌─────────┐    ┌──────────┐
│   OpenClaw   │◄──────────────►│  Router │◄──►│   You    │
│   (WSL2)     │                │  :5900  │    │ (Remote) │
└──────────────┘                └─────────┘    └──────────┘
```

**Why NOT recommended:**
- Exposes VNC port to internet
- Requires firewall configuration
- Target for brute force attacks

---

### Option 3: Reverse SSH Tunnel (Secure)

```
┌──────────────┐    ┌──────────────┐    ┌──────────┐
│   OpenClaw   │───►│  VPS/VPS     │◄───│   You    │
│   (WSL2)     │    │  (Jump Host) │    │ (Remote) │
└──────────────┘    └──────────────┘    └──────────┘
      │                                           │
      └────────── SSH Tunnel ─────────────────────┘
```

**Setup:**
```bash
# On OpenClaw (WSL2)
ssh -R 5900:localhost:5900 user@vps-server

# On your machine
ssh -L 5900:localhost:5900 user@vps-server
# Then connect VNC to localhost:5900
```

**Pros:**
- Encrypted tunnel
- No port forwarding needed
- Secure

**Cons:**
- Requires VPS/jump host
- More complex setup

---

### Option 4: Self-Hosted Relay (RECOMMENDED)

```
┌──────────────┐         ┌──────────────┐         ┌──────────┐
│   OpenClaw   │◄───────►│ Self-Hosted  │◄────────│   You    │
│   (WSL2)     │  ID/Relay│  Relay Server│  ID/Relay│ (Client) │
└──────────────┘         └──────────────┘         └──────────┘
                              │
                         (Your VPS or Home Server)
```

**RustDesk Relay Server Setup:**
```bash
# Run relay server with Docker
docker run --net=host \
  -e RELAY_SERVER=your-domain.com:21117 \
  rustdesk/rustdesk-server:latest
```

**Pros:**
- Full control
- No third-party dependencies
- Works through any firewall
- Encrypted

**Cons:**
- Requires server to run relay
- Initial setup complexity

---

## 4. OpenClaw Integration

### How OpenClaw Would Connect

```
┌─────────────────────────────────────────────────────────────┐
│              OPENCLAW INTEGRATION FLOW                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. USER REQUEST                                            │
│     "Show me the desktop"                                   │
│                           │                                 │
│                           ▼                                 │
│  2. OPENCLAW CHECKS VNC STATUS                              │
│     - Is RustDesk running?                                  │
│     - Get connection ID                                     │
│                           │                                 │
│                           ▼                                 │
│  3. OPENCLAW CAPTURES SCREEN                                │
│     - Uses existing screen/camera tools                     │
│     - Or: initiates VNC connection                          │
│                           │                                 │
│                           ▼                                 │
│  4. OPENCLAW DISPLAYS/ACTS                                  │
│     - Shows screenshot                                      │
│     - Or: describes what it sees                            │
│     - Or: sends mouse/keyboard commands                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Integration Methods

#### Method A: Screen Capture + Analysis

OpenClaw periodically captures the screen and analyzes it.

```javascript
// OpenClaw tool integration
{
  "tool": "screen_capture",
  "action": "snapshot",
  "output": "analyze with vision model"
}
```

**Pros:**
- No VNC client needed on your end
- Can analyze screen content
- Works with existing OpenClaw capabilities

**Cons:**
- Not true remote control
- Delayed updates

---

#### Method B: VNC Client Integration

OpenClaw acts as a VNC client, you connect as viewer.

```javascript
// OpenClaw runs VNC server in WSL2
// You connect with VNC client
// OpenClaw can send commands to the VNC session
```

**Pros:**
- True remote control
- You see what OpenClaw sees

**Cons:**
- Requires VNC client on your machine
- More complex

---

#### Method C: Hybrid Approach (RECOMMENDED)

```
┌─────────────────────────────────────────────────────────────┐
│                   HYBRID APPROACH                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   NORMAL MODE              │   REMOTE CONTROL MODE          │
│   ───────────              │   ─────────────────            │
│   OpenClaw uses:           │   You connect via VNC:         │
│   - browser tool           │   - See full desktop           │
│   - shell commands         │   - Control mouse/keyboard     │
│   - limited context        │   - OpenClaw assists           │
│                                                             │
│   SWITCH TRIGGER:                                           │
│   "Let me see your screen" or "Take control"                │
│                                                             │
│   OpenClaw:                                                 │
│   1. Starts RustDesk                                        │
│   2. Provides connection ID                                 │
│   3. You connect                                            │
│   4. OpenClaw can watch/help                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. OS-Specific Setup

### Windows WSL2 Setup

```bash
# 1. Install RustDesk in WSL2 (Ubuntu/Debian)
wget https://github.com/rustdesk/rustdesk/releases/download/1.3.5/rustdesk-1.3.5-x86_64.deb
sudo dpkg -i rustdesk-1.3.5-x86_64.deb
sudo apt-get install -f  # Fix dependencies

# 2. Configure RustDesk
# Edit /usr/lib/rustdesk/rustdesk2.ini
# Set permanent password

# 3. Start RustDesk service
rustdesk --service

# 4. Note the ID and password
rustdesk --version
```

**WSL2 Specific Considerations:**
- WSL2 has its own IP address
- Can access Windows host via `$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')`
- May need to configure Windows Firewall
- Consider using Windows-native RustDesk instead for full desktop

---

### Native Windows Setup (RECOMMENDED)

**Why Native Windows is Better:**
- WSL2 is isolated from Windows desktop
- Native Windows RustDesk can control entire computer
- Better performance
- Full access to Windows GUI

```powershell
# 1. Download RustDesk Windows installer
# https://github.com/rustdesk/rustdesk/releases

# 2. Install and configure
# - Set permanent password
# - Enable service
# - Configure startup

# 3. Get connection info
# ID: 123 456 789
# Password: [your secure password]
```

---

### RustDesk Configuration for OpenClaw

```ini
# rustdesk2.ini
[options]
# Permanent password (generate securely)
verification-method=PermanentPassword
permanent-password=YOUR_SECURE_PASSWORD_HERE

# Disable random password
enable-rand-password=N

# Auto-start
auto-start=Y

# Accept incoming connections
allow-auto-disconnect=N

# Security
allow-remote-config=N

# Relay server (if self-hosted)
custom-relay-server=your-relay.example.com:21117
custom-id-server=your-relay.example.com:21116
```

---

## PROJECT 2: RECOMMENDED IMPLEMENTATION

### Phase 1: Basic VNC Access - 1 hour
1. Install RustDesk on native Windows
2. Set permanent password
3. Test connection from your device
4. Document connection ID

### Phase 2: Self-Hosted Relay - 2-3 hours
1. Set up relay server (Hetzner/DigitalOcean VPS ~$5/mo)
2. Configure RustDesk to use custom relay
3. Set up firewall rules
4. Enable 2FA if available

### Phase 3: OpenClaw Integration - 2-4 hours
1. Create OpenClaw tool to start/stop RustDesk
2. Implement screen capture integration
3. Add command to provide connection details
4. Document usage workflow

---

# COST BREAKDOWN

## Project 1: Real-Time Dashboard

| Option | Monthly Cost | Setup Time | Maintenance |
|--------|-------------|------------|-------------|
| **Phase 1: Smart Polling** | **FREE** | 2 hours | None |
| **Phase 2: SSE on Render** | **FREE*** | 4 hours | Low |
| **Phase 3: Paid Render** | **$7/month** | 6 hours | Low |
| **Alternative: VPS** | **$5-6/month** | 1 day | Medium |
| **Alternative: Railway** | **$5+/month** | 4 hours | Low |

*Free tier has cold starts after 15 min idle

## Project 2: Full Computer Control

| Component | Monthly Cost | Notes |
|-----------|-------------|-------|
| **RustDesk (personal)** | **FREE** | No relay needed for local |
| **VPS for relay** | **$3-5/month** | Hetzner CX11 €4.51 |
| **RustDesk Pro** | **$9.90/month** | Commercial use, managed relay |
| **RealVNC Personal** | **FREE** | Limited to 5 computers |
| **RealVNC Professional** | **~$5/month** | Per computer |

### Total Recommended Monthly Cost

| Phase | Dashboard | VNC Relay | **Total** |
|-------|-----------|-----------|-----------|
| Phase 1 | $0 | $0 | **$0** |
| Phase 2 | $0 | $0 | **$0** |
| Phase 3 | $7 | $5 | **$12** |

---

# SECURITY CONSIDERATIONS SUMMARY

## Project 1: Dashboard
- ✅ HTTPS only (Render/Railway provide this)
- ✅ No sensitive data in data.json
- ✅ CORS properly configured
- ✅ Rate limiting on API endpoints

## Project 2: VNC Access
- ✅ E2E encryption enabled
- ✅ Strong password (32+ chars)
- ✅ Self-hosted relay (not public)
- ✅ IP whitelisting if possible
- ✅ Time-limited sessions
- ✅ Audit logs enabled
- ✅ 2FA enabled if available

---

# TIME ESTIMATES

| Task | Estimated Time |
|------|----------------|
| **PROJECT 1** | |
| Phase 1: Smart Polling | 2 hours |
| Phase 2: SSE Server | 4-6 hours |
| Phase 3: WebSocket + SQLite | 1-2 days |
| **PROJECT 1 TOTAL** | **2-3 days** |
| | |
| **PROJECT 2** | |
| Phase 1: Basic RustDesk | 1 hour |
| Phase 2: Self-hosted Relay | 2-3 hours |
| Phase 3: OpenClaw Integration | 2-4 hours |
| **PROJECT 2 TOTAL** | **1 day** |
| | |
| **BOTH PROJECTS** | **3-4 days** |

---

# NEXT STEPS

1. **Decide on approach for Project 1:**
   - Quick win: Implement smart polling today
   - Full solution: Deploy SSE to Render

2. **Start Project 2 immediately:**
   - Install RustDesk on Windows
   - Test connection
   - Can be done in parallel

3. **Questions to answer:**
   - What's your budget preference? (Free vs $12/month)
   - Do you have a VPS already?
   - Is 30-second polling acceptable for Phase 1?

---

*Document generated: 2026-02-11*
*For: OpenClaw Infrastructure Planning*
