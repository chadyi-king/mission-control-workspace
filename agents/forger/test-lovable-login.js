const { chromium } = require('playwright');

(async () => {
    console.log('Testing Lovable login...');
    
    // Load credentials
    const email = process.env.LOVABLE_EMAIL || 's10258361@connect.np.edu.sg';
    const password = process.env.LOVABLE_PASSWORD || 'Digimon7+';
    
    if (!email || !password) {
        console.error('❌ Credentials not found');
        process.exit(1);
    }
    
    console.log(`Using email: ${email}`);
    
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    const page = await context.newPage();
    
    try {
        // Step 1: Navigate to login page
        console.log('\n1. Navigating to login...');
        await page.goto('https://lovable.dev/login', { waitUntil: 'networkidle', timeout: 30000 });
        await page.screenshot({ path: '/tmp/lovable-login-page.png' });
        console.log('   ✅ Login page loaded');
        
        // Step 2: Check for email/password fields
        const emailField = await page.$('input[type="email"], input[name="email"]');
        const passwordField = await page.$('input[type="password"]');
        
        if (!emailField || !passwordField) {
            console.log('   ⚠️ Standard login form not found, checking for OAuth...');
            
            // Check for Google/GitHub OAuth buttons
            const googleBtn = await page.$('button:has-text("Google"), a:has-text("Google")');
            const githubBtn = await page.$('button:has-text("GitHub"), a:has-text("GitHub")');
            
            if (googleBtn) {
                console.log('   ℹ️ Google OAuth button found');
            }
            if (githubBtn) {
                console.log('   ℹ️ GitHub OAuth button found');
            }
            
            console.log('   ❌ Cannot automate OAuth login without additional setup');
            console.log('   💡 Recommendation: Use GitHub export instead');
            
        } else {
            console.log('   ✅ Email and password fields found');
            
            // Step 3: Fill in credentials
            console.log('\n2. Filling credentials...');
            await emailField.fill(email);
            await passwordField.fill(password);
            console.log('   ✅ Credentials filled');
            
            // Step 4: Submit login
            console.log('\n3. Submitting login...');
            const submitBtn = await page.$('button[type="submit"], button:has-text("Login"), button:has-text("Sign in")');
            
            if (submitBtn) {
                await Promise.all([
                    submitBtn.click(),
                    page.waitForNavigation({ waitUntil: 'networkidle', timeout: 30000 })
                ]);
                
                await page.screenshot({ path: '/tmp/lovable-after-login.png' });
                console.log('   ✅ Login submitted, page navigated');
                
                // Step 5: Check if logged in
                const currentUrl = page.url();
                console.log(`   Current URL: ${currentUrl}`);
                
                if (currentUrl.includes('dashboard') || currentUrl.includes('project')) {
                    console.log('   ✅ Successfully logged in!');
                    
                    // Step 6: Look for projects
                    console.log('\n4. Looking for projects...');
                    const projectLinks = await page.$$('a[href*="project"], .project-card, [data-testid="project"]');
                    console.log(`   Found ${projectLinks.length} project elements`);
                    
                    // Take screenshot of dashboard
                    await page.screenshot({ path: '/tmp/lovable-dashboard.png', fullPage: true });
                    console.log('   ✅ Dashboard screenshot saved');
                    
                } else if (currentUrl.includes('login')) {
                    console.log('   ❌ Still on login page - credentials may be wrong');
                    
                    // Check for error messages
                    const errorMsg = await page.$('.error, .alert, [role="alert"]');
                    if (errorMsg) {
                        const errorText = await errorMsg.textContent();
                        console.log(`   Error: ${errorText}`);
                    }
                } else {
                    console.log('   ⚠️ Unknown state after login');
                }
            } else {
                console.log('   ❌ Submit button not found');
            }
        }
        
    } catch (error) {
        console.error('\n❌ Error:', error.message);
        await page.screenshot({ path: '/tmp/lovable-error.png' });
    } finally {
        await browser.close();
        console.log('\n✅ Browser closed');
    }
})();
