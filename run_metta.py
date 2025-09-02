#!/usr/bin/env python3
"""
MeTTa Terminal Runner
Direct interface to run MeTTa queries and see raw output

Usage:
    python3 run_metta.py
    
Then type MeTTa queries like:
    !(getNextTask)
    !(scheduleTasks)
    !(match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps) ($task $desc))
"""

import os
import sys
from hyperon import MeTTa

class MeTTaRunner:
    def __init__(self):
        self.metta = MeTTa()
        self.load_scheduler()
        self.setup_sample_data()
    
    def load_scheduler(self):
        """Load the MeTTa scheduler logic"""
        try:
            scheduler_path = os.path.join('metta_brain', 'scheduler.metta')
            with open(scheduler_path, 'r') as f:
                scheduler_code = f.read()
            
            print("🧠 Loading MeTTa scheduler logic...")
            result = self.metta.run(scheduler_code)
            print(f"✅ MeTTa scheduler loaded successfully")
            if result:
                print(f"📋 Load result: {result}")
            
        except Exception as e:
            print(f"❌ Error loading scheduler: {e}")
            sys.exit(1)
    
    def setup_sample_data(self):
        """Add some sample tasks for testing"""
        print("\n📝 Adding sample tasks...")
        
        sample_tasks = [
            '(task Task1 Description "Plan project structure" Deadline "2024-01-15" Priority High Dependencies ())',
            '(task Task2 Description "Set up development environment" Deadline "2024-01-16" Priority High Dependencies (Task1))',
            '(task Task3 Description "Implement core features" Deadline "2024-01-20" Priority Medium Dependencies (Task2))',
            '(task Task4 Description "Write tests" Deadline "2024-01-22" Priority Medium Dependencies (Task3))',
            '(task Task5 Description "Deploy application" Deadline "2024-01-25" Priority Low Dependencies (Task4))'
        ]
        
        for task in sample_tasks:
            result = self.metta.run(task)
            print(f"  ✓ Added: {task}")
            if result:
                print(f"    Result: {result}")
        
        print("✅ Sample tasks added successfully\n")
    
    def run_query(self, query):
        """Execute a MeTTa query and show detailed output"""
        print(f"\n🧠 Executing MeTTa Query:")
        print(f"   Query: {query}")
        print(f"   {'='*50}")
        
        try:
            # Execute the query
            result = self.metta.run(query)
            
            print(f"🔍 Raw MeTTa Result:")
            print(f"   Type: {type(result)}")
            print(f"   Value: {result}")
            
            if result and len(result) > 0:
                print(f"   Length: {len(result)}")
                print(f"   First element: {result[0]}")
                
                if hasattr(result[0], '__iter__') and not isinstance(result[0], str):
                    print(f"   First element type: {type(result[0])}")
                    print(f"   First element length: {len(result[0])}")
                    
                    for i, item in enumerate(result[0]):
                        print(f"   Item {i}: {item} (type: {type(item)})")
                        if hasattr(item, 'get_children'):
                            children = item.get_children()
                            print(f"     Children: {children}")
            
            print(f"   {'='*50}")
            
            # Try to process the result
            processed = self.process_result(result, query)
            print(f"🎯 Processed Result:")
            print(f"   {processed}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error executing query: {e}")
            return None
    
    def process_result(self, result, query):
        """Process MeTTa result into human-readable format"""
        if not result or not result[0]:
            return "No results found"
        
        try:
            if "getNextTask" in query:
                if str(result[0][0]) == "NoTasksAvailable":
                    return "No tasks available (all dependencies not met)"
                return f"Next task: {result[0][0]}"
            
            elif "scheduleTasks" in query:
                if result[0]:
                    tasks = [str(task) for task in result[0]]
                    return f"Optimal order: {' → '.join(tasks)}"
                return "No tasks to schedule"
            
            elif "match" in query and "task" in query:
                tasks = []
                for item in result[0]:
                    if hasattr(item, 'get_children') and len(item.get_children()) >= 5:
                        children = item.get_children()
                        task_id = str(children[0])
                        desc = str(children[1]).strip('"')
                        deadline = str(children[2]).strip('"')
                        priority = str(children[3])
                        tasks.append(f"{task_id}: '{desc}' (Priority: {priority}, Deadline: {deadline})")
                
                if tasks:
                    return f"Found {len(tasks)} tasks:\n" + "\n".join(f"   {task}" for task in tasks)
                return "No tasks found"
            
            else:
                return str(result[0])
                
        except Exception as e:
            return f"Error processing: {e}"
    
    def interactive_mode(self):
        """Run in interactive mode"""
        print("🚀 MeTTa Interactive Terminal")
        print("=" * 50)
        print("Enter MeTTa queries (or 'help' for examples, 'quit' to exit)")
        print()
        
        while True:
            try:
                query = input("MeTTa> ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                elif query.lower() == 'help':
                    self.show_help()
                    continue
                
                elif query.lower() == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    continue
                
                elif not query:
                    continue
                
                # Execute the query
                self.run_query(query)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break
    
    def show_help(self):
        """Show help with example queries"""
        print("\n📚 MeTTa Query Examples:")
        print("=" * 30)
        print("🔍 Basic Queries:")
        print("   !(getNextTask)")
        print("   !(scheduleTasks)")
        print("   !(getAllTasks)")
        print()
        print("📋 Task Queries:")
        print("   !(match &self (task $task Description $desc Deadline $deadline Priority $priority Dependencies $deps) ($task $desc))")
        print("   !(getOverdueTasks)")
        print("   !(getTasksDueToday)")
        print()
        print("🔗 Dependency Queries:")
        print("   !(getDependencies Task1)")
        print("   !(dependenciesCompleted Task2)")
        print()
        print("📊 Analytics:")
        print("   !(getProductivityInsights)")
        print("   !(getOptimalTaskOrder)")
        print()
        print("💡 Commands:")
        print("   help  - Show this help")
        print("   clear - Clear screen")
        print("   quit  - Exit")
        print()

def main():
    """Main function"""
    print("🧠 MeTTa Terminal Runner")
    print("Direct interface to the MeTTa reasoning engine")
    print()
    
    runner = MeTTaRunner()
    
    if len(sys.argv) > 1:
        # Run single query from command line
        query = ' '.join(sys.argv[1:])
        runner.run_query(query)
    else:
        # Interactive mode
        runner.interactive_mode()

if __name__ == "__main__":
    main()
