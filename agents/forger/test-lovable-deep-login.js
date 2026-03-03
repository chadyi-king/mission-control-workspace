const { chromium } = require('playwright');

(async () => {
    console.log('Testing Lovable login with YOUR credentials...');
    console.log('Email: s10258361@connect.np.edu.sg');
    
    const browser = await chromium.launch({ headless: true }); // Fixed: headless mode for server
    const context = await browser.newContext();
    const page = await context.newPage();
    
    try {
        // Step 1: Go to main page first
        console.log('\n1. Loading lovable.dev...');
        await page.goto('https://lovable.dev', { waitUntil: 'networkidle' });
        await page.screenshot({ path: '/tmp/lovable-home.png' });
        
        // Step 2: Look for ANY login-related links
        console.log('\n2. Looking for login links...');
        const allLinks = await page.$$('a');
        for (let i = 0; i < Math.min(allLinks.length, 10); i++) {
            const text = await allLinks[i].textContent();
            const href = await allLinks[i].getAttribute('href');
            if (text?.toLowerCase().includes('login') || text?.toLowerCase().includes('sign')) {
                console.log(`   Found: "${text?.trim()}" -> ${href}`);
            }
        }
        
        // Step 3: Try clicking any login link
        const loginLink = await page.$('a[href*="login"], a[href*="signin"], button:has-text("Login"), button:has-text("Sign in")');
        
        if (loginLink) {
            const href = await loginLink.getAttribute('href');
            console.log(`\n3. Clicking login link: ${href}`);
            await loginLink.click();
            await page.waitForNavigation({ waitUntil: 'networkidle' });
            await page.screenshot({ path: '/tmp/lovable-login-form.png' });
            
            // Step 4: NOW look for email/password
            console.log('\n4. Looking for email/password fields...');
            
            const emailInput = await page.$('input[type="email"], input[name="email"], input[placeholder*="email" i]');
            const passwordInput = await page.$('input[type="password"], input[name="password"]');
            
            if (emailInput && passwordInput) {
                console.log('   ✅ EMAIL/PASSWORD FIELDS FOUND!');
                
                // Fill in YOUR credentials
                console.log('\n5. Filling YOUR credentials...');
                await emailInput.fill('s10258361@connect.np.edu.sg');
                await passwordInput.fill('Digimon7+');
                console.log('   ✅ Credentials filled');
                
                // Find submit button
                const submitBtn = await page.$('button[type="submit"], button:has-text("Login"), button:has-text("Sign in")');
                if (submitBtn) {
                    console.log('\n6. Submitting...');
                    await Promise.all([
                        submitBtn.click(),
                        page.waitForNavigation({ waitUntil: 'networkidle', timeout: 30000 }).catch(() => {})
                    ]);
                    
                    await page.screenshot({ path: '/tmp/lovable-logged-in.png' });
                    
                    const url = page.url();
                    console.log(`   Current URL: ${url}`);
                    
                    if (url.includes('dashboard') || url.includes('project')) {
                        console.log('   ✅✅✅ LOGIN SUCCESSFUL! ✅✅✅');
                        
                        // Look for B3 and B6
                        console.log('\n7. Looking for your projects...');
                        const projects = await page.$$('[data-testid="project"], .project-card, a[href*="project"]');
                        console.log(`   Found ${projects.length} projects`);
                        
                        for (let i = 0; i < Math.min(projects.length, 5); i++) {
                            const text = await projects[i].textContent();
                            console.log(`   - ${text?.trim()}`);
                        }
                        
                    } else {
                        console.log('   ❌ Login failed or wrong credentials');
                    }
                }
            } else {
                console.log('   ❌ Still no email/password fields');
                console.log('   Page HTML:', await page.content().then(c => c.substring(0, 500)));
            }
        } else {
            console.log('   ❌ No login link found');
            // Try direct URL
            console.log('\n3b. Trying direct /login URL...');
            await page.goto('https://lovable.dev/login', { waitUntil: 'networkidle' });
            await page.screenshot({ path: '/tmp/lovable-direct-login.png' });
            
            const emailInput = await page.$('input[type="email"]');
            if (emailInput) {
                console.log('   ✅ Login form found at /login!');
            }
        }
        
    } catch (error) {
        console.error('❌ Error:', error);
        await page.screenshot({ path: '/tmp/lovable-error.png' });
    } finally {
        await browser.close();
        console.log('\n✅ Test complete');
    }
})();
