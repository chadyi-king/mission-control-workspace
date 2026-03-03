const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
    console.log('=== LOVABLE LOGIN AUTOMATION ===');
    console.log('Email: s10258361@connect.np.edu.sg');
    console.log('');
    
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    const page = await context.newPage();
    
    try {
        // Step 1: Go directly to login
        console.log('1. Navigating to login page...');
        await page.goto('https://lovable.dev/login', { waitUntil: 'networkidle', timeout: 30000 });
        await page.screenshot({ path: '/tmp/lovable-login.png' });
        console.log('   ✅ Login page loaded');
        
        // Step 2: Fill credentials
        console.log('\n2. Filling YOUR credentials...');
        await page.fill('input[type="email"], input[name="email"]', 's10258361@connect.np.edu.sg');
        await page.fill('input[type="password"], input[name="password"]', 'Digimon7+');
        console.log('   ✅ Credentials filled');
        
        // Step 3: Submit
        console.log('\n3. Submitting login...');
        await Promise.all([
            page.click('button[type="submit"], button:has-text("Sign in"), button:has-text("Login")'),
            page.waitForNavigation({ waitUntil: 'networkidle', timeout: 30000 }).catch(() => {})
        ]);
        
        await page.screenshot({ path: '/tmp/lovable-after-login.png' });
        
        const url = page.url();
        console.log(`   Current URL: ${url}`);
        
        // Step 4: Check if logged in
        if (url.includes('dashboard') || url.includes('project') || !url.includes('login')) {
            console.log('   ✅✅✅ LOGIN SUCCESSFUL! ✅✅✅');
            
            // Save session for future use
            const cookies = await context.cookies();
            fs.writeFileSync('/home/chad-yi/.openclaw/workspace/agents/forger/.secrets/lovable-session.json', JSON.stringify(cookies, null, 2));
            console.log('   ✅ Session saved for automation');
            
            // Step 5: Find projects
            console.log('\n4. Looking for your projects...');
            await page.waitForTimeout(2000);
            
            const projects = await page.$$('[data-testid="project"], .project-card, a[href*="project"]');
            console.log(`   Found ${projects.length} project(s)`);
            
            for (let i = 0; i < Math.min(projects.length, 10); i++) {
                const text = await projects[i].textContent();
                const href = await projects[i].getAttribute('href');
                console.log(`   ${i+1}. ${text?.trim().substring(0, 50)}${href ? ` (${href})` : ''}`);
            }
            
            // Step 6: Look for B3 and B6 specifically
            console.log('\n5. Searching for B3 (Team Elevate) and B6 (Elluminate)...');
            const pageContent = await page.content();
            
            if (pageContent.toLowerCase().includes('team elevate') || pageContent.toLowerCase().includes('elevate')) {
                console.log('   ✅ Found: Team Elevate (B3)');
            }
            if (pageContent.toLowerCase().includes('elluminate')) {
                console.log('   ✅ Found: Elluminate (B6)');
            }
            
            console.log('\n✅✅✅ FULL AUTOMATION POSSIBLE! ✅✅✅');
            console.log('You can now say "Export B3" and I will:');
            console.log('  1. Login automatically');
            console.log('  2. Navigate to project');
            console.log('  3. Click Export → GitHub');
            console.log('  4. Handle everything else');
            
        } else {
            console.log('   ❌ Login failed');
            
            // Check for errors
            const errorText = await page.$eval('.error, [role="alert"], .alert', el => el.textContent).catch(() => null);
            if (errorText) {
                console.log(`   Error: ${errorText}`);
            }
        }
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        await page.screenshot({ path: '/tmp/lovable-error.png' });
    } finally {
        await browser.close();
        console.log('\n✅ Automation test complete');
    }
})();
