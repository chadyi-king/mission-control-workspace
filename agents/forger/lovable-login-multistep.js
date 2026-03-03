const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
    console.log('=== LOVABLE LOGIN - MULTI-STEP ===');
    
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    const page = await context.newPage();
    
    try {
        // Step 1: Load login page
        console.log('1. Loading login page...');
        await page.goto('https://lovable.dev/login', { waitUntil: 'networkidle' });
        await page.screenshot({ path: '/tmp/lovable-step1.png' });
        console.log('   ✅ Login page loaded');
        
        // Accept cookies if present
        const acceptCookies = await page.$('button:has-text("Accept all"), button:has-text("Accept")');
        if (acceptCookies) {
            await acceptCookies.click();
            await page.waitForTimeout(1000);
        }
        
        // Step 2: Fill email
        console.log('\n2. Entering email...');
        await page.fill('input[type="email"], input[placeholder*="email" i]', 's10258361@connect.np.edu.sg');
        console.log('   ✅ Email entered');
        
        // Step 3: Click Continue
        console.log('\n3. Clicking Continue...');
        await page.click('button:has-text("Continue"), button[type="submit"]');
        await page.waitForTimeout(3000); // Wait for password field
        await page.screenshot({ path: '/tmp/lovable-step2.png' });
        
        // Step 4: Check if password field appeared
        const passwordInput = await page.$('input[type="password"]');
        
        if (passwordInput) {
            console.log('   ✅ Password field appeared');
            
            // Step 5: Fill password
            console.log('\n4. Entering password...');
            await passwordInput.fill('Digimon7+');
            console.log('   ✅ Password entered');
            
            // Step 6: Submit login
            console.log('\n5. Submitting...');
            await Promise.all([
                page.click('button[type="submit"], button:has-text("Sign in"), button:has-text("Login")'),
                page.waitForNavigation({ waitUntil: 'networkidle', timeout: 30000 }).catch(() => {})
            ]);
            
        } else {
            console.log('   ⚠️ No password field - checking current state...');
            // Maybe it sent a magic link or needs different flow
        }
        
        await page.screenshot({ path: '/tmp/lovable-step3.png' });
        
        const url = page.url();
        console.log(`\n6. Current URL: ${url}`);
        
        // Check login success
        if (url.includes('dashboard') || url.includes('projects') || url.includes('app.lovable')) {
            console.log('   ✅✅✅ LOGIN SUCCESSFUL! ✅✅✅');
            
            // Save session
            const cookies = await context.cookies();
            fs.writeFileSync('/home/chad-yi/.openclaw/workspace/agents/forger/.secrets/lovable-session.json', JSON.stringify(cookies, null, 2));
            console.log('   ✅ Session saved');
            
            // Find projects
            console.log('\n7. Finding your projects...');
            await page.waitForTimeout(2000);
            
            const projects = await page.$$('text=/Team Elevate|Elluminate|B3|B6/i');
            console.log(`   Found ${projects.length} matching projects`);
            
        } else if (url.includes('login')) {
            console.log('   ❌ Still on login - check credentials or 2FA');
            
            const error = await page.$eval('.error, [role="alert"]', el => el.textContent).catch(() => null);
            if (error) console.log(`   Error: ${error}`);
        } else {
            console.log('   ⚠️ Unknown state');
        }
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        await page.screenshot({ path: '/tmp/lovable-error.png' });
    } finally {
        await browser.close();
        console.log('\n✅ Complete');
    }
})();
