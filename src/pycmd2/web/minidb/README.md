# MiniDB - Personal Database

MiniDB is a personal database system with hierarchical workspace support. It can be accessed through a web interface (React) or a local GUI application.

## Features

- Hierarchical workspace organization
- Multiple access methods:
  - Web interface (React)
  - Local GUI application
  - Command-line interface (CLI)
- JSON-based storage
- RESTful API for web access

## Installation

Make sure you have Python 3.6+ installed.

```bash
uv sync
```

For the web frontend, you also need Node.js and npm installed.

```bash
cd frontend
yarn
```

## Usage

### Command Line Interface

```bash
# Create a new workspace
python -m minidb.cli create myproject

# Create a child workspace
python -m minidb.cli create subproject --parent myproject

# List all workspaces
python -m minidb.cli list

# Add data to a workspace
python -m minidb.cli add-data myproject/todo "Buy groceries" "Milk, Eggs, Bread"

# Show workspace details
python -m minidb.cli show myproject

# Delete a workspace
python -m minidb.cli delete myproject/subproject
```

### Web Interface

1. Start the API server:
```bash
cd ./minidb
fastapi dev app.py
```

2. In another terminal, start the React frontend:
```bash
cd frontend
vite dev
```

3. Open your browser at http://localhost:3000

### Local GUI Application

```bash
python -m minidb.gui
```

## Project Structure

```
minidb/
├── core.py          # Core database functionality
├── cli.py           # Command-line interface
├── web_api.py       # Web API (Flask)
├── gui.py           # Local GUI (Tkinter)
├── frontend/        # React web frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   └── services/    # API service functions
│   └── public/          # Static files
└── README.md
```

## API Endpoints

- `GET /api/workspaces` - List all root workspaces
- `GET /api/workspaces/<path>` - Get a specific workspace
- `POST /api/workspaces` - Create a new workspace
- `DELETE /api/workspaces/<path>` - Delete a workspace
- `POST /api/workspaces/<path>/data` - Add data to a workspace
- `DELETE /api/workspaces/<path>/data/<key>` - Remove data from a workspace

## Data Model

Workspaces can contain:
- Child workspaces (hierarchical structure)
- Key-value data pairs

Each workspace has:
- Name
- Path (derived from hierarchy)
- Creation timestamp
- Data dictionary
