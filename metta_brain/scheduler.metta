; Smart To-Do Task Scheduler - MeTTa Brain
; Core reasoning engine for intelligent task scheduling

; Task representation structure
; (task TaskID Description "Task description" Deadline "YYYY-MM-DD" Priority Level Dependencies (TaskID1 TaskID2...))

; Priority levels (lower number = higher priority)
(priority High 1)
(priority Medium 2)
(priority Low 3)

; Task status tracking
(status NotStarted 0)
(status InProgress 1)
(status Completed 2)

; Core query functions for task attributes
(= (getDescription $task)
   (match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps) $desc))

(= (getDeadline $task)
   (match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps) $deadline))

(= (getPriority $task)
   (match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps) $priority))

(= (getDependencies $task)
   (match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps) $deps))

; Get priority weight for sorting
(= (getPriorityWeight $priority)
   (match &self (priority $priority $weight) $weight))

; Check if task has no dependencies (can be started immediately)
(= (hasNoDependencies $task)
   (let $deps (getDependencies $task)
        (if (== $deps ()) True False)))

; Check if all dependencies are completed
(= (dependenciesCompleted $task)
   (let $deps (getDependencies $task)
        (if (== $deps ())
            True
            (allCompleted $deps))))

; Helper function to check if all tasks in list are completed
(= (allCompleted ())
   True)
(= (allCompleted ($head . $tail))
   (if (isCompleted $head)
       (allCompleted $tail)
       False))

; Check if a task is completed
(= (isCompleted $task)
   (match &self (taskStatus $task Completed) True))

; Get all tasks that are ready to be executed (dependencies met, not completed)
(= (getReadyTasks)
   (match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps)
          (if (and (dependenciesCompleted $task) (not (isCompleted $task)))
              $task
              ())))

; Sort tasks by priority and deadline
(= (sortTasksByPriority $tasks)
   (sortTasks $tasks))

; Basic task sorting implementation
(= (sortTasks ())
   ())
(= (sortTasks ($task))
   ($task))
(= (sortTasks ($task1 $task2 . $rest))
   (let $priority1 (getPriorityWeight (getPriority $task1))
        (let $priority2 (getPriorityWeight (getPriority $task2))
             (if (< $priority1 $priority2)
                 (cons $task1 (sortTasks ($task2 . $rest)))
                 (cons $task2 (sortTasks ($task1 . $rest)))))))

; Main scheduling algorithm - returns optimal task order
(= (scheduleTasks)
   (let $readyTasks (getReadyTasks)
        (sortTasksByPriority $readyTasks)))

; Get next recommended task
(= (getNextTask)
   (let $schedule (scheduleTasks)
        (if (== $schedule ())
            NoTasksAvailable
            (car $schedule))))

; Add new task to the system
(= (addTask $taskId $description $deadline $priority $dependencies)
   (add-atom &self (task $taskId Description $description Deadline $deadline Priority $priority Dependencies $dependencies)))

; Update task status
(= (updateTaskStatus $task $status)
   (add-atom &self (taskStatus $task $status)))

; Mark task as completed
(= (completeTask $task)
   (updateTaskStatus $task Completed))

; Get task completion percentage
(= (getCompletionPercentage)
   (let $allTasks (getAllTasks)
        (let $completedTasks (getCompletedTasks)
             (if (== $allTasks ())
                 0
                 (/ (length $completedTasks) (length $allTasks))))))

; Get all tasks in the system
(= (getAllTasks)
   (match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps) $task))

; Get completed tasks
(= (getCompletedTasks)
   (match &self (taskStatus $task Completed) $task))

; Check for circular dependencies
(= (hasCircularDependency $task $visited)
   (if (member $task $visited)
       True
       (let $deps (getDependencies $task)
            (checkCircularInDeps $deps (cons $task $visited)))))

(= (checkCircularInDeps () $visited)
   False)
(= (checkCircularInDeps ($dep . $rest) $visited)
   (if (hasCircularDependency $dep $visited)
       True
       (checkCircularInDeps $rest $visited)))

; Validate task before adding
(= (validateTask $taskId $dependencies)
   (not (hasCircularDependency $taskId $dependencies)))

; Advanced scheduling features for enhanced intelligence

; Calculate task urgency based on deadline proximity
(= (getUrgencyScore $task)
   (let $deadline (getDeadline $task)
        (let $daysLeft (days-until-deadline $deadline)
             (if (< $daysLeft 0) 10      ; Overdue - highest urgency
                 (if (< $daysLeft 1) 8   ; Due today
                     (if (< $daysLeft 3) 6   ; Due within 3 days
                         (if (< $daysLeft 7) 4   ; Due within a week
                             2)))))))    ; More than a week

; Enhanced scheduling that considers both priority and urgency
(= (getTaskScore $task)
   (let $priorityWeight (getPriorityWeight (getPriority $task))
        (let $urgencyScore (getUrgencyScore $task)
             (+ (* $priorityWeight 3) $urgencyScore))))

; Get tasks sorted by comprehensive scoring
(= (getOptimalTaskOrder)
   (let $readyTasks (getReadyTasks)
        (sortTasksByScore $readyTasks)))

; Sort tasks by their calculated scores
(= (sortTasksByScore ())
   ())
(= (sortTasksByScore ($task))
   ($task))
(= (sortTasksByScore ($task1 $task2 . $rest))
   (let $score1 (getTaskScore $task1)
        (let $score2 (getTaskScore $task2)
             (if (> $score1 $score2)
                 (cons $task1 (sortTasksByScore ($task2 . $rest)))
                 (cons $task2 (sortTasksByScore ($task1 . $rest)))))))

; Get overdue tasks for alerts
(= (getOverdueTasks)
   (match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps)
          (if (< (days-until-deadline $deadline) 0) $task ())))

; Get tasks due today
(= (getTasksDueToday)
   (match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps)
          (if (== (days-until-deadline $deadline) 0) $task ())))

; Get tasks due within specified days
(= (getTasksDueWithin $days)
   (match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps)
          (if (and (<= (days-until-deadline $deadline) $days)
                   (>= (days-until-deadline $deadline) 0))
              $task ())))

; Calculate project completion estimate
(= (getProjectCompletionDays)
   (let $allTasks (getAllTasks)
        (let $pendingTasks (getPendingTasks)
             (if (== $pendingTasks ())
                 0
                 (estimateCompletionTime $pendingTasks)))))

; Get pending (not completed) tasks
(= (getPendingTasks)
   (match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps)
          (if (not (isCompleted $task)) $task ())))

; Estimate completion time based on task complexity
(= (estimateCompletionTime $tasks)
   (length $tasks))  ; Simple estimation - can be enhanced

; Get task statistics for analytics
(= (getTaskStatistics)
   (let $total (length (getAllTasks))
        (let $completed (length (getCompletedTasks))
             (let $pending (length (getPendingTasks))
                  (let $overdue (length (getOverdueTasks))
                       (Statistics Total $total Completed $completed Pending $pending Overdue $overdue))))))

; Find critical path (longest dependency chain)
(= (getCriticalPath)
   (findLongestDependencyChain (getAllTasks)))

; Helper function to find longest dependency chain
(= (findLongestDependencyChain $tasks)
   (findMaxDepthTask $tasks 0 ()))

(= (findMaxDepthTask () $maxDepth $longestPath)
   $longestPath)
(= (findMaxDepthTask ($task . $rest) $maxDepth $longestPath)
   (let $depth (getTaskDepth $task 0)
        (if (> $depth $maxDepth)
            (findMaxDepthTask $rest $depth ($task))
            (findMaxDepthTask $rest $maxDepth $longestPath))))

; Calculate depth of a task in dependency chain
(= (getTaskDepth $task $currentDepth)
   (let $deps (getDependencies $task)
        (if (== $deps ())
            $currentDepth
            (+ 1 (getMaxDepthFromDeps $deps $currentDepth)))))

(= (getMaxDepthFromDeps () $currentDepth)
   $currentDepth)
(= (getMaxDepthFromDeps ($dep . $rest) $currentDepth)
   (let $depDepth (getTaskDepth $dep $currentDepth)
        (let $restDepth (getMaxDepthFromDeps $rest $currentDepth)
             (if (> $depDepth $restDepth) $depDepth $restDepth))))

; Smart recommendation with explanation
(= (getRecommendationWithReason)
   (let $nextTask (getNextTask)
        (if (== $nextTask NoTasksAvailable)
            (NoRecommendation "All dependencies not met or no tasks available")
            (let $reason (getRecommendationReason $nextTask)
                 (Recommendation $nextTask $reason)))))

; Generate explanation for why a task is recommended
(= (getRecommendationReason $task)
   (let $priority (getPriority $task)
        (let $urgency (getUrgencyScore $task)
             (let $deps (getDependencies $task)
                  (if (== $deps ())
                      (concat-strings "High priority task with no dependencies, urgency score: " (toString $urgency))
                      (concat-strings "Dependencies completed, priority: " (toString $priority)))))))

; Productivity insights
(= (getProductivityInsights)
   (let $stats (getTaskStatistics)
        (let $criticalPath (getCriticalPath)
             (let $overdue (getOverdueTasks)
                  (ProductivityReport
                     Statistics $stats
                     CriticalPath $criticalPath
                     OverdueTasks $overdue
                     Recommendations (getProductivityRecommendations))))))

; Generate productivity recommendations
(= (getProductivityRecommendations)
   (let $overdue (getOverdueTasks)
        (if (> (length $overdue) 0)
            ("Focus on overdue tasks first" "Consider adjusting deadlines" "Break down large tasks")
            ("Good progress!" "Consider adding more challenging tasks" "Maintain current pace"))))
