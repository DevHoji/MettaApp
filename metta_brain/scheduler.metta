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
