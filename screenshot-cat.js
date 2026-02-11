const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  await page.goto('https://chadyi-king.github.io/mission-control-dashboard/categories.html?nocache=1');
  await page.waitForTimeout(5000);
  await page.screenshot({ path: '/home/chad-yi/.openclaw/workspace/dashboard-categories.png', fullPage: true });
  console.log('Screenshot saved');
  
  await browser.close();
})();
