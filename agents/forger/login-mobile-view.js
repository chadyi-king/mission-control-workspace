const { chromium } = require('playwright');

(async () => {
    console.log('=== LOGIN WITH VISIBLE PASSWORD FIELD ===');
    
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        viewport: { width: 375, height: 812 } // Mobile viewport like your screenshot
    });
    const page = await context.newPage();
    
    try {
        console.log('1. Going to login...');
        await page.goto('https://lovable.dev/login', { waitUntil: 'networkidle' });
        
        console.log('2. Filling email...');
        await page.fill('input[type="email"]', 's10258361@connect.np.edu.sg');
        
        console.log('3. Looking for password field...');
        
        // Wait for password field to appear (try multiple selectors)
        await page.waitForSelector('input[type="password"], input[placeholder*="password" i], input[name="password"]', { timeout: 10000 });
        
        console.log('   ✅ Password field found!');
        
        console.log('4. Filling password...');
        await page.fill('input[type="password"]', 'Digimon7+');
        
        console.log('5. Clicking Log in...');
        await page.click('button:has-text("Log in"), button[type="submit"]');
        
        await page.waitForNavigation({ waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
        
        const url = page.url();
        console.log(`URL: ${url}`);
        
        if (!url.includes('login')) {
            console.log('✅✅✅ LOGIN SUCCESS! ✅✅✅');
            
            // Save session
            const cookies = await context.cookies();
            require('fs').writeFileSync(
                '/home/chad-yi/.openclaw/workspace/agents/forger/.secrets/lovable-session.json',
                JSON.stringify(cookies, null, 2)
            );
            console.log('Session saved!');
        } else {
            console.log('❌ Login failed');
        }
        
    } catch (error) {
        console.error('Error:', error.message);
    } finally {
        await browser.close();
    }
})();
