const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  // Capture console logs and errors
  page.on('console', msg => console.log('CONSOLE:', msg.type(), msg.text()));
  page.on('pageerror', err => console.log('PAGE ERROR:', err.message));
  
  console.log('Navigating...');
  try {
    const response = await page.goto('https://chadyi-king.github.io/mission-control-dashboard/insights.html?nocache=1', {timeout: 30000});
    console.log('Response status:', response.status());
    await page.waitForTimeout(5000);
    
    // Execute JavaScript to check if appData exists
    const appDataExists = await page.evaluate(() => { return typeof appData !== 'undefined' && appData !== null; });
    console.log('appData exists:', appDataExists);
    
    await page.screenshot({ path: '/home/chad-yi/.openclaw/workspace/dashboard-insights.png', fullPage: true });
    console.log('Screenshot saved');
  } catch (e) {
    console.log('ERROR:', e.message);
  }
  
  await browser.close();
})();
