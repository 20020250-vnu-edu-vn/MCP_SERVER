import asyncio
import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

async def main():
    print("Setting up connections to multiple MCP servers...")
    
    # Configure the client with multiple servers
    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": ["tests/servers/math_server.py"],
                "transport": "stdio",
            },
            "weather": {
                "command": "python",
                "args": ["tests/servers/weather_server.py"],
                "transport": "stdio",
            },
            "time": {
                "command": "python",
                "args": ["tests/servers/time_server.py"],
                "transport": "stdio",
            }
        }
    )
    
    # Get all tools from all servers
    print("Loading tools from all servers...")
    tools = await client.get_tools()
    print(f"Loaded tools: {[tool.name for tool in tools]}")
    
    # Create an agent with access to all tools
    model = ChatOpenAI(model="gpt-3.5-turbo")
    agent = create_react_agent(model, tools)
    
    # Test with math query
    print("\nRunning math query...")
    math_query = "What is 7 multiplied by 9?"
    math_response = await agent.ainvoke({"messages": [{"role": "user", "content": math_query}]})
    print("Math Response:")
    for message in math_response["messages"]:
        print(f"{message['role'].upper()}: {message['content']}")
    
    # Test with weather query
    print("\nRunning weather query...")
    weather_query = "What's the weather in New York?"
    weather_response = await agent.ainvoke({"messages": [{"role": "user", "content": weather_query}]})
    print("Weather Response:")
    for message in weather_response["messages"]:
        print(f"{message['role'].upper()}: {message['content']}")
    
    # Test with time query
    print("\nRunning time query...")
    time_query = "What time is it now?"
    time_response = await agent.ainvoke({"messages": [{"role": "user", "content": time_query}]})
    print("Time Response:")
    for message in time_response["messages"]:
        print(f"{message['role'].upper()}: {message['content']}")

if __name__ == "__main__":
    asyncio.run(main()) 