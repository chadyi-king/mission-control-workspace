# Project Tasks Modal (A6-14)

**Goal:** Implement the "Project Tasks List" enhancement so that every Mission Control page can show the full task list for a project inside a rich modal instead of the current placeholder alerts.

## Context
- All dashboard pages live in `mission-control-dashboard/` and currently duplicate the same inline CSS + JS. Pages that render project cards: `index.html`, `categories.html`, `insights.html`, `resources.html`, `system.html`, `profile.html`.
- `loadData()` (inline on every page) fetches `data.json`, builds `appData` and `allProjects`, and each project object gets a `tasks` array (all tasks from `appData.tasks` with matching `project` id).
- The "Open Project" buttons still call `alert(...)`. The tasks section inside each project card only shows the first few tasks and adds a "+X more" stub.

## Requirements
1. **Modal UI**
   - Add a reusable modal shell (backdrop + content panel) to each page.
   - Header must show project id + name, status badge, total tasks, urgent count, and a close button.
   - Include quick stats row (Total, Active, Review, Done, Urgent) and an overall progress bar.
   - Provide filters: status chips (All/Pending/Active/Review/Done), priority chips (All/High/Medium/Low), search box, and sort dropdown (Created newest/oldest, Priority, Status).
   - List ALL tasks for the selected project (no artificial limit). Grouping by status (e.g., Pending vs Completed) is fine, but the user has to be able to scroll through the entire list.
   - Each task row should show title, notes snippet, priority, status, createdAt, completedAt (if done), and use the existing badge/priority colors.
   - Footer actions: keep "Add Task" and add a placeholder "Spawn Agent" (calls `quickAction('Spawn Agent')` for now).

2. **Interactions**
   - `openProject(projectId, options)` must populate the modal and show it. Replace the current `alert` implementation.
   - Clicking the "+X more" summaries or the "View all" cta in the project card should call `openProject` for that project.
   - Modal closes via close button, backdrop click, or `Escape` key.
   - Preserve scroll position of the underlying page.

3. **Data handling**
   - Build a `projectLookup` map after `loadData()` so `openProject` can find the latest project object.
   - Filters/search operate on the in-memory `proj.tasks` array; do not refetch.
   - Use the shared helper functions that already exist in the page (`safeParseDate`, `formatAbsoluteTimestamp`, `getPriorityClass`, etc.). If you need a new helper, add it near the other helper definitions to keep things consistent.

4. **Pages to update**
   - Apply the same modal markup + scripts to **all six pages** listed above so that the behavior matches regardless of which section the user is viewing.
   - Keep the sidebar/header styles untouched.

5. **Styling**
   - Follow the existing luxury/glassmorphism palette. The modal should feel like the rest of the dashboard (blurred background, crimson accents, Orbitron/Rajdhani fonts).
   - Ensure the modal layout is responsive (max-width ~1200px, full-height scrollable content on small screens).

6. **Testing / validation**
   - After wiring everything, run a quick `python3` snippet (similar to earlier ones) to print task counts per project so you know the dataset you expect in the modal.
   - Describe in the summary how to manually test: e.g., open `index.html` locally, click "Open Project" on A2 or any project with many tasks, try filters/search/close, repeat on `categories.html`.

7. **Nice-to-haves (time permitting)**
   - Make the `+X more` placeholder rows in the card an inline button that calls `openProject`.
   - When the modal is open, allow switching between Pending vs Completed tabs without rerunning filters.

## Constraints
- Pure HTML/CSS/vanilla JS only (no frameworks, no build step).
- Do not rewrite the existing timeline component or the home layout that other agents touched.
- Keep code organized—new helper functions should live with the other helpers; modal-specific CSS should go near the bottom of the stylesheet for easy tracking.
- Keep behavior in other parts of the page exactly the same unless a change is required for the modal.

Deliverable: Working modal across all dashboard pages + summary describing the work, manual checks, and any follow-ups.
