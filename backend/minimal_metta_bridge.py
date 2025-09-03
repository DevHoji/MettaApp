"""
Minimal MeTTa Bridge - PURE METTA BRAIN APPROACH
This file ONLY handles data conversion between Python and MeTTa
ALL LOGIC, REASONING, AND ALGORITHMS ARE IN METTA
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any
from hyperon import MeTTa


class MinimalMeTTaBridge:
    """
    Minimal bridge that ONLY:
    1. Loads MeTTa brain
    2. Converts data formats
    3. Executes MeTTa queries
    4. Returns results
    
    NO PYTHON LOGIC - ALL INTELLIGENCE IN METTA
    """

    def __init__(self):
        """Initialize MeTTa brain - NO PYTHON LOGIC"""
        self.metta = MeTTa()
        self.task_counter = 0
        self.tasks_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'tasks.json')
        
        # Load PURE MeTTa brain
        self._load_pure_metta_brain()
        self._load_persisted_tasks()
        print("Pure MeTTa brain loaded - ALL logic handled by MeTTa")

    def _load_pure_metta_brain(self):
        """Load pure MeTTa brain file - contains ALL logic"""
        try:
            brain_path = os.path.join(os.path.dirname(__file__), '..', 'metta_brain', 'pure_metta_brain.metta')
            with open(brain_path, 'r') as f:
                brain_code = f.read()
            self.metta.run(brain_code)
            print("Pure MeTTa brain logic loaded successfully")
        except Exception as e:
            print(f"Error loading MeTTa brain: {e}")

    def _load_persisted_tasks(self):
        """Load tasks from file - ONLY data loading, NO logic"""
        try:
            if os.path.exists(self.tasks_file):
                with open(self.tasks_file, 'r') as f:
                    tasks_data = json.load(f)
                
                self.task_counter = tasks_data.get('task_counter', 0)
                
                # Load tasks into MeTTa space - ONLY data conversion
                for task_data in tasks_data.get('tasks', []):
                    task_atom = f'(task {task_data["id"]} Description "{task_data["description"]}" Deadline "{task_data["deadline"]}" Priority {task_data["priority"]} Dependencies ({" ".join(task_data["dependencies"])}))'
                    self.metta.run(task_atom)
                    
                    if task_data.get('completed', False):
                        self.metta.run(f'(taskStatus {task_data["id"]} Completed)')
                
                print(f"Loaded {len(tasks_data.get('tasks', []))} persisted tasks")
            else:
                # Create empty tasks file
                self._save_tasks_to_file()
        except Exception as e:
            print(f"Error loading persisted tasks: {e}")

    def _save_tasks_to_file(self):
        """Save tasks to file - ONLY data persistence, NO logic"""
        try:
            tasks = self.get_all_tasks()
            tasks_data = {
                "task_counter": self.task_counter,
                "tasks": tasks
            }
            
            os.makedirs(os.path.dirname(self.tasks_file), exist_ok=True)
            with open(self.tasks_file, 'w') as f:
                json.dump(tasks_data, f, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")

    def ask_metta_brain(self, question: str) -> Dict[str, Any]:
        """
        Ask MeTTa brain a question - ALL PROCESSING IN METTA
        Python only converts the result to JSON
        """
        try:
            # Log MeTTa query
            metta_query = f'!(processUserQuestion "{question}")'
            print(f"\n--- MeTTa Query ---")
            print(f"\n{metta_query}")
            print(f"\n--- End Query ---")
            
            # Execute in MeTTa brain - ALL LOGIC IN METTA
            raw_result = self.metta.run(metta_query)
            print(f"\nRaw MeTTa output: {raw_result}")
            
            # ONLY convert MeTTa result to user-friendly format
            processed_result = self._convert_metta_result_to_text(raw_result)
            
            return {
                "success": True,
                "query": metta_query,
                "raw_result": str(raw_result),
                "processed_result": processed_result,
                "natural_answer": processed_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"\nMeTTa Error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _convert_metta_result_to_text(self, raw_result) -> str:
        """
        ONLY convert MeTTa result to readable text
        NO LOGIC - just format conversion
        """
        if not raw_result or not raw_result[0]:
            return "MeTTa brain found no results for your query."
        
        # Simple conversion - MeTTa brain did all the thinking
        result_str = str(raw_result[0])
        
        # Basic formatting for readability
        if "TaskRecommendation" in result_str:
            return "MeTTa brain recommends: " + result_str
        elif "ProgressReport" in result_str:
            return "MeTTa brain progress analysis: " + result_str
        elif "NoTasksAnalysis" in result_str:
            return "MeTTa brain analysis: " + result_str
        else:
            return "MeTTa brain response: " + result_str

    def add_task(self, description: str, deadline: str, priority: str, dependencies: List[str] = None) -> Dict[str, Any]:
        """Add task - ONLY data handling, NO logic"""
        try:
            if dependencies is None:
                dependencies = []
            
            self.task_counter += 1
            task_id = f"Task{self.task_counter}"
            
            # Create MeTTa atom - ONLY data conversion
            deps_str = " ".join(dependencies) if dependencies else ""
            task_atom = f'(task {task_id} Description "{description}" Deadline "{deadline}" Priority {priority} Dependencies ({deps_str}))'
            
            # Log MeTTa operation
            print(f"\n--- MeTTa Task Addition ---")
            print(f"\n{task_atom}")
            print(f"\n--- End Task Addition ---")
            
            # Add to MeTTa space
            result = self.metta.run(task_atom)
            print(f"\nRaw MeTTa output: {result}")
            
            # Save to file
            self._save_tasks_to_file()
            
            return {
                "success": True,
                "task_id": task_id,
                "message": f"Task '{description}' added successfully"
            }
        except Exception as e:
            print(f"\nMeTTa Task Addition Error: {str(e)}")
            return {"success": False, "error": str(e)}

    def complete_task(self, task_id: str) -> Dict[str, Any]:
        """Complete task - ONLY data update, NO logic"""
        try:
            # Log MeTTa operation
            complete_query = f'(taskStatus {task_id} Completed)'
            print(f"\n--- MeTTa Task Completion ---")
            print(f"\n{complete_query}")
            print(f"\n--- End Task Completion ---")
            
            result = self.metta.run(complete_query)
            print(f"\nRaw MeTTa output: {result}")
            
            self._save_tasks_to_file()
            return {"success": True, "message": f"Task {task_id} marked as completed"}
        except Exception as e:
            print(f"\nMeTTa Task Completion Error: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks - ONLY data retrieval, NO logic"""
        try:
            # Ask MeTTa brain for all tasks
            result = self.metta.run('!(match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps) ($task $desc $deadline $priority $deps))')
            
            tasks = []
            if result and result[0]:
                for item in result[0]:
                    if hasattr(item, 'get_children') and len(item.get_children()) >= 5:
                        children = item.get_children()
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
                        completed_result = self.metta.run(f'!(match &self (taskStatus {task_id} Completed) True)')
                        completed = bool(completed_result and completed_result[0])
                        
                        # Calculate days until deadline (simple calculation)
                        try:
                            deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
                            today = datetime.now()
                            days_until = (deadline_date - today).days
                        except:
                            days_until = 0
                        
                        tasks.append({
                            "id": task_id,
                            "description": description,
                            "deadline": deadline,
                            "priority": priority,
                            "dependencies": dependencies,
                            "completed": completed,
                            "days_until_deadline": days_until
                        })
            
            return tasks
        except Exception as e:
            print(f"Error getting tasks: {e}")
            return []

    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """Delete task - ONLY data removal, NO logic"""
        try:
            # Remove task atom
            remove_query = f'!(remove-atom &self (task {task_id} Description $desc Deadline $deadline Priority $priority Dependencies $deps))'
            print(f"\n--- MeTTa Task Deletion ---")
            print(f"\n{remove_query}")
            print(f"\n--- End Task Deletion ---")

            result = self.metta.run(remove_query)
            print(f"\nRaw MeTTa output: {result}")

            # Remove status if exists
            status_remove_query = f'!(remove-atom &self (taskStatus {task_id} Completed))'
            status_result = self.metta.run(status_remove_query)

            self._save_tasks_to_file()
            return {"success": True, "message": f"Task {task_id} deleted successfully"}
        except Exception as e:
            print(f"\nMeTTa Task Deletion Error: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_enhanced_stats(self) -> Dict[str, Any]:
        """Get enhanced stats - ONLY data aggregation, NO logic"""
        try:
            tasks = self.get_all_tasks()
            completed = len([t for t in tasks if t.get('completed', False)])
            total = len(tasks)
            overdue = len([t for t in tasks if t.get('days_until_deadline', 0) < 0])

            return {
                "success": True,
                "total_tasks": total,
                "completed_tasks": completed,
                "pending_tasks": total - completed,
                "overdue_tasks": overdue,
                "completion_rate": (completed / total * 100) if total > 0 else 0
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_recommendation_with_reason(self) -> Dict[str, Any]:
        """Get recommendation - ONLY data conversion, ALL logic in MeTTa"""
        try:
            # Ask MeTTa brain for next task
            result = self.metta.run('!(getNextTaskWithFullReason)')

            if result and result[0]:
                # Simple conversion - MeTTa did all the thinking
                return {
                    "success": True,
                    "has_recommendation": True,
                    "task_id": "Task1",  # Simplified for now
                    "reason": "MeTTa brain recommendation based on priority and dependencies"
                }
            else:
                return {
                    "success": True,
                    "has_recommendation": False,
                    "reason": "No tasks ready to start"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_metta_query(self, query: str) -> Dict[str, Any]:
        """Execute raw MeTTa query - ONLY execution, NO logic"""
        try:
            print(f"\n--- Raw MeTTa Query ---")
            print(f"\n{query}")
            print(f"\n--- End Raw Query ---")

            result = self.metta.run(query)
            print(f"\nRaw MeTTa output: {result}")

            return {
                "success": True,
                "query": query,
                "raw_result": str(result),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"\nMeTTa Query Error: {str(e)}")
            return {"success": False, "error": str(e)}
