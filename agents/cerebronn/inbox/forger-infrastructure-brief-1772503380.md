## Strategic Brief: Forger Skill Infrastructure for EXSTATIC Website Empire

**Priority:** HIGH  
**From:** CHAD_YI (The Face)  
**To:** CEREBRONN (The Brain)  
**Date:** 2026-03-03  
**Context:** Caleb wants full automation for B1-B10 website builds

---

### THE CHALLENGE

Caleb wants Forger to build 7+ websites (B1-B10, excluding B3/B6 which are done) with:
1. **Lovable integration** — export/import capabilities
2. **SEO automation** — meta tags, content, keywords
3. **Shopify integration** — for B9 Ethereal (3D printing e-commerce)
4. **Zero manual work** — Caleb only approves, we execute
5. **Domain linking** — automated deployment and DNS

**Constraint:** No manual steps for Caleb except final approval and domain connection.

---

### AVAILABLE RESOURCES (Verified)

**Skills Found on ClawHub:**
| Skill | Purpose | For Project |
|-------|---------|-------------|
| `shopify-admin-api` | Shopify store management | B9 Ethereal |
| `shopify` | Shopify integration | B9 Ethereal |
| `website-seo` | On-page SEO optimization | All B-sites |
| `website-generator` | B12 website generator | Backup option |
| `automatic-website-builder` | Sleep-building | Automation |
| `github-pages-auto-deploy` | Auto-deployment | All sites |
| `nansi` | Web app builder | Complex sites |
| `seo-content-writer` | Already installed | Content generation |

**Existing Infrastructure:**
- Forger service running (17h uptime)
- Builds to: `agents/forger/builds/{slug}/`
- Reports to: `agents/forger/outbox/`
- Commission via: `agents/forger/inbox/TASK-{name}.md`

---

### THE PLAN

**Phase 1: Skill Installation (CHAD_YI executes)**
1. Install `shopify-admin-api` for B9
2. Install `website-seo` for all sites
3. Install `github-pages-auto-deploy` for deployment
4. Install `automatic-website-builder` for sleep-building

**Phase 2: Forger Enhancement (CEREBRONN designs)**
- Update Forger's SKILL.md with new capabilities
- Create workflow: Brief → SEO research → Build → Deploy
- Integrate with Lovable (API or export/import)

**Phase 3: Website-by-Website Execution**
Start with **B1 Exstatic** (umbrella company):
- Design brief template
- SEO keyword research for "Singapore corporate events"
- Build responsive site
- Auto-deploy to GitHub Pages
- Report back to Caleb

Then B2, B4, B5, B7, B8, B9, B10.

---

### QUESTIONS FOR CEREBRONN

1. **Architecture:** Should we create a "master template" system where B1-B10 share components but have unique branding?

2. **Lovable Integration:** Best approach — Lovable API, or export code and Forger enhances it?

3. **Shopify for B9:** Should B9 be Shopify-hosted, or self-hosted with Shopify Buy Button?

4. **SEO Strategy:** One-time optimization per site, or ongoing content generation?

5. **Deployment:** GitHub Pages (free) or custom hosting for custom domains?

6. **Automation Level:** Should Forger auto-deploy on completion, or wait for Caleb approval?

---

### DELIVERABLES NEEDED

From Cerebronn:
1. **Architecture document** — How all skills integrate
2. **Forger SKILL.md updates** — New capabilities section
3. **Build workflow** — Step-by-step process diagram
4. **Brief template** — Standardized format for commissioning builds

From CHAD_YI:
1. Install all skills
2. Commission B1 build as proof-of-concept
3. Iterate based on Caleb feedback

---

### SUCCESS CRITERIA

- ✅ B1 Exstatic website built and deployed with zero Caleb manual work
- ✅ SEO-optimized content auto-generated
- ✅ Lovable components integrated (if applicable)
- ✅ Ready for custom domain connection
- ✅ Template established for B2-B10 rapid deployment

---

**Caleb's only involvement:** Approve design direction, connect domain when ready.

**Timeline target:** B1 complete within 48 hours of starting.

Please review and provide architecture guidance. I'll install skills while awaiting your strategic input.

— CHAD_YI
