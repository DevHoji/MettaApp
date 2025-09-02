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
            # Add task to MeTTa space
            self.metta.run(task_atom)

            # Validate for circular dependencies
            validation_result = self.metta.run(f'!(validateTask {task_id} {deps_str})')
            if validation_result and validation_result[0] and not validation_result[0][0]:
                # Remove the invalid task
                self.metta.run(f'!(remove-atom &self {task_atom})')
                return {"success": False, "error": "Circular dependency detected"}

            # Save tasks to file for persistence
            self._save_tasks_to_file()

            return {
                "success": True,
                "task_id": task_id,
                "message": f"Task '{description}' added successfully"
            }
        except Exception as e:
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

            self.metta.run(f'!(completeTask {task_id})')
            return {"success": True, "message": f"Task {task_id} marked as completed"}
        except Exception as e:
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
            task_result = self.metta.run(f'!(match &self (task {task_id} Description $desc Deadline $deadline Priority $priority Dependencies $deps) (task {task_id} Description $desc Deadline $deadline Priority $priority Dependencies $deps))')
            if task_result and task_result[0]:
                task_atom = task_result[0][0]
                self.metta.run(f'!(remove-atom &self {task_atom})')

            # Remove task status if exists
            status_result = self.metta.run(f'!(match &self (taskStatus {task_id} $status) (taskStatus {task_id} $status))')
            if status_result and status_result[0]:
                status_atom = status_result[0][0]
                self.metta.run(f'!(remove-atom &self {status_atom})')

            return {"success": True, "message": f"Task {task_id} deleted successfully"}
        except Exception as e:
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
        """Execute raw MeTTa query and return both raw and processed results"""
        try:
            print(f"\n🧠 MeTTa Query: {query}")

            # Execute the query
            raw_result = self.metta.run(query)

            # Log raw MeTTa output
            print(f"🔍 Raw MeTTa Result: {raw_result}")

            # Process result for user-friendly display
            processed_result = self._process_metta_result(raw_result, query)

            return {
                "success": True,
                "query": query,
                "raw_result": str(raw_result),
                "processed_result": processed_result,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            error_msg = f"Error executing MeTTa query: {e}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "query": query,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _process_metta_result(self, raw_result, query: str) -> str:
        """Process raw MeTTa result into user-friendly format"""
        try:
            if not raw_result or not raw_result[0]:
                return "No results found."

            # Handle different types of queries
            if "getNextTask" in query:
                if str(raw_result[0][0]) == "NoTasksAvailable":
                    return "No tasks are currently available. All tasks may have unmet dependencies."
                else:
                    task_id = str(raw_result[0][0])
                    task = next((t for t in self.get_all_tasks() if t['id'] == task_id), None)
                    if task:
                        return f"Next recommended task: '{task['description']}' (Priority: {task['priority']}, Deadline: {task['deadline']})"
                    return f"Next recommended task: {task_id}"

            elif "scheduleTasks" in query:
                if raw_result[0]:
                    task_ids = [str(task) for task in raw_result[0]]
                    return f"Optimal task order: {' → '.join(task_ids)}"
                return "No tasks to schedule."

            elif "getOverdueTasks" in query:
                if raw_result[0]:
                    overdue_tasks = [str(task) for task in raw_result[0]]
                    return f"Overdue tasks: {', '.join(overdue_tasks)}"
                return "No overdue tasks."

            elif "getDependencies" in query:
                if raw_result[0] and hasattr(raw_result[0][0], 'get_children'):
                    deps = [str(dep) for dep in raw_result[0][0].get_children()]
                    return f"Dependencies: {', '.join(deps) if deps else 'None'}"
                return "No dependencies found."

            elif "match" in query and "task" in query:
                # Handle task queries
                tasks = []
                for item in raw_result[0]:
                    if hasattr(item, 'get_children') and len(item.get_children()) >= 5:
                        children = item.get_children()
                        task_id = str(children[0])
                        description = str(children[1]).strip('"')
                        tasks.append(f"{task_id}: {description}")

                if tasks:
                    return f"Found {len(tasks)} tasks:\n" + "\n".join(tasks)
                return "No tasks found."

            else:
                # Generic result processing
                return f"Result: {str(raw_result[0])}"

        except Exception as e:
            return f"Error processing result: {str(e)}"

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
        """Convert natural language question to MeTTa query"""
        question = question.lower().strip()

        # Question patterns and their MeTTa equivalents
        patterns = {
            "what is the next task": "!(getNextTask)",
            "next task": "!(getNextTask)",
            "what should i do next": "!(getNextTask)",
            "recommend task": "!(getNextTask)",

            "show all tasks": "!(match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps) ($task $desc $deadline $priority $deps))",
            "list tasks": "!(match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps) ($task $desc $deadline $priority $deps))",
            "all tasks": "!(match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps) ($task $desc $deadline $priority $deps))",

            "schedule tasks": "!(scheduleTasks)",
            "optimal order": "!(scheduleTasks)",
            "task order": "!(scheduleTasks)",

            "overdue tasks": "!(getOverdueTasks)",
            "what tasks are overdue": "!(getOverdueTasks)",
            "late tasks": "!(getOverdueTasks)",

            "completed tasks": "!(match &self (taskStatus $task Completed) $task)",
            "finished tasks": "!(match &self (taskStatus $task Completed) $task)",
            "done tasks": "!(match &self (taskStatus $task Completed) $task)",

            "high priority tasks": "!(match &self (task $task Description $desc Deadline $deadline Priority High Dependencies $deps) $task)",
            "urgent tasks": "!(match &self (task $task Description $desc Deadline $deadline Priority High Dependencies $deps) $task)",

            "tasks due today": "!(getTasksDueToday)",
            "today's tasks": "!(getTasksDueToday)",

            "productivity insights": "!(getProductivityInsights)",
            "how am i doing": "!(getProductivityInsights)",
            "progress report": "!(getProductivityInsights)",
        }

        # Find matching pattern
        for pattern, query in patterns.items():
            if pattern in question:
                return query

        # Handle dependency questions
        if "dependencies" in question:
            # Try to extract task ID from question
            words = question.split()
            for word in words:
                if word.startswith("task") and len(word) > 4:
                    task_id = word.capitalize()
                    return f"!(getDependencies {task_id})"
            return "!(match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps) ($task $deps))"

        return None

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
