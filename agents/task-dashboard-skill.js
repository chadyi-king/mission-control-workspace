class TaskDashboardSkill {
  constructor() {
    this.tasks = [];
  }

  // Add a new task
  addTask(title, description = '', dueDate = null, priority = 'normal', tags = []) {
    const task = {
      id: this.tasks.length + 1,
      title,
      description,
      dueDate,
      priority,
      tags,
      completed: false,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    this.tasks.push(task);
    return task;
  }

  // Update an existing task by id
  updateTask(id, updates) {
    const task = this.tasks.find(t => t.id === id);
    if (!task) {
      throw new Error(`Task with id ${id} not found`);
    }
    Object.assign(task, updates);
    task.updatedAt = new Date();
    return task;
  }

  // Mark a task as completed
  completeTask(id) {
    return this.updateTask(id, { completed: true });
  }

  // Remove a task by id
  removeTask(id) {
    const index = this.tasks.findIndex(t => t.id === id);
    if (index === -1) {
      throw new Error(`Task with id ${id} not found`);
    }
    this.tasks.splice(index, 1);
    return true;
  }

  // Get tasks filtered by criteria
  getTasks(filter = {}) {
    return this.tasks.filter(task => {
      for (const key in filter) {
        if (filter[key] instanceof Array) {
          if (!filter[key].includes(task[key])) return false;
        } else if (task[key] !== filter[key]) {
          return false;
        }
      }
      return true;
    });
  }

  // Visualization data for dashboard
  getDashboardData() {
    const total = this.tasks.length;
    const completed = this.tasks.filter(t => t.completed).length;
    const pending = total - completed;

    // Group by priority
    const byPriority = this.tasks.reduce((acc, task) => {
      acc[task.priority] = (acc[task.priority] || 0) + 1;
      return acc;
    }, {});

    // Tasks upcoming deadlines (next 7 days)
    const now = new Date();
    const oneWeekLater = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
    const upcomingDeadlines = this.tasks.filter(t => {
      return t.dueDate && new Date(t.dueDate) >= now && new Date(t.dueDate) <= oneWeekLater && !t.completed;
    });

    return {
      total,
      completed,
      pending,
      byPriority,
      upcomingDeadlines,
    };
  }

  // Integration placeholder - to connect with external calendars / tools
  syncWithExternalTools() {
    // Implement integration here - e.g., sync tasks with calendar events or external APIs
  }

  // Interactive dashboard rendering (mockup text-based, replace with UI framework code)
  renderDashboard() {
    const data = this.getDashboardData();
    return `Task Dashboard for Caleb E:\n` +
      `Total tasks: ${data.total}\n` +
      `Completed: ${data.completed}\n` +
      `Pending: ${data.pending}\n` +
      `By priority: ${JSON.stringify(data.byPriority)}\n` +
      `Upcoming deadlines (next 7 days): ${data.upcomingDeadlines.map(t => t.title).join(', ') || 'None'}`;
  }
}

module.exports = TaskDashboardSkill;
