const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('https://chadyi-king.github.io/mission-control-dashboard/');
  await page.waitForTimeout(3000); // Wait for JS to load
  await page.screenshot({ path: '/home/chad-yi/.openclaw/workspace/dashboard-homepage.png', fullPage: true });
  console.log('Screenshot saved to dashboard-homepage.png');
  await browser.close();
})();
