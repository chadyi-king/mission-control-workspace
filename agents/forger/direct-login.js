const { chromium } = require('playwright');

(async () => {
    console.log('=== DIRECT LOGIN ATTEMPT ===');
    console.log('Trying: Fill email, then password (no Continue click)');
    
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        viewport: { width: 375, height: 812 } // Mobile like screenshot
    });
    const page = await context.newPage();
    
    try {
        await page.goto('https://lovable.dev/login', { waitUntil: 'networkidle' });
        await page.screenshot({ path: '/tmp/login-start.png' });
        
        // Check what's visible immediately
        console.log('Checking for form fields...');
        
        const hasEmail = await page.$('input[type="email"]') !== null;
        const hasPassword = await page.$('input[type="password"]') !== null;
        
        console.log(`Email field: ${hasEmail ? '✅' : '❌'}`);
        console.log(`Password field: ${hasPassword ? '✅' : '❌'}`);
        
        if (hasEmail && hasPassword) {
            console.log('Both fields visible! Filling...');
            
            await page.fill('input[type="email"]', 's10258361@connect.np.edu.sg');
            await page.fill('input[type="password"]', 'Digimon7+');
            
            await page.screenshot({ path: '/tmp/login-filled.png' });
            
            console.log('Clicking Log in...');
            await page.click('button:has-text("Log in")');
            
            await page.waitForTimeout(5000);
            await page.screenshot({ path: '/tmp/login-result.png', fullPage: true });
            
            const url = page.url();
            console.log(`Result URL: ${url}`);
            
            if (!url.includes('login')) {
                console.log('✅✅✅ SUCCESS! ✅✅✅');
            } else {
                console.log('❌ Still on login page');
            }
        } else {
            console.log('❌ Password field not immediately visible');
            console.log('Account likely uses OAuth primarily');
        }
        
    } catch (e) {
        console.error('Error:', e.message);
    } finally {
        await browser.close();
    }
})();
