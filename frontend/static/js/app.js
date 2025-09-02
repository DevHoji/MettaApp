/**
 * Smart To-Do Task Scheduler - Frontend JavaScript
 * Interactive functionality for the task scheduler application
 *
 * Features:
 * - Task management (CRUD operations)
 * - Real-time UI updates
 * - MeTTa AI integration
 * - Professional user experience
 */

class TaskScheduler {
    constructor() {
        this.tasks = [];
        this.currentFilter = 'all';
        this.apiBase = '/api';
        this.init();
    }

    /**
     * Initialize the application
     */
    init() {
        this.setupEventListeners();
        this.loadTasks();
        this.updateStats();
        this.loadNextTaskRecommendation();
        this.setupProgressRing();

        // Set default deadline to tomorrow
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        document.getElementById('task-deadline').value = tomorrow.toISOString().split('T')[0];

        console.log('Smart Task Scheduler initialized with MeTTa AI');
    }

    /**
     * Setup event listeners for UI interactions
     */
    setupEventListeners() {
        // Add task form submission
        document.getElementById('add-task-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addTask();
        });

        // Refresh tasks button
        document.getElementById('refresh-tasks').addEventListener('click', () => {
            this.loadTasks();
            this.showToast('Tasks refreshed', 'info');
        });

        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.setFilter(e.target.dataset.filter);
            });
        });

        // Start next task button
        document.getElementById('start-next-task').addEventListener('click', () => {
            this.startNextTask();
        });

        // Modal close
        document.querySelector('.modal-close').addEventListener('click', () => {
            this.closeModal();
        });

        // Close modal on backdrop click
        document.getElementById('task-modal').addEventListener('click', (e) => {
            if (e.target.id === 'task-modal') {
                this.closeModal();
            }
        });

        // Auto-refresh every 30 seconds
        setInterval(() => {
            this.loadTasks();
            this.updateStats();
            this.loadNextTaskRecommendation();
        }, 30000);
    }

    /**
     * Setup progress ring animation
     */
    setupProgressRing() {
        const circle = document.querySelector('.progress-ring-circle');
        const radius = circle.r.baseVal.value;
        const circumference = radius * 2 * Math.PI;

        circle.style.strokeDasharray = `${circumference} ${circumference}`;
        circle.style.strokeDashoffset = circumference;

        // Add gradient definition
        const svg = document.querySelector('.progress-ring');
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        const gradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
        gradient.id = 'progressGradient';
        gradient.innerHTML = `
            <stop offset="0%" style="stop-color:#6366f1;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#8b5cf6;stop-opacity:1" />
        `;
        defs.appendChild(gradient);
        svg.appendChild(defs);
    }

    /**
     * Update progress ring based on completion percentage
     */
    updateProgressRing(percentage) {
        const circle = document.querySelector('.progress-ring-circle');
        const radius = circle.r.baseVal.value;
        const circumference = radius * 2 * Math.PI;
        const offset = circumference - (percentage / 100) * circumference;

        circle.style.strokeDashoffset = offset;
        circle.classList.add('active');

        document.getElementById('progress-percentage').textContent = `${Math.round(percentage)}%`;
    }

    /**
     * Show loading overlay
     */
    showLoading() {
        document.getElementById('loading-overlay').classList.add('active');
    }

    /**
     * Hide loading overlay
     */
    hideLoading() {
        document.getElementById('loading-overlay').classList.remove('active');
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;

        document.getElementById('toast-container').appendChild(toast);

        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 100);

        // Remove after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    /**
     * Make API request with error handling
     */
    async apiRequest(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.apiBase}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'API request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            this.showToast(error.message, 'error');
            throw error;
        }
    }

    /**
     * Load all tasks from the backend
     */
    async loadTasks() {
        try {
            const response = await this.apiRequest('/tasks');
            this.tasks = response.tasks || [];
            this.renderTasks();
            this.updateDependencyOptions();
        } catch (error) {
            console.error('Error loading tasks:', error);
            this.tasks = [];
            this.renderTasks();
        }
    }

    /**
     * Add a new task
     */
    async addTask() {
        const form = document.getElementById('add-task-form');
        const formData = new FormData(form);

        const taskData = {
            description: formData.get('description'),
            deadline: formData.get('deadline'),
            priority: formData.get('priority'),
            dependencies: Array.from(document.getElementById('task-dependencies').selectedOptions)
                .map(option => option.value)
        };

        // Validate form data
        if (!taskData.description || !taskData.deadline || !taskData.priority) {
            this.showToast('Please fill in all required fields', 'error');
            return;
        }

        this.showLoading();

        try {
            const response = await this.apiRequest('/tasks', {
                method: 'POST',
                body: JSON.stringify(taskData)
            });

            this.showToast(response.message, 'success');
            form.reset();

            // Reset deadline to tomorrow
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            document.getElementById('task-deadline').value = tomorrow.toISOString().split('T')[0];

            await this.loadTasks();
            await this.updateStats();
            await this.loadNextTaskRecommendation();

        } catch (error) {
            console.error('Error adding task:', error);
        } finally {
            this.hideLoading();
        }
    }

    /**
     * Complete a task
     */
    async completeTask(taskId) {
        this.showLoading();

        try {
            const response = await this.apiRequest(`/tasks/${taskId}/complete`, {
                method: 'POST'
            });

            this.showToast(response.message, 'success');
            await this.loadTasks();
            await this.updateStats();
            await this.loadNextTaskRecommendation();

        } catch (error) {
            console.error('Error completing task:', error);
        } finally {
            this.hideLoading();
        }
    }

    /**
     * Delete a task
     */
    async deleteTask(taskId) {
        if (!confirm('Are you sure you want to delete this task?')) {
            return;
        }

        this.showLoading();

        try {
            const response = await this.apiRequest(`/tasks/${taskId}`, {
                method: 'DELETE'
            });

            this.showToast(response.message, 'success');
            await this.loadTasks();
            await this.updateStats();
            await this.loadNextTaskRecommendation();

        } catch (error) {
            console.error('Error deleting task:', error);
        } finally {
            this.hideLoading();
        }
    }

    /**
     * Load next task recommendation from MeTTa AI
     */
    async loadNextTaskRecommendation() {
        try {
            const response = await this.apiRequest('/next-task');
            const nextTaskId = response.next_task;

            const descriptionElement = document.getElementById('next-task-description');
            const startButton = document.getElementById('start-next-task');

            if (nextTaskId) {
                const task = this.tasks.find(t => t.id === nextTaskId);
                if (task) {
                    descriptionElement.innerHTML = `
                        <strong>${task.description}</strong><br>
                        <small>Priority: ${task.priority} | Deadline: ${this.formatDate(task.deadline)}</small>
                    `;
                    startButton.style.display = 'block';
                    startButton.dataset.taskId = nextTaskId;
                } else {
                    descriptionElement.textContent = 'Task details not found';
                    startButton.style.display = 'none';
                }
            } else {
                descriptionElement.innerHTML = `
                    <em>No tasks available or all dependencies not met</em><br>
                    <small>Add more tasks or complete dependencies to get recommendations</small>
                `;
                startButton.style.display = 'none';
            }
        } catch (error) {
            console.error('Error loading next task recommendation:', error);
            document.getElementById('next-task-description').textContent = 'Unable to load recommendation';
        }
    }

    /**
     * Start the next recommended task
     */
    async startNextTask() {
        const taskId = document.getElementById('start-next-task').dataset.taskId;
        if (taskId) {
            await this.completeTask(taskId);
        }
    }

    /**
     * Update statistics display
     */
    async updateStats() {
        try {
            const response = await this.apiRequest('/stats');
            const stats = response.stats;

            // Update header stats
            document.getElementById('total-tasks').textContent = stats.total_tasks;
            document.getElementById('completed-tasks').textContent = stats.completed_tasks;
            document.getElementById('pending-tasks').textContent = stats.pending_tasks;

            // Update progress section
            document.getElementById('progress-completed').textContent = stats.completed_tasks;
            document.getElementById('progress-pending').textContent = stats.pending_tasks;

            // Update progress ring
            this.updateProgressRing(stats.completion_percentage);

        } catch (error) {
            console.error('Error updating stats:', error);
        }
    }

    /**
     * Render tasks in the UI
     */
    renderTasks() {
        const taskList = document.getElementById('task-list');
        const filteredTasks = this.getFilteredTasks();

        if (filteredTasks.length === 0) {
            taskList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-tasks"></i>
                    <h3>No tasks found</h3>
                    <p>Add your first task to get started with intelligent scheduling</p>
                </div>
            `;
            return;
        }

        taskList.innerHTML = filteredTasks.map(task => this.createTaskElement(task)).join('');

        // Add event listeners to task elements
        this.attachTaskEventListeners();
    }

    /**
     * Create HTML element for a task
     */
    createTaskElement(task) {
        const isCompleted = task.completed;
        const isOverdue = !isCompleted && this.isOverdue(task.deadline);
        const isDueSoon = !isCompleted && !isOverdue && this.isDueSoon(task.deadline);

        const dependencyText = task.dependencies.length > 0
            ? `<div class="task-dependencies">
                 <i class="fas fa-link"></i>
                 <span class="dependency-count">${task.dependencies.length}</span>
                 dependencies
               </div>`
            : '';

        return `
            <div class="task-item ${isCompleted ? 'completed' : ''}" data-task-id="${task.id}">
                <div class="task-checkbox ${isCompleted ? 'checked' : ''}"
                     onclick="taskScheduler.toggleTask('${task.id}', ${!isCompleted})">
                    ${isCompleted ? '<i class="fas fa-check"></i>' : ''}
                </div>

                <div class="task-content">
                    <div class="task-description">${this.escapeHtml(task.description)}</div>
                    <div class="task-meta">
                        <div class="task-priority ${task.priority.toLowerCase()}">
                            ${this.getPriorityIcon(task.priority)} ${task.priority}
                        </div>
                        <div class="task-deadline ${isOverdue ? 'overdue' : isDueSoon ? 'due-soon' : ''}">
                            <i class="fas fa-calendar"></i>
                            ${this.formatDate(task.deadline)}
                            ${task.days_until_deadline !== undefined ?
                                `(${task.days_until_deadline} days)` : ''}
                        </div>
                        ${dependencyText}
                    </div>
                </div>

                <div class="task-actions">
                    <button class="task-action-btn info" onclick="taskScheduler.showTaskDetails('${task.id}')"
                            title="View Details">
                        <i class="fas fa-info"></i>
                    </button>
                    <button class="task-action-btn delete" onclick="taskScheduler.deleteTask('${task.id}')"
                            title="Delete Task">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Attach event listeners to task elements
     */
    attachTaskEventListeners() {
        // Task item click to show details
        document.querySelectorAll('.task-item').forEach(item => {
            item.addEventListener('click', (e) => {
                // Don't trigger if clicking on buttons or checkbox
                if (e.target.closest('.task-actions') || e.target.closest('.task-checkbox')) {
                    return;
                }

                const taskId = item.dataset.taskId;
                this.showTaskDetails(taskId);
            });
        });
    }

    /**
     * Toggle task completion status
     */
    async toggleTask(taskId, complete) {
        if (complete) {
            await this.completeTask(taskId);
        }
        // Note: We don't handle uncompleting tasks as it's not in the requirements
    }

    /**
     * Show task details in modal
     */
    showTaskDetails(taskId) {
        const task = this.tasks.find(t => t.id === taskId);
        if (!task) return;

        const modal = document.getElementById('task-modal');
        const modalTitle = document.getElementById('modal-title');
        const modalBody = document.getElementById('modal-body');

        modalTitle.textContent = task.description;

        const dependenciesHtml = task.dependencies.length > 0
            ? `<div class="detail-section">
                 <h4>Dependencies</h4>
                 <ul>
                   ${task.dependencies.map(depId => {
                       const depTask = this.tasks.find(t => t.id === depId);
                       return `<li>${depTask ? depTask.description : depId}</li>`;
                   }).join('')}
                 </ul>
               </div>`
            : '<div class="detail-section"><h4>Dependencies</h4><p>No dependencies</p></div>';

        modalBody.innerHTML = `
            <div class="task-details">
                <div class="detail-section">
                    <h4>Priority</h4>
                    <div class="task-priority ${task.priority.toLowerCase()}">
                        ${this.getPriorityIcon(task.priority)} ${task.priority}
                    </div>
                </div>

                <div class="detail-section">
                    <h4>Deadline</h4>
                    <p>${this.formatDate(task.deadline)}
                       ${task.days_until_deadline !== undefined ?
                         `(${task.days_until_deadline} days remaining)` : ''}</p>
                </div>

                <div class="detail-section">
                    <h4>Status</h4>
                    <p>${task.completed ? '✅ Completed' : '⏳ Pending'}</p>
                </div>

                ${dependenciesHtml}

                <div class="detail-section">
                    <h4>Task ID</h4>
                    <p><code>${task.id}</code></p>
                </div>
            </div>
        `;

        modal.classList.add('active');
    }

    /**
     * Close modal
     */
    closeModal() {
        document.getElementById('task-modal').classList.remove('active');
    }

    /**
     * Set task filter
     */
    setFilter(filter) {
        this.currentFilter = filter;

        // Update active filter button
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-filter="${filter}"]`).classList.add('active');

        // Re-render tasks with new filter
        this.renderTasks();
    }

    /**
     * Get filtered tasks based on current filter
     */
    getFilteredTasks() {
        let filtered = [...this.tasks];

        switch (this.currentFilter) {
            case 'pending':
                filtered = filtered.filter(task => !task.completed);
                break;
            case 'completed':
                filtered = filtered.filter(task => task.completed);
                break;
            case 'high':
                filtered = filtered.filter(task => task.priority === 'High');
                break;
            case 'all':
            default:
                // No filtering needed
                break;
        }

        // Sort tasks: incomplete first, then by priority, then by deadline
        return filtered.sort((a, b) => {
            // Completed tasks go to bottom
            if (a.completed !== b.completed) {
                return a.completed ? 1 : -1;
            }

            // Sort by priority (High=1, Medium=2, Low=3)
            const priorityOrder = { 'High': 1, 'Medium': 2, 'Low': 3 };
            const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
            if (priorityDiff !== 0) return priorityDiff;

            // Sort by deadline
            return new Date(a.deadline) - new Date(b.deadline);
        });
    }

    /**
     * Update dependency options in the form
     */
    updateDependencyOptions() {
        const select = document.getElementById('task-dependencies');
        const incompleteTasks = this.tasks.filter(task => !task.completed);

        select.innerHTML = incompleteTasks.map(task =>
            `<option value="${task.id}">${task.description}</option>`
        ).join('');
    }

    /**
     * Utility function to check if a date is overdue
     */
    isOverdue(dateString) {
        const deadline = new Date(dateString);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        deadline.setHours(0, 0, 0, 0);
        return deadline < today;
    }

    /**
     * Utility function to check if a date is due soon (within 3 days)
     */
    isDueSoon(dateString) {
        const deadline = new Date(dateString);
        const today = new Date();
        const threeDaysFromNow = new Date(today.getTime() + (3 * 24 * 60 * 60 * 1000));

        today.setHours(0, 0, 0, 0);
        deadline.setHours(0, 0, 0, 0);
        threeDaysFromNow.setHours(0, 0, 0, 0);

        return deadline >= today && deadline <= threeDaysFromNow;
    }

    /**
     * Format date for display
     */
    formatDate(dateString) {
        const date = new Date(dateString);
        const options = {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        };
        return date.toLocaleDateString('en-US', options);
    }

    /**
     * Get priority icon
     */
    getPriorityIcon(priority) {
        switch (priority) {
            case 'High': return '🔴';
            case 'Medium': return '🟡';
            case 'Low': return '🟢';
            default: return '⚪';
        }
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Get task statistics for display
     */
    getTaskStats() {
        const total = this.tasks.length;
        const completed = this.tasks.filter(task => task.completed).length;
        const pending = total - completed;
        const completionPercentage = total > 0 ? (completed / total) * 100 : 0;

        return {
            total,
            completed,
            pending,
            completionPercentage
        };
    }

    /**
     * Handle keyboard shortcuts
     */
    handleKeyboardShortcuts(event) {
        // Ctrl/Cmd + Enter to add task
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            const form = document.getElementById('add-task-form');
            if (document.activeElement && form.contains(document.activeElement)) {
                event.preventDefault();
                this.addTask();
            }
        }

        // Escape to close modal
        if (event.key === 'Escape') {
            this.closeModal();
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.taskScheduler = new TaskScheduler();

    // Add keyboard shortcuts
    document.addEventListener('keydown', (event) => {
        window.taskScheduler.handleKeyboardShortcuts(event);
    });

    // Add some helpful console messages
    console.log('🧠 Smart Task Scheduler powered by MeTTa AI');
    console.log('💡 Features: Intelligent scheduling, dependency management, real-time recommendations');
    console.log('🚀 Ready to optimize your productivity!');
});

// Add CSS for modal details
const additionalStyles = `
    .task-details {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }

    .detail-section h4 {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .detail-section p {
        color: var(--text-secondary);
        margin: 0;
    }

    .detail-section ul {
        margin: 0;
        padding-left: 1.5rem;
        color: var(--text-secondary);
    }

    .detail-section code {
        background: var(--bg-secondary);
        padding: 0.25rem 0.5rem;
        border-radius: var(--radius-sm);
        font-family: 'Monaco', 'Menlo', monospace;
        font-size: 0.75rem;
    }
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);
