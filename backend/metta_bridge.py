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


class MeTTaBridge:
    """Bridge class for MeTTa-Python integration"""

    def __init__(self):
        """Initialize MeTTa instance and load scheduler logic"""
        self.metta = MeTTa()
        self.task_counter = 0
        self._load_scheduler_logic()
        self._register_python_functions()

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
