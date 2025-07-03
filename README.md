# MCP Tools Web Demo with AWS Terraform

A comprehensive web interface for testing Model Context Protocol (MCP) tools, including math operations, time functions, weather API, and AWS Terraform infrastructure management.

## 🚀 Features

- **Interactive Web Interface**: Clean, responsive UI built with TailwindCSS and Alpine.js
- **Multiple Tool Categories**:
  - 🧮 **Math Operations**: Addition, subtraction, multiplication, division
  - ⏰ **Time Functions**: Current time and date operations
  - 🌤️ **Weather API**: Location-based weather information
  - 🏗️ **AWS Terraform**: Infrastructure management and documentation search
- **Real-time Tool Execution**: Execute MCP tools directly from the browser
- **Tool Discovery**: Automatic categorization and filtering of available tools
- **Quick Test Examples**: Pre-configured test cases for common operations

## 📋 Prerequisites

### Required Dependencies
```bash
pip install fastapi uvicorn langchain-mcp-adapters
```

### Optional Dependencies
- **uvx**: For AWS Terraform MCP server integration
- **Python 3.8+**: Required for running the application

## 🛠️ Installation

1. **Clone or download the application**:
   ```bash
   # Save the script as mcp_web_demo.py
   ```

2. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn langchain-mcp-adapters
   ```

3. **Set up test servers** (optional):
   Create a `tests/servers/` directory with the following test servers:
   - `math_server.py`: Math operations
   - `time_server.py`: Time functions
   - `weather_server.py`: Weather API

4. **Install AWS Terraform MCP server** (optional):
   ```bash
   # Install uvx if not already installed
   pip install uvx
   ```

## 🚀 Usage

### Starting the Server
```bash
python mcp_web_demo.py
```

The web interface will be available at: **http://localhost:8000**

### Using the Web Interface

1. **Browse Available Tools**: View all available MCP tools categorized by type
2. **Filter Tools**: Use the search box to find specific tools
3. **Select a Tool**: Click on any tool to view its details and parameters
4. **Set Parameters**: Fill in required parameters for the selected tool
5. **Execute**: Click "Execute Tool" to run the tool and view results
6. **Quick Tests**: Use pre-configured examples for common operations

### Tool Categories

| Category | Description | Example Tools |
|----------|-------------|---------------|
| 🧮 **Math** | Basic arithmetic operations | `add`, `subtract`, `multiply`, `divide` |
| ⏰ **Time** | Date and time functions | `get_time`, `get_date` |
| 🌤️ **Weather** | Weather information | `get_weather` |
| 🏗️ **Terraform/AWS** | Infrastructure management | `SearchAwsProviderDocs`, `checkov` |

## 🔧 Configuration

### Server Configuration
The application is configured to connect to multiple MCP servers:

```python
server_configs = {
    "math": {
        "command": sys.executable,
        "args": [math_server_path],
        "transport": "stdio",
    },
    "time": {
        "command": sys.executable,
        "args": [time_server_path],
        "transport": "stdio",
    },
    "weather": {
        "command": sys.executable,
        "args": [weather_server_path],
        "transport": "stdio",
    },
    "terraform": {
        "command": "uvx",
        "args": ["awslabs.terraform-mcp-server@latest"],
        "transport": "stdio",
        "env": {
            "FASTMCP_LOG_LEVEL": "ERROR"
        }
    }
}
```

### Environment Variables
- `FASTMCP_LOG_LEVEL`: Controls logging level for the FastMCP server (default: ERROR)

## 📡 API Endpoints

### GET `/`
Returns the main web interface HTML page.

### GET `/api/tools`
Returns a JSON array of available MCP tools.

**Response Format**:
```json
[
  {
    "name": "tool_name",
    "description": "Tool description",
    "args_schema": {
      "properties": {
        "param1": {"type": "string"},
        "param2": {"type": "number"}
      }
    }
  }
]
```

### POST `/api/execute`
Executes a specified MCP tool with given parameters.

**Request Format**:
```json
{
  "tool_name": "add",
  "parameters": {
    "a": "5",
    "b": "3"
  }
}
```

**Response Format**:
```json
{
  "result": "8"
}
```

## 🧪 Testing Examples

### Math Operations
```bash
# Addition
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "add", "parameters": {"a": "5", "b": "3"}}'

# Multiplication
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "multiply", "parameters": {"a": "4", "b": "6"}}'
```

### Time Functions
```bash
# Get current time
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "get_time", "parameters": {}}'
```

### Weather API
```bash
# Get weather for San Francisco
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "get_weather", "parameters": {"location": "San Francisco"}}'
```

### AWS Terraform
```bash
# Search AWS provider documentation
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "SearchAwsProviderDocs", "parameters": {"asset_name": "aws_ec2_instance"}}'
```

## 🐛 Troubleshooting

### Common Issues

1. **Missing Dependencies**:
   ```bash
   pip install fastapi uvicorn langchain-mcp-adapters
   ```

2. **AWS Terraform Server Not Available**:
   - Install uvx: `pip install uvx`
   - Ensure internet connection for downloading the server

3. **Test Servers Missing**:
   - The application will work without test servers
   - Only AWS Terraform tools will be available

4. **Port Already in Use**:
   - Change the port in the `uvicorn.run()` call
   - Or kill the process using port 8000

### Debug Mode
To enable debug logging, modify the server configuration:
```python
"env": {
    "FASTMCP_LOG_LEVEL": "DEBUG"
}
```

## 🔒 Security Considerations

- The application runs on `0.0.0.0:8000` by default (accessible from any network interface)
- For production use, consider:
  - Restricting host to `127.0.0.1` for localhost only
  - Adding authentication and authorization
  - Using HTTPS with proper SSL certificates
  - Implementing rate limiting

## 📄 License

This project is provided as-is for educational and testing purposes. Please ensure you comply with the licenses of all dependencies and MCP servers used.

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional MCP server integrations
- Enhanced error handling
- Better UI/UX design
- Documentation improvements
- Test coverage

## 📞 Support

For issues related to:
- **FastAPI**: Check the [FastAPI documentation](https://fastapi.tiangolo.com/)
- **MCP Protocol**: Refer to the [MCP specification](https://modelcontextprotocol.io/)
- **AWS Terraform MCP**: Check the [AWS Labs repository](https://github.com/awslabs/terraform-mcp-server)

---

**Happy Testing!** �