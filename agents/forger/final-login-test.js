const { chromium } = require('playwright');

(async () => {
    console.log('=== FINAL LOGIN ATTEMPT ===');
    console.log('Email: s10258361@connect.np.edu.sg');
    console.log('Password: [confirmed]');
    
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    const page = await context.newPage();
    
    try {
        await page.goto('https://lovable.dev/login', { waitUntil: 'networkidle' });
        
        // Accept cookies
        const cookies = await page.$('button:has-text("Accept all")');
        if (cookies) await cookies.click();
        
        // Fill email
        await page.fill('input[type="email"]', 's10258361@connect.np.edu.sg');
        console.log('✅ Email filled');
        
        // Look for password field immediately (maybe it's hidden)
        let passwordInput = await page.$('input[type="password"]');
        
        if (!passwordInput) {
            console.log('No password field visible, clicking Continue...');
            await page.click('button:has-text("Continue")');
            await page.waitForTimeout(3000);
            
            // Check again for password
            passwordInput = await page.$('input[type="password"]');
        }
        
        if (passwordInput) {
            console.log('✅ Password field found!');
            await passwordInput.fill('Digimon7+');
            console.log('✅ Password filled');
            
            // Click sign in
            await page.click('button[type="submit"]');
            await page.waitForTimeout(5000);
            
            const url = page.url();
            console.log(`URL after login: ${url}`);
            
            if (!url.includes('login')) {
                console.log('✅✅✅ LOGIN SUCCESS! ✅✅✅');
                await page.screenshot({ path: '/tmp/lovable-success.png', fullPage: true });
                
                // Save session
                const cookies = await context.cookies();
                require('fs').writeFileSync(
                    '/home/chad-yi/.openclaw/workspace/agents/forger/.secrets/lovable-session.json',
                    JSON.stringify(cookies, null, 2)
                );
                console.log('✅ Session saved');
            } else {
                console.log('❌ Login failed - check if account uses Google/GitHub');
                const error = await page.$eval('.error, [role="alert"]', e => e.textContent).catch(() => '');
                if (error) console.log('Error:', error);
            }
        } else {
            console.log('❌ No password field appeared');
            console.log('Account likely uses Google/GitHub OAuth, not email/password');
            console.log('Options:');
            console.log('1. Add password in Lovable account settings');
            console.log('2. Use GitHub export (one click, works now)');
        }
        
    } catch (e) {
        console.error('Error:', e.message);
    } finally {
        await browser.close();
    }
})();
