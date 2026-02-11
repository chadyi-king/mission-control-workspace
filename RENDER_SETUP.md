# MOVE DASHBOARD TO RENDER.COM (FREE - INSTANT UPDATES)

## WHY:
- GitHub Pages: Static files, 5-10 min delay on updates
- Render.com: Live server, 30 second delay on updates

## COST:
- FREE tier: $0/month (sleeps after 15 min idle)
- Starter: $7/month (always on)

## SETUP STEPS:

### 1. Create Render Account
1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repos

### 2. Create New Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repo: `chadyi-king/mission-control-dashboard`
3. Configure:
   - **Name:** mission-control-dashboard
   - **Environment:** Static Site
   - **Build Command:** (leave empty)
   - **Publish Directory:** ./
4. Click "Create Web Service"

### 3. Get Your URL
- Render gives you: `https://mission-control-dashboard.onrender.com`
- This updates in 30 seconds when you push to GitHub

### 4. Update Dashboard
The HTML files stay the same - just hosted on Render instead of GitHub Pages

### 5. (Optional) Custom Domain
- Add your own domain in Render settings
- Or keep the .onrender.com URL

## COMPARISON:

| Feature | GitHub Pages | Render.com |
|---------|--------------|------------|
| Cost | Free | Free* |
| Update Speed | 5-10 minutes | 30 seconds |
| Always On | Yes | No* |
| Custom Domain | Yes | Yes |
| Server-side | No | No (static) |

*Free tier sleeps after 15 min idle ($7/mo for always-on)

## RECOMMENDATION:
Start with Render.com FREE tier
- Test if update speed matters to you
- If yes, upgrade to $7/mo
- If no, stay on GitHub Pages and wait 10 minutes
