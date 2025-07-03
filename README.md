# MCP Tools Web Demo

This is a web-based interface for testing Model Context Protocol (MCP) tools with a modern, interactive UI.

## Features

- 🔧 **Interactive Tool Testing**: Select and test MCP tools through a web interface
- 📋 **Tool Discovery**: Automatically loads and displays all available MCP tools
- 🎯 **Parameter Input**: Dynamic form generation based on tool schemas
- 🚀 **Quick Test Examples**: Pre-configured buttons for common test scenarios
- 📊 **Real-time Results**: See tool execution results and errors immediately
- 🎨 **Modern UI**: Beautiful, responsive interface built with Tailwind CSS

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install fastapi uvicorn
   ```

2. **Run the Web Demo**:
   ```bash
   python demo_mcp_tools.py
   ```

3. **Open Your Browser**:
   Navigate to `http://localhost:8000`

## How to Use

### Available Tools
The demo automatically loads the following MCP tools:
- **Math Tools**: `add`, `multiply` - Basic arithmetic operations
- **Time Tool**: `get_time` - Get current time
- **Weather Tool**: `get_weather` - Get weather information for a location

### Testing Tools

1. **Select a Tool**: Click on any tool card in the "Available Tools" section
2. **Enter Parameters**: Fill in the required parameters (if any)
3. **Execute**: Click the "Execute Tool" button
4. **View Results**: Results or errors will be displayed below

### Quick Test Examples

Use the pre-configured quick test buttons for common scenarios:
- **Math: Add** - Adds 5 + 3
- **Math: Multiply** - Multiplies 4 × 6
- **Get Time** - Shows current time
- **Weather** - Gets weather for San Francisco

## API Endpoints

The web demo exposes the following API endpoints:

- `GET /` - Main web interface
- `GET /api/tools` - List all available tools (JSON)
- `POST /api/execute` - Execute a tool with parameters

### Example API Usage

```bash
# Get available tools
curl http://localhost:8000/api/tools

# Execute a tool
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "add",
    "parameters": {"a": "5", "b": "3"}
  }'
```

## Architecture

- **Backend**: FastAPI web server
- **Frontend**: HTML with Alpine.js for reactivity
- **Styling**: Tailwind CSS for modern UI
- **MCP Integration**: Uses langchain-mcp-adapters for tool management

## Stopping the Server

Press `Ctrl+C` in the terminal to stop the web server.

## Troubleshooting

### Missing Dependencies
If you see an error about missing dependencies, install them:
```bash
pip install fastapi uvicorn
```

### Port Already in Use
If port 8000 is already in use, you can modify the port in the script:
```python
uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")  # Use port 8001
```

### Tool Loading Issues
If tools fail to load, ensure the test servers are working:
```bash
# Test individual servers
python tests/servers/math_server.py
python tests/servers/time_server.py
python tests/servers/weather_server.py
``` 