"""
MeTTa Bridge Module
Interface between Python backend and MeTTa reasoning engine

This module handles all communication between Python and MeTTa,
converting data formats and executing MeTTa reasoning functions.
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from hyperon import MeTTa, S, V, E, ValueAtom, OperationAtom
import json
import pickle


class MeTTaBridge:
    """Bridge class for MeTTa-Python integration"""

    def __init__(self):
        """Initialize MeTTa instance and load scheduler logic"""
        self.metta = MeTTa()
        self.task_counter = 0
        self.tasks_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'tasks.json')
        self.debug_mode = True  # Enable MeTTa debug output
        self._ensure_data_directory()
        self._load_scheduler_logic()
        self._register_python_functions()
        self._load_persisted_tasks()

    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        data_dir = os.path.dirname(self.tasks_file)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def _load_persisted_tasks(self):
        """Load tasks from file and restore to MeTTa space"""
        try:
            if os.path.exists(self.tasks_file):
                with open(self.tasks_file, 'r') as f:
                    tasks_data = json.load(f)

                # Restore tasks to MeTTa space
                for task_data in tasks_data.get('tasks', []):
                    task_atom = f'(task {task_data["id"]} Description "{task_data["description"]}" Deadline "{task_data["deadline"]}" Priority {task_data["priority"]} Dependencies ({" ".join(task_data["dependencies"])}))'
                    self.metta.run(task_atom)

                    # Restore completion status
                    if task_data.get('completed', False):
                        self.metta.run(f'(taskStatus {task_data["id"]} Completed)')

                self.task_counter = tasks_data.get('task_counter', 0)
                print(f"Loaded {len(tasks_data.get('tasks', []))} persisted tasks")
        except Exception as e:
            print(f"Error loading persisted tasks: {e}")

    def _save_tasks_to_file(self):
        """Save current tasks to file for persistence"""
        try:
            tasks = self.get_all_tasks()
            tasks_data = {
                'task_counter': self.task_counter,
                'tasks': tasks,
                'timestamp': datetime.now().isoformat()
            }

            with open(self.tasks_file, 'w') as f:
                json.dump(tasks_data, f, indent=2)

        except Exception as e:
            print(f"Error saving tasks to file: {e}")

    def _load_scheduler_logic(self):
        """Load MeTTa scheduler logic from file"""
        try:
            scheduler_path = os.path.join(os.path.dirname(__file__), '..', 'metta_brain', 'scheduler.metta')
            with open(scheduler_path, 'r') as f:
                scheduler_code = f.read()
            self.metta.run(scheduler_code)
            print("MeTTa scheduler logic loaded successfully")
        except Exception as e:
            print(f"Error loading scheduler logic: {e}")
            raise

    def _register_python_functions(self):
        """Register Python utility functions in MeTTa"""

        # Date comparison function
        def compare_dates(date1_str, date2_str):
            """Compare two date strings, return -1 if date1 < date2, 0 if equal, 1 if date1 > date2"""
            try:
                date1 = datetime.strptime(date1_str, "%Y-%m-%d")
                date2 = datetime.strptime(date2_str, "%Y-%m-%d")
                if date1 < date2:
                    return -1
                elif date1 > date2:
                    return 1
                else:
                    return 0
            except:
                return 0

        # Days until deadline function
        def days_until_deadline(deadline_str):
            """Calculate days until deadline"""
            try:
                deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
                today = datetime.now()
                delta = deadline - today
                return delta.days
            except:
                return 999  # Default to far future if parsing fails

        # Register functions in MeTTa
        self.metta.register_atom("compare-dates",
                                OperationAtom("compare-dates", compare_dates))
        self.metta.register_atom("days-until-deadline",
                                OperationAtom("days-until-deadline", days_until_deadline))

    def add_task(self, description: str, deadline: str, priority: str, dependencies: List[str] = None) -> Dict[str, Any]:
        """Add a new task to MeTTa knowledge base"""
        if dependencies is None:
            dependencies = []

        # Generate unique task ID
        self.task_counter += 1
        task_id = f"Task{self.task_counter}"

        # Validate dependencies exist
        for dep in dependencies:
            if not self._task_exists(dep):
                return {"success": False, "error": f"Dependency {dep} does not exist"}

        # Create MeTTa task atom
        deps_str = "(" + " ".join(dependencies) + ")" if dependencies else "()"
        task_atom = f'(task {task_id} Description "{description}" Deadline "{deadline}" Priority {priority} Dependencies {deps_str})'

        try:
            # Log MeTTa operation to terminal
            print(f"\n--- MeTTa Task Addition ---")
            print(f"\n{task_atom}")
            print(f"\n--- End Task Addition ---")

            # Add task to MeTTa space
            result = self.metta.run(task_atom)
            print(f"\nRaw MeTTa output: {result}")

            # Validate for circular dependencies
            validation_query = f'!(validateTask {task_id} {deps_str})'
            print(f"\n--- MeTTa Validation Query ---")
            print(f"\n{validation_query}")
            print(f"\n--- End Validation Query ---")

            validation_result = self.metta.run(validation_query)
            print(f"\nRaw MeTTa validation output: {validation_result}")

            if validation_result and validation_result[0] and not validation_result[0][0]:
                # Remove the invalid task
                remove_query = f'!(remove-atom &self {task_atom})'
                print(f"\n--- MeTTa Task Removal (Circular Dependency) ---")
                print(f"\n{remove_query}")
                print(f"\n--- End Task Removal ---")

                remove_result = self.metta.run(remove_query)
                print(f"\nRaw MeTTa removal output: {remove_result}")
                return {"success": False, "error": "Circular dependency detected"}

            # Save tasks to file for persistence
            self._save_tasks_to_file()

            return {
                "success": True,
                "task_id": task_id,
                "message": f"Task '{description}' added successfully"
            }
        except Exception as e:
            print(f"\nMeTTa Task Addition Error: {str(e)}")
            return {"success": False, "error": str(e)}

    def _task_exists(self, task_id: str) -> bool:
        """Check if a task exists in the knowledge base"""
        try:
            result = self.metta.run(f'!(match &self (task {task_id} Description $desc Deadline $deadline Priority $priority Dependencies $deps) {task_id})')
            return bool(result and result[0])
        except:
            return False

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Retrieve all tasks from MeTTa knowledge base"""
        try:
            # Get all tasks
            result = self.metta.run('!(match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps) ($task $desc $deadline $priority $deps))')

            tasks = []
            if result and result[0]:
                for task_data in result[0]:
                    if hasattr(task_data, 'get_children') and len(task_data.get_children()) >= 5:
                        children = task_data.get_children()
                        task_id = str(children[0])
                        description = str(children[1]).strip('"')
                        deadline = str(children[2]).strip('"')
                        priority = str(children[3])

                        # Parse dependencies
                        deps_atom = children[4]
                        dependencies = []
                        if hasattr(deps_atom, 'get_children'):
                            dependencies = [str(dep) for dep in deps_atom.get_children()]

                        # Check completion status
                        status_result = self.metta.run(f'!(match &self (taskStatus {task_id} $status) $status)')
                        is_completed = False
                        if status_result and status_result[0]:
                            is_completed = str(status_result[0][0]) == "Completed"

                        tasks.append({
                            "id": task_id,
                            "description": description,
                            "deadline": deadline,
                            "priority": priority,
                            "dependencies": dependencies,
                            "completed": is_completed,
                            "days_until_deadline": self._calculate_days_until_deadline(deadline)
                        })

            return tasks
        except Exception as e:
            print(f"Error getting tasks: {e}")
            return []

    def _calculate_days_until_deadline(self, deadline_str: str) -> int:
        """Calculate days until deadline"""
        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
            today = datetime.now()
            delta = deadline - today
            return delta.days
        except:
            return 999

    def get_scheduled_tasks(self) -> List[str]:
        """Get optimally scheduled task order from MeTTa"""
        try:
            result = self.metta.run('!(scheduleTasks)')
            if result and result[0]:
                return [str(task) for task in result[0]]
            return []
        except Exception as e:
            print(f"Error getting scheduled tasks: {e}")
            return []

    def get_next_task(self) -> Optional[str]:
        """Get the next recommended task"""
        try:
            result = self.metta.run('!(getNextTask)')
            if result and result[0] and str(result[0][0]) != "NoTasksAvailable":
                return str(result[0][0])
            return None
        except Exception as e:
            print(f"Error getting next task: {e}")
            return None

    def complete_task(self, task_id: str) -> Dict[str, Any]:
        """Mark a task as completed"""
        try:
            if not self._task_exists(task_id):
                return {"success": False, "error": "Task does not exist"}

            # Log MeTTa operation to terminal
            complete_query = f'!(completeTask {task_id})'
            print(f"\n--- MeTTa Task Completion ---")
            print(f"\n{complete_query}")
            print(f"\n--- End Task Completion ---")

            result = self.metta.run(complete_query)
            print(f"\nRaw MeTTa output: {result}")

            # Save tasks to file for persistence
            self._save_tasks_to_file()

            return {"success": True, "message": f"Task {task_id} marked as completed"}
        except Exception as e:
            print(f"\nMeTTa Task Completion Error: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_task_dependencies(self, task_id: str) -> List[str]:
        """Get dependencies for a specific task"""
        try:
            result = self.metta.run(f'!(getDependencies {task_id})')
            if result and result[0]:
                deps_atom = result[0][0]
                if hasattr(deps_atom, 'get_children'):
                    return [str(dep) for dep in deps_atom.get_children()]
            return []
        except Exception as e:
            print(f"Error getting dependencies: {e}")
            return []

    def get_completion_stats(self) -> Dict[str, Any]:
        """Get completion statistics"""
        try:
            all_tasks = self.get_all_tasks()
            completed_tasks = [task for task in all_tasks if task['completed']]

            total_count = len(all_tasks)
            completed_count = len(completed_tasks)
            completion_percentage = (completed_count / total_count * 100) if total_count > 0 else 0

            return {
                "total_tasks": total_count,
                "completed_tasks": completed_count,
                "pending_tasks": total_count - completed_count,
                "completion_percentage": round(completion_percentage, 1)
            }
        except Exception as e:
            print(f"Error getting completion stats: {e}")
            return {"total_tasks": 0, "completed_tasks": 0, "pending_tasks": 0, "completion_percentage": 0}

    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """Delete a task from the system"""
        try:
            if not self._task_exists(task_id):
                return {"success": False, "error": "Task does not exist"}

            # Check if other tasks depend on this task
            all_tasks = self.get_all_tasks()
            dependent_tasks = [task for task in all_tasks if task_id in task['dependencies']]

            if dependent_tasks:
                dependent_names = [task['description'] for task in dependent_tasks]
                return {
                    "success": False,
                    "error": f"Cannot delete task. The following tasks depend on it: {', '.join(dependent_names)}"
                }

            # Remove task and its status
            task_query = f'!(match &self (task {task_id} Description $desc Deadline $deadline Priority $priority Dependencies $deps) (task {task_id} Description $desc Deadline $deadline Priority $priority Dependencies $deps))'
            print(f"\n--- MeTTa Task Deletion Query ---")
            print(f"\n{task_query}")
            print(f"\n--- End Task Deletion Query ---")

            task_result = self.metta.run(task_query)
            print(f"\nRaw MeTTa task query output: {task_result}")

            if task_result and task_result[0]:
                task_atom = task_result[0][0]
                remove_query = f'!(remove-atom &self {task_atom})'
                print(f"\n--- MeTTa Task Removal ---")
                print(f"\n{remove_query}")
                print(f"\n--- End Task Removal ---")

                remove_result = self.metta.run(remove_query)
                print(f"\nRaw MeTTa removal output: {remove_result}")

            # Remove task status if exists
            status_query = f'!(match &self (taskStatus {task_id} $status) (taskStatus {task_id} $status))'
            print(f"\n--- MeTTa Status Deletion Query ---")
            print(f"\n{status_query}")
            print(f"\n--- End Status Deletion Query ---")

            status_result = self.metta.run(status_query)
            print(f"\nRaw MeTTa status query output: {status_result}")

            if status_result and status_result[0]:
                status_atom = status_result[0][0]
                status_remove_query = f'!(remove-atom &self {status_atom})'
                print(f"\n--- MeTTa Status Removal ---")
                print(f"\n{status_remove_query}")
                print(f"\n--- End Status Removal ---")

                status_remove_result = self.metta.run(status_remove_query)
                print(f"\nRaw MeTTa status removal output: {status_remove_result}")

            # Save tasks to file for persistence
            self._save_tasks_to_file()

            return {"success": True, "message": f"Task {task_id} deleted successfully"}
        except Exception as e:
            print(f"\nMeTTa Task Deletion Error: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_overdue_tasks(self) -> List[str]:
        """Get tasks that are overdue"""
        try:
            result = self.metta.run('!(getOverdueTasks)')
            if result and result[0]:
                return [str(task) for task in result[0]]
            return []
        except Exception as e:
            print(f"Error getting overdue tasks: {e}")
            return []

    def get_tasks_due_today(self) -> List[str]:
        """Get tasks due today"""
        try:
            result = self.metta.run('!(getTasksDueToday)')
            if result and result[0]:
                return [str(task) for task in result[0]]
            return []
        except Exception as e:
            print(f"Error getting tasks due today: {e}")
            return []

    def get_tasks_due_within(self, days: int) -> List[str]:
        """Get tasks due within specified number of days"""
        try:
            result = self.metta.run(f'!(getTasksDueWithin {days})')
            if result and result[0]:
                return [str(task) for task in result[0]]
            return []
        except Exception as e:
            print(f"Error getting tasks due within {days} days: {e}")
            return []

    def get_optimal_task_order(self) -> List[str]:
        """Get tasks ordered by optimal scoring (priority + urgency)"""
        try:
            result = self.metta.run('!(getOptimalTaskOrder)')
            if result and result[0]:
                return [str(task) for task in result[0]]
            return []
        except Exception as e:
            print(f"Error getting optimal task order: {e}")
            return []

    def get_recommendation_with_reason(self) -> Dict[str, Any]:
        """Get next task recommendation with explanation"""
        try:
            result = self.metta.run('!(getRecommendationWithReason)')
            if result and result[0]:
                recommendation = result[0][0]
                if hasattr(recommendation, 'get_children') and len(recommendation.get_children()) >= 2:
                    children = recommendation.get_children()
                    if str(children[0]) == "Recommendation":
                        task_id = str(children[1])
                        reason = str(children[2]) if len(children) > 2 else "Optimal choice based on priority and dependencies"
                        return {
                            "task_id": task_id,
                            "reason": reason,
                            "has_recommendation": True
                        }
                    elif str(children[0]) == "NoRecommendation":
                        return {
                            "task_id": None,
                            "reason": str(children[1]) if len(children) > 1 else "No tasks available",
                            "has_recommendation": False
                        }

            return {
                "task_id": None,
                "reason": "Unable to generate recommendation",
                "has_recommendation": False
            }
        except Exception as e:
            print(f"Error getting recommendation with reason: {e}")
            return {
                "task_id": None,
                "reason": "Error generating recommendation",
                "has_recommendation": False
            }

    def get_productivity_insights(self) -> Dict[str, Any]:
        """Get comprehensive productivity insights from MeTTa"""
        try:
            result = self.metta.run('!(getProductivityInsights)')
            if result and result[0]:
                # Parse the productivity report
                insights = {
                    "overdue_tasks": self.get_overdue_tasks(),
                    "tasks_due_today": self.get_tasks_due_today(),
                    "tasks_due_this_week": self.get_tasks_due_within(7),
                    "optimal_order": self.get_optimal_task_order(),
                    "recommendations": [
                        "Focus on high-priority tasks first",
                        "Complete dependencies before dependent tasks",
                        "Address overdue tasks immediately"
                    ]
                }
                return insights
            return {}
        except Exception as e:
            print(f"Error getting productivity insights: {e}")
            return {}

    def get_enhanced_stats(self) -> Dict[str, Any]:
        """Get enhanced statistics with urgency and insights"""
        try:
            basic_stats = self.get_completion_stats()
            overdue_count = len(self.get_overdue_tasks())
            due_today_count = len(self.get_tasks_due_today())
            due_this_week_count = len(self.get_tasks_due_within(7))

            return {
                **basic_stats,
                "overdue_tasks": overdue_count,
                "due_today": due_today_count,
                "due_this_week": due_this_week_count,
                "urgency_level": "high" if overdue_count > 0 else "medium" if due_today_count > 0 else "low"
            }
        except Exception as e:
            print(f"Error getting enhanced stats: {e}")
            return self.get_completion_stats()

    def execute_metta_query(self, query: str) -> Dict[str, Any]:
        """Execute raw MeTTa query and return both raw and processed results with proper terminal logging"""
        try:
            # Clean terminal logging like trainer's project
            print(f"\n--- MeTTa Query ---")
            print(f"\n{query}")
            print(f"\n--- End Query ---")

            # Execute the query
            raw_result = self.metta.run(query)

            # Log raw MeTTa output to terminal
            print(f"\nRaw MeTTa output: {raw_result}")

            # Process result for user-friendly display
            processed_result = self._process_metta_result(raw_result, query)

            # Create detailed debug information
            debug_info = {
                "query_type": self._identify_query_type(query),
                "execution_time": datetime.now().isoformat(),
                "raw_result_type": str(type(raw_result)),
                "raw_result_length": len(raw_result) if raw_result else 0,
                "has_results": bool(raw_result and raw_result[0]) if raw_result else False,
                "metta_space_size": self._get_metta_space_info()
            }

            return {
                "success": True,
                "query": query,
                "raw_result": str(raw_result),
                "processed_result": processed_result,
                "debug_info": debug_info,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            error_msg = f"Error executing MeTTa query: {e}"
            print(f"\nMeTTa Error: {error_msg}")

            return {
                "success": False,
                "query": query,
                "error": str(e),
                "error_type": str(type(e)),
                "timestamp": datetime.now().isoformat()
            }

    def _identify_query_type(self, query: str) -> str:
        """Identify the type of MeTTa query for debugging"""
        if "getNextTask" in query:
            return "Next Task Recommendation"
        elif "scheduleTasks" in query:
            return "Task Scheduling"
        elif "match" in query:
            return "Pattern Matching Query"
        elif "getOverdueTasks" in query:
            return "Overdue Task Query"
        elif "getDependencies" in query:
            return "Dependency Query"
        else:
            return "Generic Query"

    def _get_metta_space_info(self) -> Dict[str, Any]:
        """Get information about the current MeTTa space for debugging"""
        try:
            # Try to count tasks in the space
            all_tasks_result = self.metta.run('!(match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps) $task)')
            task_count = len(all_tasks_result[0]) if all_tasks_result and all_tasks_result[0] else 0

            # Try to count completed tasks
            completed_result = self.metta.run('!(match &self (taskStatus $task Completed) $task)')
            completed_count = len(completed_result[0]) if completed_result and completed_result[0] else 0

            return {
                "total_tasks": task_count,
                "completed_tasks": completed_count,
                "pending_tasks": task_count - completed_count
            }
        except Exception as e:
            return {"error": f"Could not get space info: {str(e)}"}

    def _process_metta_result(self, raw_result, query: str) -> str:
        """Process raw MeTTa result into user-friendly format with detailed reasoning"""
        try:
            if not raw_result or not raw_result[0]:
                # Check if we have any tasks at all
                all_tasks = self.get_all_tasks()
                if not all_tasks:
                    return "No tasks found in the system. Please add some tasks first to get recommendations and analysis."
                return "No results found for this specific query, but you have tasks in the system."

            # Handle different types of queries with detailed reasoning
            if "getNextTask" in query:
                if str(raw_result[0][0]) == "NoTasksAvailable":
                    # Provide detailed reasoning why no tasks are available
                    all_tasks = self.get_all_tasks()
                    pending_tasks = [t for t in all_tasks if not t.get('completed', False)]
                    if not pending_tasks:
                        return "🎉 Congratulations! All tasks are completed. No more tasks to work on."
                    else:
                        # Analyze why tasks aren't available
                        blocked_tasks = []
                        for task in pending_tasks:
                            if task['dependencies']:
                                incomplete_deps = []
                                for dep_id in task['dependencies']:
                                    dep_task = next((t for t in all_tasks if t['id'] == dep_id), None)
                                    if dep_task and not dep_task.get('completed', False):
                                        incomplete_deps.append(dep_task['description'])
                                if incomplete_deps:
                                    blocked_tasks.append(f"'{task['description']}' is waiting for: {', '.join(incomplete_deps)}")

                        if blocked_tasks:
                            return f"No tasks are ready to start. Here's why:\n" + "\n".join(f"• {reason}" for reason in blocked_tasks)
                        return "All pending tasks have unmet dependencies. Please check your task dependencies."
                else:
                    task_id = str(raw_result[0][0])
                    task = next((t for t in self.get_all_tasks() if t['id'] == task_id), None)
                    if task:
                        # Provide detailed reasoning for the recommendation
                        reasoning = self._generate_task_reasoning(task)
                        return f"🎯 **Next recommended task**: '{task['description']}'\n\n**Why this task?**\n{reasoning}\n\n📋 **Details**: Priority: {task['priority']}, Deadline: {task['deadline']}"
                    return f"Next recommended task: {task_id}"

            elif "scheduleTasks" in query:
                if raw_result[0]:
                    task_ids = [str(task) for task in raw_result[0]]
                    all_tasks = self.get_all_tasks()

                    # Create detailed schedule with reasoning
                    schedule_details = []
                    for i, task_id in enumerate(task_ids, 1):
                        task = next((t for t in all_tasks if t['id'] == task_id), None)
                        if task:
                            schedule_details.append(f"{i}. '{task['description']}' ({task['priority']} priority)")

                    reasoning = self._generate_schedule_reasoning(task_ids, all_tasks)
                    return f"📋 **Optimal Task Schedule**:\n" + "\n".join(schedule_details) + f"\n\n**Scheduling Logic**:\n{reasoning}"
                return "No tasks to schedule."

            elif "getOverdueTasks" in query:
                if raw_result[0]:
                    overdue_task_ids = [str(task) for task in raw_result[0]]
                    all_tasks = self.get_all_tasks()
                    overdue_details = []

                    for task_id in overdue_task_ids:
                        task = next((t for t in all_tasks if t['id'] == task_id), None)
                        if task:
                            days_overdue = abs(task.get('days_until_deadline', 0))
                            overdue_details.append(f"• '{task['description']}' - {days_overdue} days overdue ({task['priority']} priority)")

                    return f"⚠️ **Overdue Tasks** ({len(overdue_task_ids)} found):\n" + "\n".join(overdue_details) + "\n\n💡 **Recommendation**: Focus on these tasks immediately to get back on track."
                return "✅ Great news! No overdue tasks found."

            elif "match" in query and "task" in query:
                # Handle task queries with detailed information
                tasks = []
                completed_count = 0

                for item in raw_result[0]:
                    if hasattr(item, 'get_children') and len(item.get_children()) >= 5:
                        children = item.get_children()
                        task_id = str(children[0])
                        description = str(children[1]).strip('"')
                        deadline = str(children[2]).strip('"')
                        priority = str(children[3])

                        # Check if completed
                        all_tasks = self.get_all_tasks()
                        task_obj = next((t for t in all_tasks if t['id'] == task_id), None)
                        status = "✅ Completed" if task_obj and task_obj.get('completed', False) else "⏳ Pending"
                        if task_obj and task_obj.get('completed', False):
                            completed_count += 1

                        # Calculate urgency
                        urgency = ""
                        if task_obj:
                            days = task_obj.get('days_until_deadline', 0)
                            if days < 0:
                                urgency = " 🔴 OVERDUE"
                            elif days == 0:
                                urgency = " 🟡 DUE TODAY"
                            elif days <= 3:
                                urgency = " 🟠 DUE SOON"

                        tasks.append(f"• **{task_id}**: '{description}' ({priority} priority, Due: {deadline}){urgency} - {status}")

                if tasks:
                    summary = f"📊 **Task Summary**: {len(tasks)} total tasks, {completed_count} completed, {len(tasks) - completed_count} pending\n\n"
                    return summary + "\n".join(tasks)
                return "No tasks found in the system."

            elif "taskStatus" in query and "Completed" in query:
                # Handle completed tasks query
                if raw_result[0]:
                    completed_task_ids = [str(task) for task in raw_result[0]]
                    all_tasks = self.get_all_tasks()
                    completed_details = []

                    for task_id in completed_task_ids:
                        task = next((t for t in all_tasks if t['id'] == task_id), None)
                        if task:
                            completed_details.append(f"• '{task['description']}' ({task['priority']} priority)")

                    return f"✅ **Completed Tasks** ({len(completed_task_ids)} found):\n" + "\n".join(completed_details)
                return "No completed tasks found."

            else:
                # Generic result processing with more detail
                return f"🔍 **Query Result**: {str(raw_result[0])}\n\n💡 Try asking more specific questions like 'What is my next task?' or 'Show all tasks'."

        except Exception as e:
            return f"❌ Error processing result: {str(e)}\n\nPlease try rephrasing your question or ask for help."

    def ask_metta_brain(self, user_question: str) -> Dict[str, Any]:
        """Natural language interface to ask MeTTa brain questions"""
        try:
            # Convert natural language to MeTTa queries
            metta_query = self._convert_question_to_metta(user_question.lower())

            if not metta_query:
                return {
                    "success": False,
                    "error": "Could not understand the question. Try asking about tasks, dependencies, or scheduling."
                }

            # Execute the MeTTa query
            result = self.execute_metta_query(metta_query)

            # Add natural language explanation
            result["natural_answer"] = self._generate_natural_answer(user_question, result)

            return result

        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing question: {str(e)}"
            }

    def _convert_question_to_metta(self, question: str) -> str:
        """Convert natural language question to MeTTa query with intelligent pattern matching"""
        question = question.lower().strip()

        # Enhanced pattern matching with fuzzy matching
        if any(word in question for word in ["next", "recommend", "should i do", "what to do"]):
            return "!(getNextTask)"

        elif any(word in question for word in ["all tasks", "list", "show tasks", "what tasks", "my tasks"]):
            return "!(match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps) ($task $desc $deadline $priority $deps))"

        elif any(word in question for word in ["schedule", "order", "sequence", "arrange"]):
            return "!(scheduleTasks)"

        elif any(word in question for word in ["overdue", "late", "missed", "past due"]):
            return "!(getOverdueTasks)"

        elif any(word in question for word in ["completed", "finished", "done", "complete"]):
            return "!(match &self (taskStatus $task Completed) $task)"

        elif any(word in question for word in ["high priority", "urgent", "important", "critical"]):
            return "!(match &self (task $task Description $desc Deadline $deadline Priority High Dependencies $deps) $task)"

        elif any(word in question for word in ["medium priority", "moderate"]):
            return "!(match &self (task $task Description $desc Deadline $deadline Priority Medium Dependencies $deps) $task)"

        elif any(word in question for word in ["low priority", "less important"]):
            return "!(match &self (task $task Description $desc Deadline $deadline Priority Low Dependencies $deps) $task)"

        elif any(word in question for word in ["today", "due today", "today's"]):
            return "!(getTasksDueToday)"

        elif any(word in question for word in ["progress", "how am i", "doing", "status", "report"]):
            return "!(getProductivityInsights)"

        elif any(word in question for word in ["dependencies", "depends", "prerequisite"]):
            # Try to extract task ID
            words = question.split()
            for word in words:
                if word.startswith("task") and len(word) > 4:
                    task_id = word.capitalize()
                    return f"!(getDependencies {task_id})"
            # If no specific task, show all dependencies
            return "!(match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps) ($task $deps))"

        elif any(word in question for word in ["ready", "available", "can do", "no dependencies"]):
            return "!(getReadyTasks)"

        elif any(word in question for word in ["count", "how many", "number"]):
            if "completed" in question:
                return "!(match &self (taskStatus $task Completed) $task)"
            else:
                return "!(match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps) $task)"

        # If no pattern matches, try to find tasks by description keywords
        elif any(word in question for word in ["find", "search", "about", "containing"]):
            return "!(match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps) ($task $desc))"

        # Default fallback - show all tasks
        return "!(match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps) ($task $desc $deadline $priority $deps))"

    def _generate_natural_answer(self, question: str, metta_result: Dict) -> str:
        """Generate natural language answer from MeTTa result"""
        if not metta_result.get("success"):
            return "I couldn't process that question. Please try asking about tasks, scheduling, or dependencies."

        processed = metta_result.get("processed_result", "")

        # Add context based on question type
        if "next task" in question.lower():
            return f"🤖 Based on my analysis of your tasks, dependencies, and priorities: {processed}"
        elif "overdue" in question.lower():
            return f"⚠️ Here's what I found about overdue tasks: {processed}"
        elif "schedule" in question.lower() or "order" in question.lower():
            return f"📋 I've calculated the optimal task sequence: {processed}"
        elif "all tasks" in question.lower() or "list" in question.lower():
            return f"📝 Here are your current tasks: {processed}"
        else:
            return f"🧠 {processed}"

    def _generate_task_reasoning(self, task: Dict) -> str:
        """Generate detailed reasoning for why a task is recommended"""
        reasons = []

        # Priority reasoning
        if task['priority'] == 'High':
            reasons.append("🔴 **High Priority**: This task is marked as high importance")
        elif task['priority'] == 'Medium':
            reasons.append("🟡 **Medium Priority**: This task has moderate importance")
        else:
            reasons.append("🟢 **Low Priority**: This task has lower importance but still needs attention")

        # Deadline reasoning
        days_until = task.get('days_until_deadline', 0)
        if days_until < 0:
            reasons.append(f"⚠️ **Overdue**: This task is {abs(days_until)} days past its deadline")
        elif days_until == 0:
            reasons.append("🔥 **Due Today**: This task must be completed today")
        elif days_until <= 3:
            reasons.append(f"⏰ **Due Soon**: Only {days_until} days remaining")
        elif days_until <= 7:
            reasons.append(f"📅 **Due This Week**: {days_until} days remaining")
        else:
            reasons.append(f"📆 **Future Deadline**: {days_until} days remaining")

        # Dependency reasoning
        if not task['dependencies']:
            reasons.append("✅ **No Dependencies**: Ready to start immediately")
        else:
            reasons.append(f"🔗 **Dependencies Met**: All {len(task['dependencies'])} prerequisite tasks are completed")

        # Add strategic reasoning
        reasons.append("🎯 **Strategic Choice**: Based on MeTTa's analysis of priority, deadline urgency, and dependency completion")

        return "\n".join(f"• {reason}" for reason in reasons)

    def _generate_schedule_reasoning(self, task_ids: List[str], all_tasks: List[Dict]) -> str:
        """Generate reasoning for the task schedule order"""
        reasoning_parts = []

        reasoning_parts.append("🧠 **MeTTa's Scheduling Algorithm**:")
        reasoning_parts.append("• Dependencies are resolved first (prerequisite tasks come before dependent tasks)")
        reasoning_parts.append("• High priority tasks are prioritized within each dependency level")
        reasoning_parts.append("• Deadline urgency is considered as a tie-breaker")

        # Analyze the actual schedule
        if len(task_ids) > 1:
            reasoning_parts.append(f"\n📋 **This Schedule Analysis**:")
            reasoning_parts.append(f"• {len(task_ids)} tasks arranged in optimal dependency order")

            # Check for dependency chains
            dependency_chains = 0
            for task_id in task_ids:
                task = next((t for t in all_tasks if t['id'] == task_id), None)
                if task and task['dependencies']:
                    dependency_chains += 1

            if dependency_chains > 0:
                reasoning_parts.append(f"• {dependency_chains} tasks have dependencies that are properly sequenced")

            # Priority distribution
            priority_counts = {'High': 0, 'Medium': 0, 'Low': 0}
            for task_id in task_ids:
                task = next((t for t in all_tasks if t['id'] == task_id), None)
                if task:
                    priority_counts[task['priority']] += 1

            priority_summary = []
            for priority, count in priority_counts.items():
                if count > 0:
                    priority_summary.append(f"{count} {priority}")

            if priority_summary:
                reasoning_parts.append(f"• Priority distribution: {', '.join(priority_summary)} priority tasks")

        return "\n".join(reasoning_parts)
