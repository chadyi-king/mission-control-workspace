# ELLUMINATE.SG - SITE STRUCTURE & DEPLOYMENT PLAN

## SITE STRUCTURE

```
elluminate.sg/
├── index.html              (Homepage - DONE)
├── about/
│   └── index.html          (About Us, Team, Mission)
├── services/
│   └── index.html          (All Services Overview)
├── programs/
│   ├── corporate.html      (Corporate Team Building)
│   ├── schools.html        (School & Youth Programs)
│   └── government.html     (Government Training)
├── contact/
│   └── index.html          (Contact Form, Location)
├── css/
│   └── styles.css          (Consolidated stylesheet)
├── js/
│   └── main.js             (Interactivity, form handling)
└── assets/
    ├── images/             (Team photos, event photos)
    ├── logos/              (Client logos)
    └── icons/              (UI icons)
```

## DEPLOYMENT OPTIONS

### Option 1: Vercel (RECOMMENDED)
- **Speed:** Global CDN, edge deployment
- **Performance:** 99.9% uptime, automatic scaling
- **Custom Domain:** Easy SSL + domain connection
- **Cost:** Free tier sufficient
- **Features:** Preview deployments, analytics

### Option 2: GitHub Pages
- **Speed:** Good (CDN via Cloudflare)
- **Performance:** Reliable
- **Custom Domain:** Supported with SSL
- **Cost:** Free
- **Limitations:** Static only, no serverless functions

### Option 3: Netlify
- **Speed:** Excellent global CDN
- **Performance:** 99.9% uptime
- **Custom Domain:** Easy setup
- **Cost:** Free tier
- **Features:** Forms, identity, edge functions

## MY RECOMMENDATION: VERCEL

**Why Vercel:**
1. Best performance in Asia (Singapore edge)
2. Superior to GitHub Pages
3. Easy custom domain (elluminate.sg)
4. Automatic HTTPS/SSL
5. Preview deployments for testing

## DEPLOYMENT PROCESS

### Step 1: Create GitHub Repo
```
Repo: chadyi-king/elluminate-website
Branch: main
```

### Step 2: Push Code
```bash
git add .
git commit -m "Initial: Elluminate website"
git push origin main
```

### Step 3: Connect Vercel
```
1. Go to vercel.com
2. Import GitHub repo
3. Deploy automatically
4. Get: elluminate-xyz.vercel.app
```

### Step 4: Custom Domain
```
1. Add domain: elluminate.sg
2. Vercel provides DNS records
3. Update DNS at your registrar
4. SSL auto-configured
```

## CURRENT STATUS

✅ Homepage (index.html) - CREATED
⏳ About page - PENDING
⏳ Services page - PENDING
⏳ Programs pages (3) - PENDING
⏳ Contact page - PENDING
⏳ CSS consolidation - PENDING
⏳ Assets (images) - NEED FROM YOU

## WHAT I NEED FROM YOU

1. **Domain Access:** DNS settings for elluminate.sg
2. **Images:** 
   - Team building activity photos
   - Your team photos
   - Client logos (if any)
3. **Content:**
   - Specific program descriptions
   - Team member bios
   - Client testimonials

## HOSTING COSTS

| Service | Monthly | Annual |
|---------|---------|--------|
| Vercel Pro | $0 (free tier) | $0 |
| Domain (elluminate.sg) | ~$1 | ~$12 |
| **TOTAL** | **~$1/month** | **~$12/year** |

## NEXT STEPS

Want me to:
1. **Create all remaining pages** (About, Services, Programs, Contact)?
2. **Set up GitHub repo** and deploy to Vercel?
3. **Guide you through domain connection**?

Which first?
