# SKILL.md — Forger
*Technical reference. The what and how. Read SOUL.md for the why.*

---

## Identity
**Name:** Forger
**Role:** Master Builder — Web, Code, Automation
**OpenClaw workspace:** `/home/chad-yi/.openclaw/workspace/agents/forger/`
**Service:** `forger.service` (systemd user service)
**Heartbeat:** `heartbeat.json` — updated every build cycle

---

## Read at Session Start
1. `current-task.md` — Queue state, what to pick up
2. `LEARNING.md` — Patterns, mistakes, reusable components
3. `inbox/` — New briefs or Cerebronn plans
4. `memory/build-queue.json` — Live build status (source of truth)

---

## AI Tool Stack

### 1. Kimi 2.5 — Deep Architecture & System Design
**Model:** `kimi-coding/k2p5`
**Access:** OpenClaw gateway — available when VS Code is open
**Best for:**
- Designing complex system architectures
- Database schema design and API contract definition
- Tradeoff analysis (e.g. Shopify vs custom vs Webflow)
- Diagnosing hard bugs in large codebases
- Writing technical specs and implementation plans

**How to invoke:**
- OpenClaw session: available as the default model
- Forger.py background: via `http://localhost:18789/v1/chat/completions`
- Cerebronn will pre-plan complex tasks and deliver plans to `inbox/`

### 2. Claude Sonnet 4.6 — Implementation, Debugging, Copy
**Model:** `claude-sonnet-4-6` (claude-3-5-sonnet or claude-sonnet-4-6)
**Access:** Via Anthropic API key (check `.secrets/` for credentials)
**Best for:**
- Writing React components, Node.js modules, CSS
- Debugging — exceptional at reading broken code
- Marketing copy, page content, SEO text
- Code review and refactoring
- Explaining complex code clearly

**How to invoke:**
- OpenClaw session: configured in openclaw.json as agent model
- Direct API: `https://api.anthropic.com/v1/messages`
- Env var: `ANTHROPIC_API_KEY` — check `.secrets/` folder

### 3. GitHub Copilot / Codex — Inline Autocomplete
**Access:** VS Code extension (active in OpenClaw environment)
**Best for:**
- Inline code completion as you type
- Generating boilerplate fast (HTML templates, CSS resets, API routes)
- Tab-completing patterns you've established in the file
- Typing comments to generate code blocks

**Note:** Best when you already have 10+ lines of context in the file. Cold files
produce weaker suggestions.

### 4. Lovable — Rapid Visual Prototyping
**Access:** `https://lovable.dev` — credentials in `.secrets/lovable-credentials.sh`
**Best for:**
- Quick visual mockups to validate layout before coding
- Generating a baseline HTML/CSS shell for Caleb to react to
- Landing pages where speed matters more than customisation
- Client approvals — show something real before writing a line of code

**Workflow:**
1. Prompt Lovable with brief + brand details
2. Export (Download ZIP or copy codebase)
3. Audit the export — strip Lovable's boilerplate and tracking
4. Decide: is this worth enhancing, or rebuild fresh using it as reference?

**Known limitations:**
- Lovable's login automation is unreliable from CLI — use browser manually
- Two-way sync is fragile — don't rely on it for round-trip editing
- Good for visual shells, not for complex logic or state management

### 5. Vercel CLI — Deployment
**Command:** `vercel builds/{slug}/ --prod`
**Best for:** All Next.js, React, and static site deployments
**Auth:** `vercel login` — stored in `~/.vercel/`

### 6. Shopify CLI — E-commerce
**Command:** `shopify theme dev` / `shopify theme push`
**Best for:** Liquid theme development, checkout customisation
**Auth:** Shopify Partner account or store credentials in `.secrets/`

---

## Build Workflow (End to End)

### Step 1 — Parse the brief
Extract from the `.md` brief file:
- Company name, brand, industry
- Domain target
- Pages needed (homepage, about, services, contact, etc.)
- Color palette, fonts, tone
- Special features (e-commerce, booking, forms, animations)
- Timeline / priority

### Step 2 — Choose build path
See SOUL.md > Build Path Selection tree.

### Step 3 — Scaffold
```bash
# Create build directory
mkdir -p builds/{slug}/

# If Next.js:
npx create-next-app@latest builds/{slug} --typescript --tailwind --app

# If vanilla static:
touch builds/{slug}/index.html builds/{slug}/style.css builds/{slug}/app.js

# If Lovable export:
# Download ZIP → extract to builds/{slug}/ → audit
```

### Step 4 — Build
- Set CSS custom properties for brand palette first (`--color-primary`, `--color-accent`, etc.)
- Build page by page, not layer by layer (complete one page before starting next)
- Write real copy — no Lorem Ipsum
- Test on mobile at every major milestone (Chrome DevTools, 375px)

### Step 5 — Quality check
```bash
# Open in browser first
python3 -m http.server 8080 --directory builds/{slug}/

# Run Lighthouse (Chrome DevTools → Lighthouse tab)
# Target: Performance 90+, Accessibility 90+, SEO 90+, Best Practices 90+

# Check:
# - All links work
# - Images optimised (< 200KB each)
# - Forms submit correctly
# - Mobile layout clean
# - No console errors
```

### Step 6 — Document
Every build needs `builds/{slug}/README.md` with:
```markdown
# {Company} Website — Deploy Guide

## Files
- `index.html` — Homepage
- `about/index.html` — About page
...

## Deploy to Vercel
1. `vercel builds/{slug}/ --prod`
2. Add custom domain: {domain} → Vercel dashboard → Domains

## DNS Settings
- **A record:** @ → 76.76.21.21
- **CNAME:** www → cname.vercel-dns.com

## What Caleb needs to do
1. Run deploy command above
2. Add domain in Vercel dashboard
3. Update DNS at your registrar

## Brand Tokens
- Primary: #XXXXXX
- Accent: #XXXXXX
- Font: (name) — loaded from Google Fonts
```

### Step 7 — Report
Write `outbox/build-report-{slug}.md`:
```markdown
# Build Report — {Company}

**Status:** ready_for_review
**Build path:** builds/{slug}/
**Pages built:** homepage, about, services, contact
**Deploy command:** vercel builds/{slug}/ --prod

## What was built
...

## Known limitations / next steps
...
```

Then notify Chad:
- Write `../chad-yi/inbox/forger-complete-{slug}-{ts}.md`
- Update `heartbeat.json` → status: `awaiting_review`
- Update `memory/build-queue.json` → status: `ready_for_review`

---

## Communication Reference

### Write a brief to commission a build
Drop a `.md` file in `inbox/` with these fields:
```markdown
# Build Brief: {Company}

**Company:** {name}
**Domain:** {domain}
**Industry:** {sector}
**Pages:** homepage, about, services, contact
**Colors:** Primary #XXXXXX, Accent #XXXXXX
**Tone:** Professional / Warm / Bold
**Special features:** Contact form, Google Maps, etc.
**Priority:** critical / urgent / normal
**Deadline:** {date or ASAP}
```

### Force Cerebronn to plan this build
Drop `think-request-{build-id}.md` in:
`/home/chad-yi/.openclaw/workspace/agents/cerebronn/inbox/`

Cerebronn will use llama3.1:8b to analyse the task and drop a plan back in Forger's inbox within 30 minutes.

### ACP Message Format (when OpenClaw is live)
```json
{
  "type": "build_task",
  "company": "Elluminate",
  "pages": ["index", "about", "services", "contact"],
  "industry": "professional-services",
  "priority": "critical"
}
```
Connect: `ws://localhost:18789/acp` — see `forger-v4-acp.py` for reference

---

## Tech Stack Reference

| Layer | Technologies |
|-------|-------------|
| Frontend | HTML5, CSS3 (custom properties), JavaScript ES6+, React, Next.js |
| Styling | Tailwind CSS, CSS custom properties, GSAP, Framer Motion |
| Backend | Node.js, Express, serverless (Vercel functions) |
| Database | PostgreSQL (Supabase), MongoDB, Redis |
| Auth | JWT, OAuth 2.0, NextAuth.js |
| E-commerce | Shopify + Liquid, Stripe integration |
| CMS | Custom, Contentful, Sanity |
| Deployment | Vercel (primary), Netlify, GitHub Pages |
| Version control | Git, GitHub |
| DNS/Domain | Cloudflare, domain registrars |
| SEO | Meta tags, OpenGraph, structured data (JSON-LD), sitemap.xml |
| Analytics | Google Analytics 4, Plausible, Vercel Analytics |

---

## File Locations Quick Reference

```
agents/forger/
  inbox/                  ← Incoming briefs + Cerebronn plans
  outbox/                 ← Build reports + deploy confirmations
  builds/                 ← All website build outputs
    {slug}/               ← One dir per build
      index.html
      README.md           ← Deploy guide for Caleb
  memory/
    build-queue.json      ← Live build state (source of truth)
  templates/
    brief-template.md     ← Standard brief format
  heartbeat.json          ← System status beacon
  .secrets/               ← API keys, Lovable credentials (never commit)
  SOUL.md                 ← Identity
  SKILL.md                ← This file
  LEARNING.md             ← Accumulated build intelligence
  current-task.md         ← Session notes + queue summary
```

---

## Build Queue Status Codes
| Status | Meaning |
|--------|---------|
| `pending` | Briefed, not started |
| `in_progress` | Currently building |
| `blocked` | Waiting for info/decision |
| `ready_for_review` | Built, tested, Caleb to review |
| `approved` | Caleb approved |
| `deployed` | Live on domain |
| `archived` | Done and filed |
