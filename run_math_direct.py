import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

async def main():
    # Set up the server parameters for the math server
    server_params = StdioServerParameters(
        command="python",
        args=["tests/servers/math_server.py"],
    )
    
    print("Starting MCP client session...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # Get tools
            print("Loading MCP tools...")
            tools = await load_mcp_tools(session)
            print(f"Loaded tools: {[tool.name for tool in tools]}")
            
            # Directly call the tools without using an agent
            print("\nTesting the 'add' tool...")
            add_tool = next(tool for tool in tools if tool.name == "add")
            add_result = await add_tool.ainvoke({"a": 3, "b": 5})
            print(f"3 + 5 = {add_result}")
            
            print("\nTesting the 'multiply' tool...")
            multiply_tool = next(tool for tool in tools if tool.name == "multiply")
            multiply_result = await multiply_tool.ainvoke({"a": 7, "b": 8})
            print(f"7 * 8 = {multiply_result}")

if __name__ == "__main__":
    asyncio.run(main()) 