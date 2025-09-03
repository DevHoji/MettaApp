"""
Smart To-Do Task Scheduler - Backend Server
Flask application with MeTTa integration

This server provides REST API endpoints for the task scheduler frontend,
integrating with MeTTa brain for intelligent task scheduling.
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import sys
from datetime import datetime, timedelta
import json

# Add the parent directory to the path to import metta_bridge
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.minimal_metta_bridge import MinimalMeTTaBridge

# Initialize Flask app
app = Flask(__name__,
           template_folder='../frontend/templates',
           static_folder='../frontend/static')
CORS(app)

# Initialize Pure MeTTa Brain - ALL LOGIC IN METTA
try:
    metta_bridge = MinimalMeTTaBridge()
    print("Pure MeTTa brain initialized successfully - ALL intelligence in MeTTa")
except Exception as e:
    print(f"Error initializing Pure MeTTa brain: {e}")
    metta_bridge = None

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks with their details"""
    try:
        if not metta_bridge:
            return jsonify({"error": "MeTTa bridge not initialized"}), 500

        tasks = metta_bridge.get_all_tasks()
        return jsonify({"success": True, "tasks": tasks})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Add a new task"""
    try:
        if not metta_bridge:
            return jsonify({"error": "MeTTa bridge not initialized"}), 500

        data = request.get_json()

        # Validate required fields
        required_fields = ['description', 'deadline', 'priority']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400

        # Validate priority
        valid_priorities = ['High', 'Medium', 'Low']
        if data['priority'] not in valid_priorities:
            return jsonify({"success": False, "error": "Priority must be High, Medium, or Low"}), 400

        # Validate date format
        try:
            datetime.strptime(data['deadline'], '%Y-%m-%d')
        except ValueError:
            return jsonify({"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}), 400

        # Get dependencies (optional)
        dependencies = data.get('dependencies', [])

        # Add task using MeTTa bridge
        result = metta_bridge.add_task(
            description=data['description'],
            deadline=data['deadline'],
            priority=data['priority'],
            dependencies=dependencies
        )

        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/tasks/<task_id>/complete', methods=['POST'])
def complete_task(task_id):
    """Mark a task as completed"""
    try:
        if not metta_bridge:
            return jsonify({"error": "MeTTa bridge not initialized"}), 500

        result = metta_bridge.complete_task(task_id)

        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    try:
        if not metta_bridge:
            return jsonify({"error": "MeTTa bridge not initialized"}), 500

        result = metta_bridge.delete_task(task_id)

        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    """Get the optimal task schedule"""
    try:
        if not metta_bridge:
            return jsonify({"error": "MeTTa bridge not initialized"}), 500

        scheduled_tasks = metta_bridge.get_scheduled_tasks()
        return jsonify({"success": True, "schedule": scheduled_tasks})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/next-task', methods=['GET'])
def get_next_task():
    """Get the next recommended task"""
    try:
        if not metta_bridge:
            return jsonify({"error": "MeTTa bridge not initialized"}), 500

        next_task = metta_bridge.get_next_task()
        return jsonify({"success": True, "next_task": next_task})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get completion statistics"""
    try:
        if not metta_bridge:
            return jsonify({"error": "MeTTa bridge not initialized"}), 500

        stats = metta_bridge.get_enhanced_stats()
        return jsonify({"success": True, "stats": stats})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/insights', methods=['GET'])
def get_insights():
    """Get productivity insights from MeTTa AI"""
    try:
        if not metta_bridge:
            return jsonify({"error": "MeTTa bridge not initialized"}), 500

        insights = metta_bridge.get_productivity_insights()
        return jsonify({"success": True, "insights": insights})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/recommendation-detailed', methods=['GET'])
def get_detailed_recommendation():
    """Get next task recommendation with explanation"""
    try:
        if not metta_bridge:
            return jsonify({"error": "MeTTa bridge not initialized"}), 500

        recommendation = metta_bridge.get_recommendation_with_reason()
        return jsonify({"success": True, "recommendation": recommendation})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/overdue-tasks', methods=['GET'])
def get_overdue_tasks():
    """Get overdue tasks"""
    try:
        if not metta_bridge:
            return jsonify({"error": "MeTTa bridge not initialized"}), 500

        overdue_tasks = metta_bridge.get_overdue_tasks()
        return jsonify({"success": True, "overdue_tasks": overdue_tasks})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/optimal-order', methods=['GET'])
def get_optimal_order():
    """Get optimal task order based on priority and urgency"""
    try:
        if not metta_bridge:
            return jsonify({"error": "MeTTa bridge not initialized"}), 500

        optimal_order = metta_bridge.get_optimal_task_order()
        return jsonify({"success": True, "optimal_order": optimal_order})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/metta-query', methods=['POST'])
def execute_metta_query():
    """Execute raw MeTTa query with debug output"""
    try:
        if not metta_bridge:
            return jsonify({"error": "MeTTa bridge not initialized"}), 500

        data = request.get_json()
        query = data.get('query', '')

        if not query:
            return jsonify({"success": False, "error": "Query is required"}), 400

        result = metta_bridge.execute_metta_query(query)
        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/ask-metta', methods=['POST'])
def ask_metta_brain():
    """Ask MeTTa brain a natural language question"""
    try:
        if not metta_bridge:
            return jsonify({"error": "MeTTa bridge not initialized"}), 500

        data = request.get_json()
        question = data.get('question', '')

        if not question:
            return jsonify({"success": False, "error": "Question is required"}), 400

        result = metta_bridge.ask_metta_brain(question)
        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/chat')
def chat_page():
    """Serve the MeTTa chat interface"""
    return render_template('chat.html')

@app.route('/api/dependencies/<task_id>', methods=['GET'])
def get_task_dependencies(task_id):
    """Get dependencies for a specific task"""
    try:
        if not metta_bridge:
            return jsonify({"error": "MeTTa bridge not initialized"}), 500

        dependencies = metta_bridge.get_task_dependencies(task_id)
        return jsonify({"success": True, "dependencies": dependencies})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "metta_bridge": "initialized" if metta_bridge else "not initialized",
        "timestamp": datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("Starting Smart To-Do Task Scheduler Backend...")
    print("MeTTa Bridge Status:", "Initialized" if metta_bridge else "Not Initialized")

    # Add some sample tasks for demonstration if no tasks exist
    if metta_bridge:
        existing_tasks = metta_bridge.get_all_tasks()
        if not existing_tasks:
            print("No existing tasks found. Adding sample tasks for demonstration...")
            try:
                # Sample tasks with dependencies and realistic dates
                from datetime import datetime, timedelta
                today = datetime.now()

                # Create tasks with dates relative to today
                metta_bridge.add_task("Plan project structure", (today + timedelta(days=2)).strftime("%Y-%m-%d"), "High", [])
                metta_bridge.add_task("Set up development environment", (today + timedelta(days=5)).strftime("%Y-%m-%d"), "High", ["Task1"])
                metta_bridge.add_task("Implement core features", (today + timedelta(days=10)).strftime("%Y-%m-%d"), "Medium", ["Task2"])
                metta_bridge.add_task("Write tests", (today + timedelta(days=15)).strftime("%Y-%m-%d"), "Medium", ["Task3"])
                metta_bridge.add_task("Deploy application", (today + timedelta(days=20)).strftime("%Y-%m-%d"), "Low", ["Task4"])

                # Add some overdue tasks for testing (only slightly overdue)
                metta_bridge.add_task("Review documentation", (today - timedelta(days=1)).strftime("%Y-%m-%d"), "Medium", [])
                metta_bridge.add_task("Update README", (today - timedelta(days=3)).strftime("%Y-%m-%d"), "Low", [])

                print("Sample tasks added successfully with realistic dates")
            except Exception as e:
                print(f"Error adding sample tasks: {e}")
        else:
            print(f"Found {len(existing_tasks)} existing tasks, skipping sample data creation")

    app.run(debug=True, host='0.0.0.0', port=5000)
