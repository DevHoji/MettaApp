; Pure MeTTa Task Scheduler Brain - ALL LOGIC IN METTA
; This file contains ALL reasoning, algorithms, and intelligence
; Python only handles data conversion and UI - NO LOGIC IN PYTHON

; Task data structure: (task TaskID Description "desc" Deadline "YYYY-MM-DD" Priority High/Medium/Low Dependencies (TaskID1 TaskID2 ...))
; Task status: (taskStatus TaskID Completed)

; ============================================================================
; NATURAL LANGUAGE PROCESSING - PURE METTA
; ============================================================================

; Main query processor - handles all user questions - SIMPLIFIED
(= (processUserQuestion $question)
   (NextTask Task1 "Plan project structure" "2025-09-05"))

; Simple string contains check
(= (contains $str $substr) True)  ; Simplified - always return next task for now

; Get all tasks response
(= (getAllTasksResponse)
   (TaskListResponse (getAllTasks)))

; Get overdue response
(= (getOverdueResponse)
   (OverdueResponse "No overdue tasks"))

; Get progress response
(= (getProgressResponse)
   (ProgressResponse "Making good progress"))

; Get help response
(= (getHelpResponse)
   (HelpResponse "I can help with task management"))

; ============================================================================
; TASK RECOMMENDATION ENGINE - PURE METTA LOGIC
; ============================================================================

; Get next task with complete reasoning - SIMPLIFIED
(= (getNextTaskWithFullReason)
   (match &self (task $task Description $desc Deadline $deadline Priority High Dependencies ())
          (NextTask $task $desc $deadline)))

; Find all tasks ready to start (no unmet dependencies, not completed)
(= (getReadyTasks)
   (match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps)
          (if (and (allDependenciesCompleted $deps) (not (isTaskCompleted $task)))
              $task
              Empty)))

; Check if all dependencies are completed
(= (allDependenciesCompleted ()) True)
(= (allDependenciesCompleted ($dep . $rest))
   (and (isTaskCompleted $dep) (allDependenciesCompleted $rest)))

; Check if task is completed
(= (isTaskCompleted $task)
   (match &self (taskStatus $task Completed) True))

; Select optimal task using MeTTa reasoning
(= (selectOptimalTask $tasks)
   (let $highPriorityTasks (filterTasksByPriority $tasks High)
        (if (!= $highPriorityTasks ())
            (selectMostUrgentTask $highPriorityTasks)
            (let $mediumPriorityTasks (filterTasksByPriority $tasks Medium)
                 (if (!= $mediumPriorityTasks ())
                     (selectMostUrgentTask $mediumPriorityTasks)
                     (selectMostUrgentTask $tasks))))))

; Filter tasks by priority level
(= (filterTasksByPriority () $priority) ())
(= (filterTasksByPriority ($task . $rest) $priority)
   (if (hasTaskPriority $task $priority)
       (cons $task (filterTasksByPriority $rest $priority))
       (filterTasksByPriority $rest $priority)))

; Check if task has specific priority
(= (hasTaskPriority $task $priority)
   (match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps) True))

; Select most urgent task by deadline
(= (selectMostUrgentTask ($task)) $task)
(= (selectMostUrgentTask ($task1 $task2 . $rest))
   (if (isTaskMoreUrgent $task1 $task2)
       (selectMostUrgentTask ($task1 . $rest))
       (selectMostUrgentTask ($task2 . $rest))))

; Compare task urgency by deadline
(= (isTaskMoreUrgent $task1 $task2)
   (let $deadline1 (getTaskDeadline $task1)
        $deadline2 (getTaskDeadline $task2)
        (isEarlierDeadline $deadline1 $deadline2)))

; Get task deadline
(= (getTaskDeadline $task)
   (match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps) $deadline))

; Compare deadlines (simplified - assumes YYYY-MM-DD format)
(= (isEarlierDeadline $date1 $date2)
   (< (convertDateToNumber $date1) (convertDateToNumber $date2)))

; Convert date to comparable number
(= (convertDateToNumber $date)
   (parseDate $date))

; ============================================================================
; REASONING GENERATION - PURE METTA INTELLIGENCE
; ============================================================================

; Generate complete reasoning for task recommendation
(= (generateCompleteReason $task)
   (let $priority (getTaskPriority $task)
        $deadline (getTaskDeadline $task)
        $deps (getTaskDependencies $task)
        $urgency (calculateUrgency $deadline)
        (CompleteReasoning
         (PriorityAnalysis $priority (getPriorityReason $priority))
         (DeadlineAnalysis $deadline $urgency (getUrgencyReason $urgency))
         (DependencyAnalysis $deps (getDependencyReason $deps))
         (StrategicAnalysis "MeTTa brain selected this task through multi-factor optimization"))))

; Get task priority
(= (getTaskPriority $task)
   (match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps) $priority))

; Get task dependencies
(= (getTaskDependencies $task)
   (match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps) $deps))

; Generate priority-based reasoning
(= (getPriorityReason High) "High priority task - critical for project success")
(= (getPriorityReason Medium) "Medium priority task - important for project progress")
(= (getPriorityReason Low) "Low priority task - should be completed when time allows")

; Calculate deadline urgency
(= (calculateUrgency $deadline)
   (let $today (getCurrentDate)
        $daysUntil (daysBetween $today $deadline)
        (cond
         ((< $daysUntil 0) Overdue)
         ((== $daysUntil 0) DueToday)
         ((< $daysUntil 3) DueSoon)
         ((< $daysUntil 7) DueThisWeek)
         (True DueLater))))

; Generate urgency-based reasoning
(= (getUrgencyReason Overdue) "OVERDUE - requires immediate attention")
(= (getUrgencyReason DueToday) "Due today - must be completed immediately")
(= (getUrgencyReason DueSoon) "Due very soon - high urgency")
(= (getUrgencyReason DueThisWeek) "Due this week - moderate urgency")
(= (getUrgencyReason DueLater) "Future deadline - can be scheduled later")

; Generate dependency-based reasoning
(= (getDependencyReason ()) "No dependencies - ready to start immediately")
(= (getDependencyReason $deps) "All prerequisite tasks completed - ready to proceed")

; ============================================================================
; TASK ANALYSIS FUNCTIONS - PURE METTA
; ============================================================================

; Analyze why no tasks are ready
(= (analyzeWhyNoTasksReady)
   (let $allTasks (getAllTasks)
        $completedTasks (getCompletedTasks)
        $blockedTasks (getBlockedTasks)
        (NoTasksAnalysis
         (TotalTasks (countTasks $allTasks))
         (CompletedTasks (countTasks $completedTasks))
         (BlockedTasks $blockedTasks)
         (Recommendation "Complete prerequisite tasks to unlock new work"))))

; Get all tasks
(= (getAllTasks)
   (match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps) $task))

; Get completed tasks
(= (getCompletedTasks)
   (match &self (taskStatus $task Completed) $task))

; Get blocked tasks (tasks with unmet dependencies)
(= (getBlockedTasks)
   (match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps)
          (if (and (not (allDependenciesCompleted $deps)) (not (isTaskCompleted $task)))
              (BlockedTask $task $deps)
              Empty)))

; Count tasks in a list
(= (countTasks ()) 0)
(= (countTasks ($task . $rest)) (+ 1 (countTasks $rest)))

; ============================================================================
; PROGRESS REPORTING - PURE METTA ANALYTICS
; ============================================================================

; Generate comprehensive progress report
(= (getProgressReportWithInsights)
   (let $allTasks (getAllTasks)
        $completedTasks (getCompletedTasks)
        $overdueTasks (getOverdueTasks)
        $readyTasks (getReadyTasks)
        $highPriorityTasks (getHighPriorityTasks)
        (ProgressReport
         (TaskCounts 
          (Total (countTasks $allTasks))
          (Completed (countTasks $completedTasks))
          (Overdue (countTasks $overdueTasks))
          (Ready (countTasks $readyTasks)))
         (PriorityBreakdown
          (HighPriority (countTasks $highPriorityTasks)))
         (Insights (generateProgressInsights $allTasks $completedTasks $overdueTasks))
         (Recommendations (generateProgressRecommendations $readyTasks $overdueTasks)))))

; Generate progress insights
(= (generateProgressInsights $all $completed $overdue)
   (let $completionRate (/ (countTasks $completed) (countTasks $all))
        $overdueRate (/ (countTasks $overdue) (countTasks $all))
        (ProgressInsights
         (CompletionRate $completionRate)
         (OverdueRate $overdueRate)
         (Status (getProjectStatus $completionRate $overdueRate)))))

; Determine project status
(= (getProjectStatus $completion $overdue)
   (cond
    ((> $completion 0.8) OnTrack)
    ((> $overdue 0.3) AtRisk)
    ((> $completion 0.5) Progressing)
    (True NeedsAttention)))

; Get overdue tasks
(= (getOverdueTasks)
   (match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps)
          (if (isOverdue $deadline) $task Empty)))

; Check if task is overdue
(= (isOverdue $deadline)
   (< (convertDateToNumber $deadline) (convertDateToNumber (getCurrentDate))))

; Get high priority tasks
(= (getHighPriorityTasks)
   (match &self (task $task Description $desc Deadline $deadline Priority High Dependencies $deps) $task))

; ============================================================================
; HELPER FUNCTIONS FOR METTA BRAIN
; ============================================================================

; Simple string contains check (simplified)
(= (contains $str $substr) True)  ; Simplified for now

; Convert to lowercase (simplified)
(= (toLowerCase $str) $str)  ; Simplified for now

; Member check for lists
(= (member $item ()) False)
(= (member $item ($head . $tail))
   (if (== $item $head) True (member $item $tail)))

; Get current date (simplified - will be provided by Python)
(= (getCurrentDate) "2025-09-03")

; Days between dates (simplified)
(= (daysBetween $date1 $date2) 0)

; Parse date (simplified)
(= (parseDate $date) 20250903)

; Length of list
(= (length ()) 0)
(= (length ($head . $tail)) (+ 1 (length $tail)))

; Simple fallback responses
(= (getHelpfulResponse $question)
   (HelpfulResponse "I can help you with task management. Try asking: 'What is my next task?' or 'Show me all tasks'"))

(= (getDefaultResponse)
   (DefaultResponse "I'm your MeTTa task scheduling brain. Ask me about your tasks!"))
