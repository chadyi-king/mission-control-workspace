const { chromium } = require('playwright');

(async () => {
    console.log('=== EXACT LOGIN SEQUENCE ===');
    console.log('Email: s10258361@connect.np.edu.sg');
    console.log('Password: Digimon7+');
    console.log('');
    console.log('Step 1: Type email');
    console.log('Step 2: Click Continue');
    console.log('Step 3: Wait for password field');
    console.log('Step 4: Type password');
    console.log('Step 5: Click Continue/Sign in');
    console.log('');
    
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    const page = await context.newPage();
    
    try {
        // Step 1: Go to login
        console.log('1. Loading login page...');
        await page.goto('https://lovable.dev/login', { waitUntil: 'networkidle' });
        await page.screenshot({ path: '/tmp/step1-start.png' });
        
        // Accept cookies if present
        const cookiesBtn = await page.$('button:has-text("Accept all")');
        if (cookiesBtn) {
            await cookiesBtn.click();
            await page.waitForTimeout(1000);
        }
        
        // Step 2: Type email
        console.log('2. Typing email...');
        await page.fill('input[type="email"]', 's10258361@connect.np.edu.sg');
        await page.screenshot({ path: '/tmp/step2-email.png' });
        console.log('   ✅ Email entered');
        
        // Step 3: Click Continue
        console.log('3. Clicking Continue button...');
        await page.click('button:has-text("Continue")');
        console.log('   ✅ Continue clicked');
        
        // Step 4: WAIT for password field to appear
        console.log('4. Waiting for password field (up to 10 seconds)...');
        await page.waitForTimeout(3000); // Wait 3 seconds
        await page.screenshot({ path: '/tmp/step3-after-continue.png' });
        
        // Check if password field appeared
        const passwordField = await page.$('input[type="password"]');
        
        if (passwordField) {
            console.log('   ✅ PASSWORD FIELD APPEARED!');
            
            // Step 5: Type password
            console.log('5. Typing password...');
            await passwordField.fill('Digimon7+');
            await page.screenshot({ path: '/tmp/step4-password.png' });
            console.log('   ✅ Password entered');
            
            // Step 6: Click Continue/Sign in
            console.log('6. Clicking Continue/Sign in...');
            
            // Look for submit button
            const submitBtn = await page.$('button[type="submit"], button:has-text("Continue"), button:has-text("Sign in"), button:has-text("Login")');
            
            if (submitBtn) {
                const btnText = await submitBtn.textContent();
                console.log(`   Button text: "${btnText?.trim()}"`);
                
                await Promise.all([
                    submitBtn.click(),
                    page.waitForNavigation({ waitUntil: 'networkidle', timeout: 30000 }).catch(() => {})
                ]);
                
                await page.waitForTimeout(3000);
                await page.screenshot({ path: '/tmp/step5-after-login.png', fullPage: true });
                
                const url = page.url();
                console.log(`   Current URL: ${url}`);
                
                if (!url.includes('login')) {
                    console.log('');
                    console.log('✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅');
                    console.log('✅ LOGIN SUCCESSFUL! ✅');
                    console.log('✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅');
                    console.log('');
                    
                    // Save session
                    const cookies = await context.cookies();
                    require('fs').writeFileSync(
                        '/home/chad-yi/.openclaw/workspace/agents/forger/.secrets/lovable-session.json',
                        JSON.stringify(cookies, null, 2)
                    );
                    console.log('✅ Session saved for automation');
                    
                    // Look for projects
                    console.log('');
                    console.log('7. Looking for your projects...');
                    const content = await page.content();
                    
                    if (content.toLowerCase().includes('team elevate') || content.toLowerCase().includes('elevate')) {
                        console.log('   ✅ Found: Team Elevate (B3)');
                    }
                    if (content.toLowerCase().includes('elluminate')) {
                        console.log('   ✅ Found: Elluminate (B6)');
                    }
                    
                    console.log('');
                    console.log('✅✅✅ FULL AUTOMATION NOW POSSIBLE! ✅✅✅');
                    
                } else {
                    console.log('   ❌ Still on login page');
                    const error = await page.$eval('.error, [role="alert"], .alert', e => e.textContent).catch(() => null);
                    if (error) console.log(`   Error: ${error}`);
                }
            } else {
                console.log('   ❌ No submit button found');
            }
        } else {
            console.log('   ❌ Password field did NOT appear after 3 seconds');
            console.log('   This means the account uses Google/GitHub OAuth');
            
            // Check what's on the page
            const buttons = await page.$$('button');
            console.log(`   Buttons found: ${buttons.length}`);
            for (let i = 0; i < Math.min(buttons.length, 5); i++) {
                const text = await buttons[i].textContent();
                console.log(`   - "${text?.trim()}"`);
            }
        }
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        await page.screenshot({ path: '/tmp/error.png' });
    } finally {
        await browser.close();
        console.log('');
        console.log('✅ Test complete');
    }
})();
