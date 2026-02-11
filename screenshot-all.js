const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  const pages = [
    { url: 'https://chadyi-king.github.io/mission-control-dashboard/categories.html', name: 'categories' },
    { url: 'https://chadyi-king.github.io/mission-control-dashboard/insights.html', name: 'insights' },
    { url: 'https://chadyi-king.github.io/mission-control-dashboard/system.html', name: 'system' },
    { url: 'https://chadyi-king.github.io/mission-control-dashboard/resources.html', name: 'resources' }
  ];
  
  for (const p of pages) {
    await page.goto(p.url);
    await page.waitForTimeout(3000);
    await page.screenshot({ path: `/home/chad-yi/.openclaw/workspace/dashboard-${p.name}.png`, fullPage: true });
    console.log(`Screenshot: dashboard-${p.name}.png`);
  }
  
  await browser.close();
})();
