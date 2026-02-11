# 🚀 Mission Control Dashboard Migration Guide
## Moving from GitHub Pages to Render.com

> **Who this is for:** You've never used Render before and want a clear, step-by-step guide to migrate your Mission Control Dashboard.

---

## 📋 Table of Contents
1. [What is Render.com?](#what-is-rendercom)
2. [Step 1: Sign Up for Render](#step-1-sign-up-for-render)
3. [Step 2: Connect Your GitHub Account](#step-2-connect-your-github-account)
4. [Step 3: Create a New Web Service](#step-3-create-a-new-web-service)
5. [Step 4: Configure Your Web Service](#step-4-configure-your-web-service)
6. [Step 5: Deploy Your Dashboard](#step-5-deploy-your-dashboard)
7. [Step 6: Verify It's Working](#step-6-verify-its-working)
8. [Step 7: Updating Your Site After Migration](#step-7-updating-your-site-after-migration)
9. [Troubleshooting Common Issues](#troubleshooting-common-issues)
10. [FAQ](#faq)

---

## What is Render.com?

**Render.com** is a cloud platform that hosts web applications, static sites, and databases. Think of it like GitHub Pages, but with more features and flexibility.

**Why move to Render?**
- Better support for dynamic sites and APIs
- Automatic HTTPS (secure connections)
- Free tier available
- Direct integration with GitHub for auto-deployments
- Custom domains with SSL certificates

---

## Step 1: Sign Up for Render

### 1.1 Visit the Render Website
1. Open your web browser (Chrome, Firefox, Safari, etc.)
2. Go to: **https://render.com**
3. Look for the big **"Get Started for Free"** button in the top-right corner

```
┌─────────────────────────────────────────────┐
│  render.com                                 │
│                                             │
│  [Logo]  Products  Pricing  Docs  Blog   [Get Started for Free] │
│                                             │
│         Build, deploy, and scale            │
│         your apps with ease                 │
│                                             │
│              [Get Started for Free]         │
│                                             │
└─────────────────────────────────────────────┘
```

### 1.2 Create Your Account
1. Click the **"Get Started for Free"** button
2. You'll see a page with three options:
   - **Continue with GitHub** ← RECOMMENDED (easiest)
   - **Continue with GitLab**
   - **Continue with Email**

3. Click **"Continue with GitHub"**

```
┌─────────────────────────────────────────────┐
│  Create your Render account                 │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │  🔵 Continue with GitHub            │    │
│  └─────────────────────────────────────┘    │
│  ┌─────────────────────────────────────┐    │
│  │  🟠 Continue with GitLab            │    │
│  └─────────────────────────────────────┘    │
│  ┌─────────────────────────────────────┐    │
│  │  ✉️  Continue with Email            │    │
│  └─────────────────────────────────────┘    │
│                                             │
└─────────────────────────────────────────────┘
```

### 1.3 Authorize Render on GitHub
After clicking "Continue with GitHub":

1. You'll be redirected to GitHub (if you're not already logged in, log in first)
2. You'll see a page titled **"Authorize Render"**
3. It will show what permissions Render wants (reading your repositories, etc.)
4. Click the green **"Authorize render"** button

```
┌─────────────────────────────────────────────┐
│  Authorize Render                           │
│                                             │
│  render wants to access your GitHub account │
│                                             │
│  ☑️  Read access to repositories            │
│  ☑️  Read access to user profile data       │
│  ☑️  Read access to email addresses         │
│                                             │
│  [Cancel]        [Authorize render]         │
│                  (green button)             │
└─────────────────────────────────────────────┘
```

5. You'll be redirected back to Render
6. Fill in your **Full Name** and **Company/Organization** (optional)
7. Click **"Complete Sign Up"**

✅ **You're now signed up for Render!**

---

## Step 2: Connect Your GitHub Account

If you signed up with GitHub, your account is already connected. Skip to Step 3.

If you signed up with email and need to connect GitHub:

1. In the Render dashboard, click your profile picture (top-right)
2. Select **"Account Settings"**
3. Click **"Connected Accounts"** on the left sidebar
4. Click **"Connect GitHub"**
5. Follow the authorization steps above

---

## Step 3: Create a New Web Service

Now let's create a new service for your Mission Control Dashboard.

### 3.1 From the Dashboard
1. You should be on the Render dashboard (url: `dashboard.render.com`)
2. Look for a big **"New +"** button (usually blue, top-right)
3. Click it

```
┌─────────────────────────────────────────────┐
│  Dashboard                      [New +] 🔽  │
│                                             │
│  Welcome to Render!                         │
│                                             │
│  Get started by creating your first service │
│                                             │
│              [New +]                        │
│                                             │
└─────────────────────────────────────────────┘
```

### 3.2 Select Service Type
A dropdown menu will appear:

```
┌─────────────────┐
│  + New          │
│ ─────────────── │
│  🌐 Web Service │  ← CLICK THIS
│  📁 Static Site │
│  🗄️  PostgreSQL │
│  🔴 Redis       │
│  🐋 Private     │
│     Registry    │
│  💾 Disk        │
│  🔑 Secret File │
│  🛡️  Shield     │
└─────────────────┘
```

**Click "Web Service"**

> **Why Web Service and not Static Site?** 
> - Use **Web Service** if your dashboard has any backend code, APIs, or needs to run a server
> - Use **Static Site** if it's purely HTML/CSS/JS with no server-side processing
> - When in doubt, start with Web Service - you can change it later

### 3.3 Connect Your Repository
You'll see a "Create a Web Service" page:

```
┌─────────────────────────────────────────────┐
│  Create a Web Service                       │
│                                             │
│  Connect a repository                       │
│  ────────────────────────────────────────   │
│                                             │
│  [GitHub icon] GitHub    [GitLab icon] GitLab│
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │  🔍  Search repositories...        │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  Or paste a public repository URL below:    │
│  ┌─────────────────────────────────────┐    │
│  │  https://github.com/user/repo       │    │
│  └─────────────────────────────────────┘    │
│                                             │
└─────────────────────────────────────────────┘
```

1. Make sure **GitHub** is selected (it should be by default)
2. In the search box, start typing your repository name (e.g., "mission-control")
3. Render will show matching repositories from your GitHub account
4. **Click on your Mission Control Dashboard repository**

If you don't see your repository:
- Click **"Configure account"** next to the GitHub heading
- This opens GitHub - grant Render access to the repository
- Return to Render and refresh the page

---

## Step 4: Configure Your Web Service

This is where you tell Render how to build and run your dashboard.

### 4.1 Basic Configuration

You'll see a form like this:

```
┌─────────────────────────────────────────────┐
│  Create a Web Service                       │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│  GitHub / your-username / mission-control   │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                             │
│  Name *                                     │
│  ┌─────────────────────────────────────┐    │
│  │  mission-control       📝           │    │
│  └─────────────────────────────────────┘    │
│  This will be part of your URL              │
│                                             │
│  Region *                                   │
│  ┌─────────────────────────────────────┐    │
│  │  Oregon (US West)      ▼            │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  Branch *                                   │
│  ┌─────────────────────────────────────┐    │
│  │  main                  ▼            │    │
│  └─────────────────────────────────────┘    │
│                                             │
└─────────────────────────────────────────────┘
```

**Fill in these fields:**

| Field | What to Enter | Notes |
|-------|---------------|-------|
| **Name** | `mission-control` (or your preferred name) | This becomes part of your URL: `mission-control.onrender.com` |
| **Region** | Choose closest to your users | Oregon (US West) is default; use Frankfurt for EU users |
| **Branch** | `main` (or `master` if that's what you use) | The branch to deploy from |

### 4.2 Build Settings

Scroll down to the **Build & Deploy** section:

```
┌─────────────────────────────────────────────┐
│  Build & Deploy                             │
│  ────────────────────────────────────────   │
│                                             │
│  Runtime *                                  │
│  ┌─────────────────────────────────────┐    │
│  │  Node                 ▼             │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  Build Command *                            │
│  ┌─────────────────────────────────────┐    │
│  │  npm install && npm run build       │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  Start Command *                            │
│  ┌─────────────────────────────────────┐    │
│  │  npm start                          │    │
│  └─────────────────────────────────────┘    │
│                                             │
└─────────────────────────────────────────────┘
```

**Choose your Runtime:**

| If your dashboard uses... | Select Runtime |
|---------------------------|----------------|
| Node.js / React / Vue / Next.js | **Node** |
| Python / Flask / Django | **Python** |
| Just HTML/CSS/JS (no build step) | **Static Site** instead |
| Ruby on Rails | **Ruby** |
| Go | **Go** |
| PHP | **PHP** |
| Docker | **Docker** |

**Common Build & Start Commands:**

**For React/Vue/Angular (Node):**
```
Build Command: npm install && npm run build
Start Command: npm start
```

**For Next.js (Node):**
```
Build Command: npm install && npm run build
Start Command: npm start
```

**For Python Flask:**
```
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

**For Python Django:**
```
Build Command: pip install -r requirements.txt
Start Command: gunicorn myproject.wsgi
```

**For Static HTML (if using Web Service):**
```
Build Command: (leave empty or echo "No build")
Start Command: python -m http.server $PORT
```

### 4.3 Environment Variables (Optional)

If your dashboard needs environment variables (API keys, secrets, etc.):

1. Scroll to the **Environment Variables** section
2. Click **"Add Environment Variable"**
3. Enter the **Key** (variable name) and **Value**

```
┌─────────────────────────────────────────────┐
│  Environment Variables                      │
│  ────────────────────────────────────────   │
│                                             │
│  ┌───────────────┬──────────────────────┐   │
│  │  KEY          │  VALUE               │   │
│  ├───────────────┼──────────────────────┤   │
│  │  API_KEY      │  sk-abc123xyz        │   │
│  ├───────────────┼──────────────────────┤   │
│  │  DATABASE_URL │  postgres://...      │   │
│  └───────────────┴──────────────────────┘   │
│                                             │
│  [+ Add Environment Variable]               │
│                                             │
└─────────────────────────────────────────────┘
```

Common environment variables you might need:
- `NODE_ENV=production`
- `PORT=10000` (Render sets this automatically, but some apps need it)
- Any API keys your dashboard uses

### 4.4 Instance Type

Scroll to the **Instance Type** section:

```
┌─────────────────────────────────────────────┐
│  Instance Type                              │
│  ────────────────────────────────────────   │
│                                             │
│  ○ Free ($0/month)           ← SELECT THIS  │
│    512 MB RAM • 0.1 CPU                     │
│                                             │
│  ○ Starter ($7/month)                       │
│    512 MB RAM • 0.5 CPU                     │
│                                             │
│  ○ Standard ($25/month)                     │
│    2 GB RAM • 1 CPU                         │
│                                             │
│  ○ Pro ($85/month)                          │
│    4 GB RAM • 2 CPU                         │
│                                             │
└─────────────────────────────────────────────┘
```

**Select "Free"** unless you know you need more resources.

> ⚠️ **Free Tier Limitations:**
> - Service spins down after 15 minutes of inactivity
> - Takes 30-60 seconds to wake up when someone visits
> - Limited to 512 MB RAM
> - Good for testing and small projects

### 4.5 Create the Service

1. Scroll to the bottom of the page
2. Click the big **"Create Web Service"** button (blue)

```
┌─────────────────────────────────────────────┐
│                                             │
│     [   Create Web Service   ]              │
│           (blue button)                     │
│                                             │
│     (or "Save" if editing)                  │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Step 5: Deploy Your Dashboard

After clicking "Create Web Service":

### 5.1 Watch the Build Process

Render will automatically start building your app. You'll see:

```
┌─────────────────────────────────────────────┐
│  mission-control                            │
│  https://mission-control.onrender.com       │
│                                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│  Build & Deploy in progress...              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                             │
│  ▶ Building...                              │
│    └─→ npm install && npm run build        │
│    └─→ [================>      ] 45%        │
│                                             │
│  ○ Deploying...                             │
│  ○ Starting...                              │
│                                             │
│  [View Logs]  [Cancel Deploy]               │
│                                             │
└─────────────────────────────────────────────┘
```

The build process typically takes:
- **1-3 minutes** for simple static sites
- **3-5 minutes** for Node.js/React apps
- **5-10 minutes** for larger apps

### 5.2 Monitor the Logs

To see what's happening:

1. Click **"View Logs"** button
2. You'll see a live stream of the build process
3. Look for:
   - Green checkmarks = success
   - Red X's = errors
   - Yellow warnings = non-critical issues

```
┌─────────────────────────────────────────────┐
│  Deploy Logs                                │
│  ────────────────────────────────────────   │
│  14:32:15  → Build started                  │
│  14:32:16  ✓ Cloning repository             │
│  14:32:18  ✓ Installing dependencies        │
│  14:32:45  ✓ Building app                   │
│  14:33:02  ✓ Deploying to server            │
│  14:33:10  ✓ Service live                   │
│                                             │
│  [Refresh]  [Download]                      │
└─────────────────────────────────────────────┘
```

### 5.3 What to Expect

**During First Deploy:**
- ⏱️ Build process takes a few minutes
- 🔄 Page may auto-refresh when complete
- ✅ You'll see "Your service is live" message
- 🌐 A URL is generated: `https://your-app-name.onrender.com`

**After Deploy Completes:**
- The status changes to **"Live"** (green indicator)
- You get a public URL
- Auto-deploy is now active (pushes to GitHub will auto-redeploy)

---

## Step 6: Verify It's Working

### 6.1 Check the Status

Look for these indicators on your service page:

```
┌─────────────────────────────────────────────┐
│  mission-control                            │
│                                             │
│  Status:  🟢 Live                           │
│  URL:     https://mission-control.onrender.com│
│  Branch:  main                              │
│                                             │
│  [🟢 Live indicator in top left]            │
│                                             │
└─────────────────────────────────────────────┘
```

### 6.2 Visit Your URL

1. Click the URL shown on the page (e.g., `https://mission-control.onrender.com`)
2. Or copy-paste it into a new browser tab
3. Your Mission Control Dashboard should load!

### 6.3 Test Key Features

Check these things work:

| Check | What to Do |
|-------|------------|
| ✅ Page loads | Does the homepage appear? |
| ✅ No broken CSS | Does it look styled correctly? |
| ✅ Links work | Click navigation links |
| ✅ Data loads | If your dashboard fetches data, does it appear? |
| ✅ No console errors | Open browser DevTools (F12) → Console tab |

### 6.4 What if It Doesn't Work?

**If you see a "Build Failed" error:**
1. Click **"View Logs"**
2. Scroll to find the red error message
3. Common fixes:
   - Wrong build command → Check your package.json scripts
   - Missing dependencies → Add to package.json/requirements.txt
   - Wrong runtime selected → Go to Settings and change it

**If you see a "Service Unavailable" error:**
1. Wait 1-2 minutes (first deploy takes time)
2. Check logs for startup errors
3. Verify your start command is correct

**If the page loads but looks broken:**
1. Open browser DevTools (F12)
2. Check Console for errors
3. Check Network tab for failed requests
4. You may need to set environment variables

---

## Step 7: Updating Your Site After Migration

### 7.1 Automatic Deployments (Default)

Render automatically deploys when you push to GitHub!

**How it works:**
1. You make changes locally
2. You commit and push to GitHub
3. Render detects the push
4. Render rebuilds and redeploys automatically

```
Local → GitHub → Render (auto-deploy)
  ↑                              ↓
  └────── Live site updates ◄────┘
```

### 7.2 Manual Deploy Trigger

If you need to redeploy manually:

1. Go to your service dashboard
2. Click **"Manual Deploy"** dropdown
3. Select **"Deploy latest commit"**

```
┌─────────────────────────────────────────────┐
│  mission-control                            │
│                                             │
│  [Manual Deploy ▼]  [Settings]  [Events]    │
│      └──→ Deploy latest commit              │
│      └──→ Clear build cache & deploy        │
│                                             │
└─────────────────────────────────────────────┘
```

### 7.3 Disable Auto-Deploy (Optional)

If you want to control when deploys happen:

1. Go to **Settings** tab
2. Scroll to **Auto-Deploy**
3. Toggle it **OFF**
4. Now you'll need to click "Manual Deploy" for updates

### 7.4 Viewing Deploy History

See all past deployments:

1. Click the **"Events"** tab
2. You'll see a list:

```
┌─────────────────────────────────────────────┐
│  Events                                     │
│  ────────────────────────────────────────   │
│                                             │
│  🟢 Deploy succeeded    2 minutes ago       │
│  🟢 Deploy succeeded    3 hours ago         │
│  🔴 Deploy failed       5 hours ago         │
│  🟢 Deploy succeeded    1 day ago           │
│                                             │
│  Click any event to see detailed logs       │
│                                             │
└─────────────────────────────────────────────┘
```

### 7.5 Rollback to Previous Version

If a new deploy broke something:

1. Go to **Events** tab
2. Find the last working deploy
3. Click the **"Rollback"** link next to it
4. Confirm the rollback

---

## Troubleshooting Common Issues

### Issue: "No module found" or package errors

**Solution:**
```bash
# Make sure your package.json has all dependencies
# If using Node:
npm install --save missing-package-name

# If using Python:
pip install package-name
pip freeze > requirements.txt
```

Then commit and push the updated files.

### Issue: "Port already in use" or connection refused

**Solution:**
Make sure your app uses the PORT environment variable:

**Node.js:**
```javascript
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Listening on ${PORT}`));
```

**Python Flask:**
```python
import os
port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port)
```

### Issue: Static files (CSS/JS) not loading

**Solution:**
1. Check your build output directory matches Render's expectations
2. Common output directories:
   - React: `build/` or `dist/`
   - Vue: `dist/`
   - Angular: `dist/`
3. In Render Settings, verify "Publish Directory" is correct

### Issue: Environment variables not working

**Solution:**
1. Go to Settings → Environment Variables
2. Check variable names match exactly (case-sensitive)
3. Redeploy after adding variables (they're only read at startup)
4. Use "Clear build cache & deploy" to be sure

### Issue: Free tier slow to wake up

**Normal behavior:**
- Free services sleep after 15 min of inactivity
- First visit after sleep takes 30-60 seconds
- This is expected - upgrade to paid tier to prevent sleeping

---

## FAQ

### Q: Can I use my own domain?
**A:** Yes! Go to Settings → Custom Domains. Render provides free SSL certificates.

### Q: How do I add a database?
**A:** Click "New +" → "PostgreSQL" or "Redis". Render will give you a connection URL to add as an environment variable.

### Q: Is the free tier really free?
**A:** Yes, forever for personal projects. Limitations: services sleep after 15 min, 512 MB RAM, limited bandwidth.

### Q: Can I have multiple sites?
**A:** Yes, you can create unlimited services on the free tier.

### Q: How is this different from GitHub Pages?
**A:** Render supports server-side code, databases, and more. GitHub Pages is static-only.

### Q: What happens if I exceed free tier limits?
**A:** Your service may be paused. You'll need to upgrade or wait until the next billing cycle.

### Q: Can I delete my service?
**A:** Yes. Go to Settings → Danger Zone → Delete Service. This cannot be undone.

### Q: How do I update environment variables?
**A:** Settings → Environment Variables. Changes require a redeploy to take effect.

---

## Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│  RENDER QUICK REFERENCE                                │
├────────────────────────────────────────────────────────┤
│                                                        │
│  🌐 Dashboard:    dashboard.render.com                 │
│  📖 Docs:         render.com/docs                      │
│  🆘 Support:      render.com/contact                   │
│                                                        │
│  ─────────────────────────────────────────────────    │
│  CREATE NEW SERVICE                                    │
│  ─────────────────────────────────────────────────    │
│  1. Click [New +] → [Web Service]                      │
│  2. Connect GitHub repo                                │
│  3. Configure name, runtime, build/start commands      │
│  4. Select Free tier                                   │
│  5. Click [Create Web Service]                         │
│                                                        │
│  ─────────────────────────────────────────────────    │
│  UPDATE SITE                                           │
│  ─────────────────────────────────────────────────    │
│  • Push to GitHub = Auto deploy ✓                     │
│  • Or: Manual Deploy → Deploy latest commit            │
│                                                        │
│  ─────────────────────────────────────────────────    │
│  COMMON COMMANDS                                       │
│  ─────────────────────────────────────────────────    │
│  Node/React:  npm install && npm run build            │
│               npm start                                │
│  Python:      pip install -r requirements.txt          │
│               gunicorn app:app                         │
│  Static:      python -m http.server $PORT              │
│                                                        │
│  ─────────────────────────────────────────────────    │
│  FREE TIER LIMITS                                      │
│  ─────────────────────────────────────────────────    │
│  • Sleeps after 15 min inactivity                     │
│  • 512 MB RAM                                         │
│  • 100 GB bandwidth/month                             │
│  • 1 build hour/day                                   │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## Next Steps

Now that your Mission Control Dashboard is on Render:

1. ✅ **Test thoroughly** - Check all features work correctly
2. ✅ **Update your README** - Change the GitHub Pages URL to your new Render URL
3. ✅ **Set up custom domain** (optional) - Point your domain to Render
4. ✅ **Add monitoring** - Set up uptime alerts
5. ✅ **Invite team members** - Go to Settings → Team
6. ✅ **Consider upgrading** - If you need 24/7 uptime

---

## Need Help?

- **Render Docs:** https://render.com/docs
- **Render Community:** https://community.render.com
- **Status Page:** https://status.render.com

---

*Guide created for Mission Control Dashboard migration from GitHub Pages to Render.com*
*Last updated: 2026-02-11*
