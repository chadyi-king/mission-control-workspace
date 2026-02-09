import puppeteer from 'puppeteer';

const baseUrl = 'https://chadyi-king.github.io/mission-control-dashboard/';
const url = `${baseUrl}?cb=${Date.now()}`;

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function run() {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const page = await browser.newPage();
  const loadLogs = [];

  page.on('console', (msg) => {
    const text = msg.text();
    if (text.includes('Data loaded')) {
      loadLogs.push({ text, ts: Date.now() });
    }
  });

  page.on('dialog', async (dialog) => {
    await dialog.accept();
  });

  const navStart = Date.now();
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });

  await page.waitForFunction(
    () => typeof dashboardData !== 'undefined' && dashboardData && dashboardData.workflow && dashboardData.workflow.pending && dashboardData.workflow.pending.length > 0,
    { timeout: 20000 }
  );

  const ensuredTasks = await page.evaluate(() => {
    if (!dashboardData.tasks) {
      dashboardData.tasks = [
        ...dashboardData.workflow.pending,
        ...dashboardData.workflow.active,
        ...dashboardData.workflow.review,
        ...dashboardData.workflow.done,
      ];
      saveData();
    }
    return dashboardData.tasks.length;
  });

  const dataStatus = await page.evaluate(async () => {
    try {
      const res = await fetch('data.json?t=' + Date.now(), { cache: 'no-store' });
      if (!res.ok) {
        return { ok: false, status: res.status };
      }
      const json = await res.json();
      return { ok: true, keys: Object.keys(json || {}), statsSample: json?.stats };
    } catch (err) {
      return { ok: false, error: err.message };
    }
  });

  const localStorageStatus = await page.evaluate(() => {
    const raw = localStorage.getItem('missionControlData');
    return {
      hasData: !!raw,
      length: raw ? raw.length : 0,
    };
  });

  const domStatCheck = await page.evaluate(() => {
    const stats = dashboardData?.stats;
    const domValues = Array.from(document.querySelectorAll('.stat-value')).map((el) => el.textContent.trim());
    return {
      stats,
      domValues,
    };
  });

  const workflowCheck = await page.evaluate(() => {
    const workflow = dashboardData?.workflow;
    const domCounts = Array.from(document.querySelectorAll('.pipeline-count')).map((el) => Number(el.textContent.trim()));
    return { workflow, domCounts };
  });

  const preTaskStats = await page.evaluate(() => ({
    totalTasks: dashboardData.tasks.length,
    spawnedToday: dashboardData.stats.spawnedToday,
    activeCount: dashboardData.workflow.active.length,
  }));

  const addTaskResult = await page.evaluate(() => {
    const before = {
      totalTasks: dashboardData.tasks.length,
      spawnedToday: dashboardData.stats.spawnedToday,
      activeCount: dashboardData.workflow.active.length,
    };

    const title = `Automation Test Task ${Date.now()}`;
    openModal();
    document.getElementById('taskTitle').value = title;
    document.getElementById('taskNotes').value = 'Automated verification task';
    document.getElementById('taskProject').value = 'A2';
    document.getElementById('taskStatus').value = 'active';
    document.querySelectorAll('.priority-btn').forEach((b) => b.classList.remove('active'));
    const highBtn = document.querySelector('[data-priority="high"]');
    highBtn.classList.add('active');
    selectedPriority = 'high';
    submitTask();

    const after = {
      totalTasks: dashboardData.tasks.length,
      spawnedToday: dashboardData.stats.spawnedToday,
      activeCount: dashboardData.workflow.active.length,
    };

    const newTask = dashboardData.tasks[dashboardData.tasks.length - 1];
    return { before, after, newTaskId: newTask.id, newTaskTitle: newTask.title };
  });

  let editResult;
  try {
    editResult = await page.evaluate((taskId) => {
      viewTask(taskId);
      document.getElementById('taskTitle').value = 'Updated ' + Date.now();
      document.getElementById('taskStatus').value = 'review';
      document.querySelectorAll('.priority-btn').forEach((b) => b.classList.remove('active'));
      const lowBtn = document.querySelector('[data-priority="low"]');
      lowBtn.classList.add('active');
      selectedPriority = 'low';
      updateTask(taskId);
      return {
        updatedTask: dashboardData.tasks.find((t) => t.id === taskId),
      };
    }, addTaskResult.newTaskId);
  } catch (err) {
    editResult = { error: err.message };
  }

  const completeResult = await page.evaluate((taskId) => {
    completeTask(taskId);
    const task = dashboardData.tasks.find((t) => t.id === taskId);
    return {
      taskStatus: task ? task.status : null,
      tasksDone: dashboardData.stats.tasksDone,
      workflowDone: dashboardData.workflow.done.some((t) => t.id === taskId),
    };
  }, addTaskResult.newTaskId);

  const deleteResult = await page.evaluate((taskId) => {
    deleteTask(taskId);
    return {
      exists: !!dashboardData.tasks.find((t) => t.id === taskId),
      totalTasks: dashboardData.tasks.length,
    };
  }, addTaskResult.newTaskId);

  let filterResult;
  try {
    filterResult = await page.evaluate(() => {
      filterTasks('status', 'pending');
      return { ok: true };
    });
  } catch (err) {
    filterResult = { ok: false, error: err.message };
  }

  let searchResult;
  try {
    searchResult = await page.evaluate(() => {
      searchTasks('Test');
      return { ok: true };
    });
  } catch (err) {
    searchResult = { ok: false, error: err.message };
  }

  const projectModalResult = await page.evaluate(() => {
    viewProject('A2');
    const title = document.getElementById('projectModalTitle').textContent;
    const total = document.getElementById('projStatTotal').textContent;
    const active = document.getElementById('projStatActive').textContent;
    closeProjectModal();
    return { title, total, active };
  });

  const elapsed = Date.now() - navStart;
  if (elapsed < 33000) {
    await delay(33000 - elapsed + 1000);
  }

  const autoRefresh = {
    count: loadLogs.length,
    logs: loadLogs,
    intervalMs: loadLogs.length >= 2 ? loadLogs[1].ts - loadLogs[0].ts : null,
  };

  const result = {
    ensuredTasks,
    dataStatus,
    localStorageStatus,
    domStatCheck,
    workflowCheck,
    preTaskStats,
    addTaskResult,
    editResult,
    completeResult,
    deleteResult,
    filterResult,
    searchResult,
    projectModalResult,
    autoRefresh,
  };

  console.log(JSON.stringify(result, null, 2));

  await browser.close();
}

run().catch((err) => {
  console.error('Test run failed:', err);
  process.exit(1);
});
