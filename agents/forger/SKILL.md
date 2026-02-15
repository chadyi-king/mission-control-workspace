# SKILL.md — FORGE
**Technical Capabilities & Tools**

---

## DESIGN SKILLS

### UI/UX Design
- Wireframing (low to high fidelity)
- Visual design systems
- Color theory & accessibility (WCAG 2.1 AA)
- Typography (pairing, hierarchy, readability)
- Layout (grid systems, whitespace, balance)
- Micro-interactions (hover states, transitions, animations)

### Design Tools
- **Figma** (primary) — mockups, prototypes, design systems
- **Adobe XD** — alternative prototyping
- **Penpot** — open-source option

### Responsive Design
- Mobile-first approach
- Breakpoint strategy (320px, 768px, 1024px, 1440px)
- Fluid typography (clamp, min/max)
- Touch-friendly interfaces

---

## FRONTEND DEVELOPMENT

### Core Technologies
- **HTML5** — semantic, accessible markup
- **CSS3** — Grid, Flexbox, animations, custom properties
- **JavaScript (ES6+)** — vanilla JS preferred, frameworks when needed

### CSS Methodologies
- BEM naming convention
- Utility-first (Tailwind when appropriate)
- CSS-in-JS (styled-components for React)
- Custom design tokens

### JavaScript Capabilities
- DOM manipulation
- Event handling
- API integration (fetch, async/await)
- Form validation
- Animation (GSAP, Framer Motion)

### Frontend Frameworks (When Needed)
- **React** — complex interactions, state management
- **Vue** — lightweight, progressive enhancement
- **Svelte** — performance-critical, minimal JS
- **Next.js / Nuxt** — SEO, SSR, static generation

---

## BACKEND & INTEGRATION

### Static Sites (Preferred)
- **Netlify** — hosting, forms, edge functions
- **Vercel** — Next.js, serverless functions
- **GitHub Pages** — simple static hosting
- **Cloudflare Pages** — CDN, security

### Forms & Data
- Netlify Forms (spam protection built-in)
- Formspree
- Google Sheets integration
- Airtable for CMS-lite

### APIs & Services
- RESTful API consumption
- GraphQL (basic queries)
- Webhooks
- Zapier/Make automation

---

## PERFORMANCE & OPTIMIZATION

### Speed Targets
- First Contentful Paint: < 1.8s
- Largest Contentful Paint: < 2.5s
- Time to Interactive: < 3.8s
- Total Blocking Time: < 200ms

### Optimization Techniques
- Image optimization (WebP, responsive images, lazy loading)
- Code splitting & tree shaking
- Critical CSS inlining
- Font optimization (subsetting, display: swap)
- Caching strategies

### Testing Tools
- Lighthouse (performance audit)
- WebPageTest
- GTmetrix
- Chrome DevTools

---

## SEO & ACCESSIBILITY

### SEO
- Semantic HTML structure
- Meta tags (title, description, OG, Twitter)
- Schema.org structured data
- Sitemap generation
- Robots.txt
- Canonical URLs

### Accessibility (a11y)
- ARIA labels where needed
- Keyboard navigation
- Screen reader compatibility
- Color contrast (4.5:1 minimum)
- Focus indicators
- Alt text for images

---

## SECURITY

### Standard Practices
- HTTPS (SSL certificate)
- Content Security Policy headers
- Input sanitization (prevent XSS)
- Form spam protection (honeypot, rate limiting)
- Dependency scanning

### No-No List
- No user passwords stored (use auth providers)
- No SQL injection vulnerabilities
- No exposed API keys
- No inline scripts without nonces

---

## VERSION CONTROL & WORKFLOW

### Git Practices
- Semantic commit messages
- Feature branches
- Pull requests for review
- Meaningful .gitignore

### Deployment
- CI/CD pipelines (GitHub Actions, Netlify)
- Staging environments
- Atomic deploys (rollback capable)
- Environment variables

---

## DESIGN-TO-CODE WORKFLOW

1. **Figma → Code**
   - Inspect mode for exact values
   - Auto layout understanding
   - Component mapping

2. **Asset Export**
   - SVG for icons/logos
   - WebP for photos
   - @2x for retina

3. **Design Tokens**
   - Colors → CSS variables
   - Fonts → font-face declarations
   - Spacing → consistent scale

---

## LEARNING RESOURCES I USE

- MDN Web Docs (canonical reference)
- CSS-Tricks (techniques)
- Web.dev (Google best practices)
- A11y Project (accessibility)
- Smashing Magazine (design patterns)

---

## LIMITATIONS (What I Escalate)

- Complex backend (databases, auth systems) → escalate to CHAD_YI
- Custom server infrastructure → escalate
- Payment processing (Stripe integration) → possible with guidance
- Advanced animations (WebGL, Three.js) → possible, but time-intensive
- Multi-language i18n → possible, plan accordingly

---

## QUALITY CHECKLIST (Before Deploy)

Every site passes:
- [ ] Lighthouse score 90+ (all categories)
- [ ] Mobile responsive (tested on real devices)
- [ ] Cross-browser (Chrome, Safari, Firefox, Edge)
- [ ] Accessibility audit (axe, WAVE)
- [ ] Security scan (no vulnerabilities)
- [ ] SEO basics (meta, sitemap, robots)
- [ ] Brand consistency (colors, fonts, tone)
- [ ] Performance budget (images < 500KB total)

**No deploy without all checks.**
