import puppeteer from 'puppeteer';

const url = 'https://chadyi-king.github.io/mission-control-dashboard/';
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function run() {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });
  const page = await browser.newPage();
  page.on('console', (msg) => {
    console.log('PAGE', msg.type(), msg.text());
  });
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
  await delay(5000);
  const info = await page.evaluate(() => ({
    type: typeof dashboardData,
    hasData: dashboardData ? dashboardData.tasks?.length : null,
  }));
  console.log('INFO', info);
  await browser.close();
}

run().catch((err) => {
  console.error('debug fail', err);
  process.exit(1);
});
