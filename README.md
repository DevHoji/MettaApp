# MeTTa Task Scheduler

An intelligent task scheduling application powered by MeTTa (Meta Type Talk) reasoning engine with AI voice integration.

## Features

- **Intelligent Task Scheduling**: Uses MeTTa's reasoning capabilities to optimize task order
- **Dependency Management**: Handles complex task dependencies with circular dependency detection
- **Priority-based Scheduling**: Considers task priorities and deadlines for optimal scheduling
- **Interactive Web Interface**: Clean, modern web interface for task management
- **Real-time Updates**: Dynamic task status updates and recommendations
- **MeTTa Brain Chat**: Direct conversation with the MeTTa reasoning engine
- **AI Voice Integration**: Text-to-speech functionality for chat responses
- **Debug Mode**: Real-time MeTTa query execution logging

## Technology Stack

- **Backend**: Python Flask with MeTTa integration
- **Frontend**: HTML5, CSS3, JavaScript with Web Speech API
- **AI Engine**: MeTTa (Meta Type Talk) for logical reasoning
- **Data Storage**: JSON-based persistence with automatic backup

## Prerequisites

Before running this project, make sure you have the following installed:

- **Python 3.8 or higher**
- **pip** (Python package installer)
- **Git** (for cloning the repository)

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/DevHoji/MettaApp.git
cd MettaApp
```

### 2. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python backend/app.py
```

### 5. Access the Application
Open your web browser and navigate to:
```
http://localhost:5000
```

## Usage Guide

### Task Management
- **Add Tasks**: Create tasks with descriptions, deadlines, and priorities
- **Set Dependencies**: Define task relationships to create logical workflows
- **Track Progress**: Monitor task completion and deadlines

### MeTTa Brain Chat
- **Ask Questions**: Use natural language to query your tasks
  - "What is my next task?"
  - "Show me overdue tasks"
  - "How am I doing with my tasks?"
- **Voice Feature**: Click the voice button (🔊) to enable AI speech responses
- **Debug Mode**: Toggle debug output to see raw MeTTa reasoning

### Dependencies Explained
Dependencies define the order in which tasks must be completed. For example:
- Task A: "Plan project structure" (no dependencies)
- Task B: "Set up development environment" (depends on Task A)
- Task C: "Implement features" (depends on Task B)

This ensures tasks are completed in the correct logical order.

## Project Structure
```
MettaApp/
├── backend/
│   ├── app.py              # Flask application
│   └── metta_bridge.py     # MeTTa integration
├── frontend/
│   ├── static/
│   │   ├── css/           # Stylesheets
│   │   └── js/            # JavaScript files
│   └── templates/         # HTML templates
├── metta_brain/
│   └── scheduler.metta    # MeTTa reasoning logic
├── data/
│   └── tasks.json         # Task persistence
└── requirements.txt       # Python dependencies
```

## Troubleshooting

### Common Issues

1. **Port already in use**: If port 5000 is busy, the app will try port 5001
2. **Voice not working**: Ensure your browser supports Web Speech API (Chrome, Edge, Safari)
3. **MeTTa errors**: Check the terminal for detailed MeTTa execution logs

### Debug Mode
Enable debug mode in the chat interface to see:
- Raw MeTTa queries
- Execution results
- Processing steps
- Error details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.
