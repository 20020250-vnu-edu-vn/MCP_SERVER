#!/usr/bin/env python3
"""Test script for AWS Terraform MCP integration."""

import asyncio
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from langchain_mcp_adapters.client import MultiServerMCPClient

async def test_integration():
    """Test the AWS Terraform MCP integration."""
    print("🧪 Testing AWS Terraform MCP Integration")
    print("=" * 50)
    
    # Get paths to test servers
    current_dir = Path(__file__).parent
    math_server_path = current_dir / "tests" / "servers" / "math_server.py"
    time_server_path = current_dir / "tests" / "servers" / "time_server.py"
    weather_server_path = current_dir / "tests" / "servers" / "weather_server.py"
    
    # Server configurations
    server_configs = {
        "math": {
            "command": sys.executable,
            "args": [str(math_server_path)],
            "transport": "stdio",
        },
        "time": {
            "command": sys.executable,
            "args": [str(time_server_path)],
            "transport": "stdio",
        },
        "weather": {
            "command": sys.executable,
            "args": [str(weather_server_path)],
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
    
    try:
        print("🔄 Initializing MCP client...")
        client = MultiServerMCPClient(server_configs)
        
        print("🔄 Loading tools from all servers...")
        tools = await client.get_tools()
        
        print(f"✅ Successfully loaded {len(tools)} tools!")
        
        # Categorize tools
        categories = {
            'Math': [],
            'Time': [],
            'Weather': [],
            'Terraform/AWS': [],
            'Other': []
        }
        
        for tool in tools:
            name = tool.name.lower()
            if any(keyword in name for keyword in ['add', 'subtract', 'multiply', 'divide']):
                categories['Math'].append(tool.name)
            elif any(keyword in name for keyword in ['time', 'date']):
                categories['Time'].append(tool.name)
            elif any(keyword in name for keyword in ['weather', 'temperature']):
                categories['Weather'].append(tool.name)
            elif any(keyword in name for keyword in ['terraform', 'aws', 'checkov', 'provider']):
                categories['Terraform/AWS'].append(tool.name)
            else:
                categories['Other'].append(tool.name)
        
        print("\n📊 Tool Categories:")
        for category, tool_names in categories.items():
            if tool_names:
                print(f"  {category}: {len(tool_names)} tools")
                for tool_name in tool_names:
                    print(f"    - {tool_name}")
        
        # Test a simple math operation
        print("\n🧮 Testing Math Tool...")
        try:
            add_tool = next(tool for tool in tools if tool.name == 'add')
            result = await add_tool.ainvoke({
                "args": {"a": 5, "b": 3},
                "id": "test_add",
                "type": "tool_call"
            })
            print(f"✅ Math test (5 + 3): {result.content}")
        except Exception as e:
            print(f"❌ Math test failed: {e}")
        
        # Test AWS provider docs search (if available)
        aws_tools = [tool for tool in tools if 'aws' in tool.name.lower() and 'provider' in tool.name.lower()]
        if aws_tools:
            print("\n🏗️ Testing AWS Terraform Tool...")
            try:
                aws_tool = aws_tools[0]
                print(f"Found AWS tool: {aws_tool.name}")
                print(f"Description: {aws_tool.description}")
                
                # Test with a simple S3 bucket search
                result = await aws_tool.ainvoke({
                    "args": {"asset_name": "aws_s3_bucket"},
                    "id": "test_aws_docs",
                    "type": "tool_call"
                })
                print("✅ AWS docs search successful!")
                print(f"Result preview: {str(result.content)[:200]}...")
            except Exception as e:
                print(f"❌ AWS tool test failed: {e}")
        else:
            print("\n⚠️  No AWS provider tools found")
        
        print(f"\n🎉 Integration test completed successfully!")
        print(f"📝 Total tools available: {len(tools)}")
        print(f"🏗️ AWS/Terraform tools: {len(categories['Terraform/AWS'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_integration())
    sys.exit(0 if success else 1) 