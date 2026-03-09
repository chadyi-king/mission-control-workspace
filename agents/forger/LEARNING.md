# LEARNING.md — Forger
*Living build intelligence. Update after every meaningful build or discovery.*
*This compounds. The more you add, the faster future builds go.*

---

## How to Use This File

After every build session or notable discovery:
1. What worked well → reinforce it (Build Patterns)
2. What failed or caused rework → flag it (Mistakes)
3. Reusable component → add to Components table
4. Brand detail discovered → add to Brand Intelligence

---

## Build Patterns (What Works Every Time)

- **CSS custom properties first** — Set `--color-primary`, `--color-accent`, `--font-heading`
  in `:root` before touching any component. Never hardcode hex values in components.

- **Hero structure** — `position: relative` wrapper + semi-transparent overlay + centered
  `.content-wrapper` with `max-width: 1100px` margin: auto. Works across all device sizes.

- **GSAP ScrollTrigger** — Load via CDN (not npm when building vanilla). Initialize after
  `DOMContentLoaded`. Don't use `defer` on the GSAP script tag — triggers fail silently.

- **Mobile-first breakpoints** — Write base CSS for 375px, then use `@media (min-width: 768px)`
  and `@media (min-width: 1024px)`. Prevents cascade fights on desktop.

- **README before marking ready_for_review** — Write the deploy README as the last step.
  It forces you to verify every file exists and every path is correct.

---

## Mistakes to Avoid

- ❌ **Lorem Ipsum anywhere** — Always write real placeholder copy based on the brief.
  Even "Coming soon" is better. Lorem breaks Caleb's trust in reviews.

- ❌ **Skipping README.md** — Chad uses this to deploy. No README = build stalls at review.

- ❌ **ready_for_review without browser test** — Open the HTML in a browser first.
  At minimum: Chrome + Chrome mobile emulation (375px).

- ❌ **Forcing Lovable when it's wrong for the job** — Lovable login automation is fragile.
  For complex builds, use Lovable as visual reference only, build from scratch.

- ❌ **Relative paths in deploy** — Use absolute paths or root-relative `/assets/` paths.
  Relative paths break when page is served from a subdirectory.

- ❌ **Images without alt text** — Accessibility + SEO. Every `<img>` needs descriptive alt.

---

## AI Tool Learnings

### Kimi 2.5
- Best prompt structure: context first, then constraints, then ask.
  Example: "I'm building X for Y using Z stack. The constraint is A. Design the database schema."
- Give it the full tech context — it uses large context windows well.
- Don't ask it to "just write the code" — ask it to think through tradeoffs first.

### Claude Sonnet 4.6
- For debugging: paste the error + the relevant code block. It reads both together well.
- For copy: give it brand voice examples. "Write like Elluminate's brand: premium, direct, human."
- Great at CSS — give it a design screenshot description and it produces clean CSS fast.

### Lovable
- **Login:** Always via browser manually. CLI automation unreliable.
- **Export quality:** Good for structure and basic components. Strip tracking scripts on export.
- **Two-way sync:** Don't trust it. Treat export as one-way. Edit locally after export.
- **What it's good at:** Layout, hero sections, navigation. Weak at custom interactions.

### GitHub Copilot / Codex
- Writes better suggestions when you have type annotations and JSDoc comments.
- Tab-complete is fastest for: API route handlers, form handlers, CSS component patterns.
- Always read what it generates — it hallucinates library APIs occasionally.

---

## Reusable Components

| Component | Description | First built for | Location |
|-----------|-------------|-----------------|----------|
| CSS Reset | Modern reset + custom properties base | — | `templates/css-reset.css` |
| — | — | — | — |

*(Add components here as you build them — they speed up every future project)*

---

## Brand Intelligence

*(Learn once, never re-read the brief)*

### Elluminate (B6)
- **Domain:** elluminate.com.sg
- **Positioning:** Flagship EXSTATIC brand, premium professional services
- **First website build** — treat as portfolio quality
- **Colors/fonts/tone:** TBD — extract from brief when starting build

### Team Elevate (B3)
- **Domain:** teamelevateSG.com
- **Positioning:** Corporate training + leadership events
- **Note:** Transitioning toward Elluminate branding
- **Colors:** Gold/black scheme noted in backlog

### MENDAKI (B8)
- **Positioning:** Malay community development programmes
- **Audience:** Malay-Muslim community in Singapore
- **Tone:** Warm, community-focused, aspirational

---

## Technical Discoveries

### Vercel Deployment
- `vercel builds/{slug}/ --prod` works from any directory
- Custom domains: dashboard.vercel.com → Project → Settings → Domains
- Edge functions: `api/` directory in project root, auto-detected by Vercel

### DNS Typical Config
- A record: `@` → `76.76.21.21` (Vercel)
- CNAME: `www` → `cname.vercel-dns.com`
- Propagation: 10 min to 48 hours depending on registrar

### Shopify
- Liquid theme dev: `shopify theme dev` (watches for changes, hot reloads)
- Push to production: `shopify theme push --store={store}.myshopify.com`
- Custom checkout: Shopify Plus only — verify plan before promising this

---

## Process Improvements

| Date | Improvement | Why |
|------|-------------|-----|
| 2026-03-02 | Forger launched clean (heartbeat, queue, inbox/outbox) | Previous v2 broke |
| 2026-03-09 | Full identity stack + AI tool hierarchy documented | Caleb requested |

---

*Last updated: 2026-03-09*
*This file compounds — update it every session.*
