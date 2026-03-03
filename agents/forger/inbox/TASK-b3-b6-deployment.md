# B3 & B6 WEBSITE DEPLOYMENT BRIEF
## Export from Lovable → Enhance → Deploy → Connect Domains

**Date:** 2026-03-03  
**From:** CHAD_YI  
**To:** Forger (The Builder)  
**Status:** HIGH PRIORITY

---

## PROJECTS OVERVIEW

### B3 - Team Elevate
| Detail | Value |
|--------|-------|
| **Company** | Team Elevate (B3) - Large scale events, D&D, carnivals |
| **Current Status** | Built in Lovable (Feb 5, 2026) |
| **Domain** | **teamelevate.sg** |
| **Action Needed** | Export → Enhance → Deploy → Domain connect |

### B6 - Elluminate
| Detail | Value |
|--------|-------|
| **Company** | Elluminate (B6) - Team building for schools/corporate/govt |
| **Current Status** | Built in Lovable (Feb 5, 2026) |
| **Domain** | **elluminate.sg** |
| **Action Needed** | Export → Enhance → Deploy → Domain connect |

---

## STEP 1: EXPORT FROM LOVABLE (Caleb Action Required)

**For Each Site:**

1. Go to https://lovable.dev
2. Open project (Team Elevate / Elluminate)
3. Click **"Export"** or **"GitHub"** button
4. Export to GitHub repository:
   - B3: `chadyi-king/team-elevate`
   - B6: `chadyi-king/elluminate`

**Expected Output:**
- React + Tailwind CSS code
- `index.html`, `src/` folder, `package.json`
- Pushed to GitHub

---

## STEP 2: FORGER ENHANCEMENTS

Once code is in GitHub, Forger will:

### A. SEO Optimization (website-seo skill)
- [ ] Add meta tags (title, description, keywords)
- [ ] Implement Open Graph tags for social sharing
- [ ] Add structured data (JSON-LD)
- [ ] Optimize images (alt tags, compression)
- [ ] Create sitemap.xml
- [ ] Create robots.txt

### B. Analytics (google-analytics skill)
- [ ] Add Google Analytics 4 tracking code
- [ ] Set up conversion tracking
- [ ] Add Google Search Console verification

### C. Contact Forms
- [ ] Add working contact form
- [ ] Connect to email service (Formspree/EmailJS)
- [ ] Form validation

### D. Performance
- [ ] Lazy load images
- [ ] Minify CSS/JS
- [ ] Optimize Core Web Vitals

---

## STEP 3: DEPLOYMENT

### Platform: Vercel (when skill installed) or GitHub Pages (now)

**GitHub Pages (Immediate):**
- Deploy via web-deploy-github skill
- URL: `chadyi-king.github.io/team-elevate`
- URL: `chadyi-king.github.io/elluminate`

**Vercel (Preferred, when skill ready):**
- Better performance
- Auto-deploy on git push
- Custom domain ready

---

## STEP 4: DOMAIN CONNECTION

### DNS Configuration Required

**For teamelevate.sg:**
```
Type: A
Name: @
Value: 76.76.21.21 (Vercel) or 185.199.108.153 (GitHub Pages)

Type: CNAME
Name: www
Value: cname.vercel-dns.com (Vercel) or chadyi-king.github.io (GitHub)
```

**For elluminate.sg:**
```
Type: A
Name: @
Value: 76.76.21.21 (Vercel) or 185.199.108.153 (GitHub Pages)

Type: CNAME
Name: www
Value: cname.vercel-dns.com (Vercel) or chadyi-king.github.io (GitHub)
```

**SSL:** Auto-enabled via Let's Encrypt (Vercel) or GitHub Pages

---

## TIMELINE

| Step | Time | Owner |
|------|------|-------|
| Export from Lovable | 5 min | Caleb |
| Forger enhancements | 2-4 hours | Forger |
| Deployment | 30 min | Forger |
| Domain connection | 5 min | Caleb (with Forger instructions) |
| **Total** | **~1 day** | **Collaborative** |

---

## SUCCESS CRITERIA

- [ ] Both sites live on custom domains
- [ ] SEO optimized (90+ Lighthouse score)
- [ ] Analytics tracking active
- [ ] Contact forms working
- [ ] SSL certificates active
- [ ] Mobile responsive
- [ ] Load time < 3 seconds

---

## NEXT ACTION

**Caleb:** Export B3 and B6 from Lovable to GitHub  
**Then:** Forger takes over for enhancements and deployment

---

*Waiting for GitHub export to proceed.*
