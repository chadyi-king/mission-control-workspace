const { chromium } = require('playwright');

(async () => {
    console.log('Testing Lovable browser automation...');
    
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    const page = await context.newPage();
    
    try {
        // Navigate to Lovable
        console.log('Navigating to https://lovable.dev...');
        await page.goto('https://lovable.dev', { waitUntil: 'networkidle', timeout: 30000 });
        
        // Take screenshot
        await page.screenshot({ path: '/tmp/lovable-homepage.png' });
        console.log('✅ Screenshot saved to /tmp/lovable-homepage.png');
        
        // Check for login button/link
        const loginLink = await page.$('a[href*="login"], button:has-text("Login"), a:has-text("Sign in")');
        if (loginLink) {
            console.log('✅ Login link found on page');
            const loginText = await loginLink.textContent();
            console.log(`   Text: "${loginText?.trim()}"`);
        } else {
            console.log('⚠️ No obvious login link found');
        }
        
        // Check page structure
        const title = await page.title();
        console.log(`✅ Page title: "${title}"`);
        
        // Check if there's a dashboard/projects link (requires login)
        const projectsLink = await page.$('a[href*="project"], a[href*="dashboard"]');
        if (projectsLink) {
            console.log('⚠️ Found project links (may require login)');
        }
        
        // Check for any forms (login forms)
        const forms = await page.$$('form');
        console.log(`ℹ️ Forms found: ${forms.length}`);
        
        const inputs = await page.$$('input[type="email"], input[type="password"]');
        console.log(`ℹ️ Login inputs found: ${inputs.length}`);
        
        console.log('\n✅ BROWSER AUTOMATION IS VIABLE');
        console.log('Playwright can navigate Lovable successfully.');
        
    } catch (error) {
        console.error('❌ Error:', error.message);
    } finally {
        await browser.close();
    }
})();
