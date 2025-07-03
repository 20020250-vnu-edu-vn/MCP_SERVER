#!/usr/bin/env python3
"""Web UI demo for testing MCP tools."""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List

try:
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.responses import HTMLResponse
    import uvicorn
except ImportError:
    print("❌ Missing dependencies. Please install FastAPI and uvicorn:")
    print("pip install fastapi uvicorn")
    sys.exit(1)

from langchain_mcp_adapters.client import MultiServerMCPClient


# Global client instance
mcp_client = None
available_tools = []


async def initialize_mcp_client():
    """Initialize the MCP client with test servers and AWS Terraform MCP server."""
    global mcp_client, available_tools
    
    # Get absolute paths to test servers
    current_dir = os.path.dirname(os.path.abspath(__file__))
    math_server_path = os.path.join(current_dir, "tests", "servers", "math_server.py")
    time_server_path = os.path.join(current_dir, "tests", "servers", "time_server.py")
    weather_server_path = os.path.join(current_dir, "tests", "servers", "weather_server.py")
    
    # Create MCP client with test servers and AWS Terraform MCP server
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
    
    mcp_client = MultiServerMCPClient(server_configs)
    
    # Load available tools
    try:
        available_tools = await mcp_client.get_tools()
        print(f"✅ Loaded {len(available_tools)} MCP tools")
        
        # Print tool categories for debugging
        tool_categories = {}
        for tool in available_tools:
            # Try to categorize tools based on name patterns
            if any(keyword in tool.name.lower() for keyword in ['add', 'subtract', 'multiply', 'divide']):
                category = 'Math'
            elif any(keyword in tool.name.lower() for keyword in ['time', 'date']):
                category = 'Time'
            elif any(keyword in tool.name.lower() for keyword in ['weather', 'temperature']):
                category = 'Weather'
            elif any(keyword in tool.name.lower() for keyword in ['terraform', 'aws', 'checkov', 'provider']):
                category = 'Terraform/AWS'
            else:
                category = 'Other'
            
            if category not in tool_categories:
                tool_categories[category] = []
            tool_categories[category].append(tool.name)
        
        print("📊 Tool categories:")
        for category, tools in tool_categories.items():
            print(f"  {category}: {len(tools)} tools - {', '.join(tools[:3])}{'...' if len(tools) > 3 else ''}")
            
    except Exception as e:
        print(f"❌ Error loading tools: {e}")
        available_tools = []


# Create FastAPI app
app = FastAPI(title="MCP Tools Web Demo with AWS Terraform", description="Test MCP tools including AWS Terraform through a web interface")


@app.on_event("startup")
async def startup_event():
    """Initialize MCP client on startup."""
    await initialize_mcp_client()


@app.get("/", response_class=HTMLResponse)
async def main_page():
    """Serve the main page with tool testing interface."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MCP Tools Web Demo with AWS Terraform</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
    </head>
    <body class="bg-gray-50 min-h-screen">
        <div class="container mx-auto px-4 py-8" x-data="mcpDemo()">
            <div class="max-w-6xl mx-auto">
                <!-- Header -->
                <div class="text-center mb-8">
                    <h1 class="text-4xl font-bold text-gray-900 mb-2">🔧 MCP Tools Web Demo</h1>
                    <p class="text-gray-600">Test Model Context Protocol tools including AWS Terraform infrastructure</p>
                    <div class="mt-4 flex justify-center space-x-4 text-sm">
                        <span class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full">Math Operations</span>
                        <span class="bg-green-100 text-green-800 px-3 py-1 rounded-full">Time Functions</span>
                        <span class="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full">Weather API</span>
                        <span class="bg-purple-100 text-purple-800 px-3 py-1 rounded-full">AWS Terraform</span>
                    </div>
                </div>

                <!-- Tools List -->
                <div class="bg-white rounded-lg shadow-md p-6 mb-6">
                    <h2 class="text-2xl font-semibold mb-4">📋 Available Tools</h2>
                    
                    <!-- Tool Filter -->
                    <div class="mb-4">
                        <input type="text" 
                               placeholder="Filter tools..." 
                               x-model="toolFilter"
                               class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                    </div>
                    
                    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3" x-show="filteredTools.length > 0">
                        <template x-for="tool in filteredTools" :key="tool.name">
                            <div class="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                                 @click="selectTool(tool)"
                                 :class="selectedTool?.name === tool.name ? 'border-blue-500 bg-blue-50' : 'border-gray-200'">
                                <h3 class="font-medium text-lg mb-2 flex items-center">
                                    <span x-text="getToolIcon(tool.name)" class="mr-2"></span>
                                    <span x-text="tool.name"></span>
                                </h3>
                                <p class="text-gray-600 text-sm" x-text="tool.description"></p>
                                <div class="mt-2">
                                    <span x-text="getToolCategory(tool.name)" 
                                          class="inline-block px-2 py-1 text-xs rounded-full"
                                          :class="getCategoryClass(tool.name)"></span>
                                </div>
                            </div>
                        </template>
                    </div>
                    <div x-show="tools.length === 0" class="text-center text-gray-500">
                        Loading tools...
                    </div>
                    <div x-show="tools.length > 0 && filteredTools.length === 0" class="text-center text-gray-500">
                        No tools match your filter.
                    </div>
                </div>

                <!-- Tool Testing Interface -->
                <div x-show="selectedTool" class="bg-white rounded-lg shadow-md p-6">
                    <h2 class="text-2xl font-semibold mb-4 flex items-center">
                        🧪 Test Tool: 
                        <span x-text="getToolIcon(selectedTool?.name)" class="mx-2"></span>
                        <span x-text="selectedTool?.name"></span>
                    </h2>
                    
                    <!-- Tool Description -->
                    <div class="mb-6 p-4 bg-blue-50 rounded-lg">
                        <p class="text-blue-800" x-text="selectedTool?.description"></p>
                    </div>

                    <!-- Tool Parameters -->
                    <div class="mb-6" x-show="Object.keys(toolParams).length > 0">
                        <h3 class="text-lg font-medium mb-3">Parameters:</h3>
                        <div class="space-y-4">
                            <template x-for="(param, key) in toolParams" :key="key">
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-1" x-text="key"></label>
                                    <input type="text" 
                                           class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                           x-model="toolParams[key]"
                                           :placeholder="'Enter ' + key">
                                </div>
                            </template>
                        </div>
                    </div>

                    <div x-show="Object.keys(toolParams).length === 0" class="mb-6 text-gray-500">
                        This tool requires no parameters.
                    </div>

                    <!-- Execute Button -->
                    <div class="mb-6">
                        <button @click="executeTool()"
                                :disabled="executing"
                                class="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-6 rounded-md transition duration-200">
                            <span x-show="!executing">🚀 Execute Tool</span>
                            <span x-show="executing">⏳ Executing...</span>
                        </button>
                    </div>

                    <!-- Results -->
                    <div x-show="result" class="mt-6">
                        <h3 class="text-lg font-medium mb-3">📊 Result:</h3>
                        <div class="bg-green-50 border border-green-200 rounded-md p-4 max-h-96 overflow-y-auto">
                            <pre class="whitespace-pre-wrap text-sm text-green-800" x-text="result"></pre>
                        </div>
                    </div>

                    <!-- Error Display -->
                    <div x-show="error" class="mt-6">
                        <h3 class="text-lg font-medium mb-3 text-red-600">❌ Error:</h3>
                        <div class="bg-red-50 border border-red-200 rounded-md p-4">
                            <pre class="whitespace-pre-wrap text-sm text-red-800" x-text="error"></pre>
                        </div>
                    </div>
                </div>

                <!-- Quick Test Examples -->
                <div class="bg-white rounded-lg shadow-md p-6 mt-6">
                    <h2 class="text-2xl font-semibold mb-4">🚀 Quick Test Examples</h2>
                    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                        <!-- Math Examples -->
                        <div class="space-y-2">
                            <h3 class="font-medium text-blue-600">🧮 Math</h3>
                            <button @click="quickTest('add', {a: '5', b: '3'})" 
                                    class="w-full p-3 text-left border rounded-lg hover:bg-gray-50">
                                <div class="font-medium">Add Numbers</div>
                                <div class="text-sm text-gray-600">5 + 3</div>
                            </button>
                            <button @click="quickTest('multiply', {a: '4', b: '6'})" 
                                    class="w-full p-3 text-left border rounded-lg hover:bg-gray-50">
                                <div class="font-medium">Multiply</div>
                                <div class="text-sm text-gray-600">4 × 6</div>
                            </button>
                        </div>
                        
                        <!-- Time Examples -->
                        <div class="space-y-2">
                            <h3 class="font-medium text-green-600">⏰ Time</h3>
                            <button @click="quickTest('get_time', {})" 
                                    class="w-full p-3 text-left border rounded-lg hover:bg-gray-50">
                                <div class="font-medium">Current Time</div>
                                <div class="text-sm text-gray-600">Get current time</div>
                            </button>
                        </div>
                        
                        <!-- Weather Examples -->
                        <div class="space-y-2">
                            <h3 class="font-medium text-yellow-600">🌤️ Weather</h3>
                            <button @click="quickTest('get_weather', {location: 'San Francisco'})" 
                                    class="w-full p-3 text-left border rounded-lg hover:bg-gray-50">
                                <div class="font-medium">SF Weather</div>
                                <div class="text-sm text-gray-600">San Francisco</div>
                            </button>
                        </div>
                        
                        <!-- AWS Terraform Examples -->
                        <div class="space-y-2">
                            <h3 class="font-medium text-purple-600">🏗️ AWS/Terraform</h3>
                            <button @click="quickTestTerraform('SearchAwsProviderDocs', {asset_name: 'aws_ec2_instance'})" 
                                    class="w-full p-3 text-left border rounded-lg hover:bg-gray-50">
                                <div class="font-medium">EC2 Docs</div>
                                <div class="text-sm text-gray-600">AWS EC2 instance docs</div>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            function mcpDemo() {
                return {
                    tools: [],
                    selectedTool: null,
                    toolParams: {},
                    result: '',
                    error: '',
                    executing: false,
                    toolFilter: '',

                    get filteredTools() {
                        if (!this.toolFilter) return this.tools;
                        return this.tools.filter(tool => 
                            tool.name.toLowerCase().includes(this.toolFilter.toLowerCase()) ||
                            tool.description.toLowerCase().includes(this.toolFilter.toLowerCase())
                        );
                    },

                    async init() {
                        await this.loadTools();
                    },

                    async loadTools() {
                        try {
                            const response = await fetch('/api/tools');
                            this.tools = await response.json();
                        } catch (err) {
                            console.error('Failed to load tools:', err);
                        }
                    },

                    getToolIcon(toolName) {
                        if (!toolName) return '🔧';
                        const name = toolName.toLowerCase();
                        if (name.includes('add') || name.includes('subtract') || name.includes('multiply') || name.includes('divide')) return '🧮';
                        if (name.includes('time') || name.includes('date')) return '⏰';
                        if (name.includes('weather') || name.includes('temperature')) return '🌤️';
                        if (name.includes('terraform') || name.includes('aws') || name.includes('checkov')) return '🏗️';
                        if (name.includes('search') || name.includes('docs')) return '📚';
                        if (name.includes('execute') || name.includes('run')) return '▶️';
                        return '🔧';
                    },

                    getToolCategory(toolName) {
                        if (!toolName) return 'Other';
                        const name = toolName.toLowerCase();
                        if (name.includes('add') || name.includes('subtract') || name.includes('multiply') || name.includes('divide')) return 'Math';
                        if (name.includes('time') || name.includes('date')) return 'Time';
                        if (name.includes('weather') || name.includes('temperature')) return 'Weather';
                        if (name.includes('terraform') || name.includes('aws') || name.includes('checkov')) return 'Terraform/AWS';
                        return 'Other';
                    },

                    getCategoryClass(toolName) {
                        const category = this.getToolCategory(toolName);
                        switch(category) {
                            case 'Math': return 'bg-blue-100 text-blue-800';
                            case 'Time': return 'bg-green-100 text-green-800';
                            case 'Weather': return 'bg-yellow-100 text-yellow-800';
                            case 'Terraform/AWS': return 'bg-purple-100 text-purple-800';
                            default: return 'bg-gray-100 text-gray-800';
                        }
                    },

                    selectTool(tool) {
                        this.selectedTool = tool;
                        this.toolParams = {};
                        this.result = '';
                        this.error = '';
                        
                        // Initialize parameters based on tool schema
                        if (tool.args_schema && tool.args_schema.properties) {
                            for (const [key, value] of Object.entries(tool.args_schema.properties)) {
                                this.toolParams[key] = '';
                            }
                        }
                    },

                    async quickTest(toolName, params) {
                        const tool = this.tools.find(t => t.name === toolName);
                        if (tool) {
                            this.selectTool(tool);
                            this.toolParams = { ...params };
                            await this.executeTool();
                        }
                    },

                    async quickTestTerraform(toolName, params) {
                        // Find terraform-related tools by checking if they contain the tool name
                        const tool = this.tools.find(t => t.name.includes(toolName) || t.name === toolName);
                        if (tool) {
                            this.selectTool(tool);
                            this.toolParams = { ...params };
                            await this.executeTool();
                        } else {
                            this.error = `Terraform tool '${toolName}' not found. Available tools: ${this.tools.map(t => t.name).join(', ')}`;
                        }
                    },

                    async executeTool() {
                        if (!this.selectedTool) return;
                        
                        this.executing = true;
                        this.result = '';
                        this.error = '';

                        try {
                            const response = await fetch('/api/execute', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({
                                    tool_name: this.selectedTool.name,
                                    parameters: this.toolParams
                                })
                            });

                            const data = await response.json();
                            
                            if (response.ok) {
                                this.result = data.result;
                            } else {
                                this.error = data.error || 'Unknown error occurred';
                            }
                        } catch (err) {
                            this.error = 'Network error: ' + err.message;
                        } finally {
                            this.executing = false;
                        }
                    }
                }
            }
        </script>
    </body>
    </html>
    """
    return html_content


@app.get("/api/tools")
async def get_tools():
    """Get available tools as JSON."""
    tools_data = []
    for tool in available_tools:
        tools_data.append({
            "name": tool.name,
            "description": tool.description,
            "args_schema": tool.args_schema if hasattr(tool, 'args_schema') else {}
        })
    return tools_data


@app.post("/api/execute")
async def execute_tool(request: Request):
    """Execute a tool with given parameters."""
    try:
        data = await request.json()
        tool_name = data.get("tool_name")
        parameters = data.get("parameters", {})
        
        # Find the tool
        tool = None
        for t in available_tools:
            if t.name == tool_name:
                tool = t
                break
        
        if not tool:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        
        # Clean up parameters (remove empty strings, convert numeric strings)
        clean_params = {}
        for k, v in parameters.items():
            if v != "":
                # Try to convert to appropriate type
                if v.isdigit():
                    clean_params[k] = int(v)
                elif v.replace('.', '').isdigit():
                    clean_params[k] = float(v)
                else:
                    clean_params[k] = v
        
        # Execute the tool
        result = await tool.ainvoke({
            "args": clean_params,
            "id": f"web_ui_{tool_name}",
            "type": "tool_call"
        })
        
        return {"result": result.content}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Run the web demo."""
    print("🚀 Starting MCP Tools Web Demo...")
    print("📝 Make sure you have FastAPI and uvicorn installed:")
    print("   pip install fastapi uvicorn")
    print()
    print("🌐 Web interface will be available at: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop the server")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()
