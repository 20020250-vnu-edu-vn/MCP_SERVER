#!/usr/bin/env python3
"""Setup script for AWS Terraform MCP integration demo."""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"   Stdout: {e.stdout}")
        if e.stderr:
            print(f"   Stderr: {e.stderr}")
        return False

def check_prerequisites():
    """Check if required tools are installed."""
    print("🔍 Checking prerequisites...")
    
    # Check for Python
    try:
        python_version = subprocess.run([sys.executable, "--version"], capture_output=True, text=True, check=True)
        print(f"✅ Python: {python_version.stdout.strip()}")
    except:
        print("❌ Python not found")
        return False
    
    # Check for uvx
    try:
        uvx_result = subprocess.run(["uvx", "--version"], capture_output=True, text=True, check=True)
        print(f"✅ uvx: {uvx_result.stdout.strip()}")
    except:
        print("❌ uvx not found. Installing...")
        if not run_command("pip install uv", "Installing uv"):
            return False
    
    return True

def install_dependencies():
    """Install required Python dependencies."""
    print("\n📦 Installing Python dependencies...")
    
    dependencies = [
        "fastapi",
        "uvicorn",
        "langchain-core",
        "mcp"
    ]
    
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            return False
    
    return True

def test_terraform_server():
    """Test if the Terraform MCP server can be accessed."""
    print("\n🧪 Testing AWS Terraform MCP server...")
    
    # This will download the server if not available
    test_command = "uvx awslabs.terraform-mcp-server@latest --help"
    if run_command(test_command, "Testing Terraform MCP server"):
        print("✅ AWS Terraform MCP server is ready")
        return True
    else:
        print("❌ AWS Terraform MCP server test failed")
        return False

def create_example_config():
    """Create an example configuration file for the MCP setup."""
    print("\n📝 Creating example configuration...")
    
    config_content = """# Example MCP Configuration for AWS Terraform Integration
# 
# This file shows how to configure the AWS Terraform MCP server
# for use with various MCP clients.

## For Amazon Q Developer CLI (~/.aws/amazonq/mcp.json):
{
  "mcpServers": {
    "awslabs.terraform-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.terraform-mcp-server@latest"],
      "env": {
        "AWS_PROFILE": "your-aws-profile",
        "AWS_REGION": "us-east-1",
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}

## Environment Variables (optional):
# AWS_PROFILE=your-aws-profile
# AWS_REGION=us-east-1
# FASTMCP_LOG_LEVEL=ERROR

## Available Tools:
# - SearchAwsProviderDocs: Search AWS Terraform provider documentation
# - SearchAwsccProviderDocs: Search AWSCC provider documentation  
# - SearchSpecificAwsIaModules: Search AWS-IA modules for AI/ML workloads
# - SearchUserProvidedModule: Analyze any Terraform registry module
# - ExecuteTerraformCommand: Run Terraform commands (init, plan, apply, etc.)
# - ExecuteTerragruntCommand: Run Terragrunt commands
# - RunCheckovScan: Security scanning with Checkov

## Prerequisites:
# 1. AWS credentials configured (aws configure or environment variables)
# 2. Terraform CLI installed (for workflow execution)
# 3. Checkov installed (for security scanning): pip install checkov
"""
    
    try:
        with open("terraform_mcp_config_example.txt", "w") as f:
            f.write(config_content)
        print("✅ Created terraform_mcp_config_example.txt")
        return True
    except Exception as e:
        print(f"❌ Failed to create config file: {e}")
        return False

def print_next_steps():
    """Print next steps for the user."""
    print("\n🎉 Setup completed! Next steps:")
    print("\n1. 🔧 Configure AWS credentials (if not already done):")
    print("   aws configure")
    print("   # OR set environment variables:")
    print("   export AWS_ACCESS_KEY_ID=your-key")
    print("   export AWS_SECRET_ACCESS_KEY=your-secret")
    print("   export AWS_DEFAULT_REGION=us-east-1")
    
    print("\n2. 🚀 Run the enhanced demo:")
    print("   python demo_mcp_tools.py")
    
    print("\n3. 🌐 Open your browser to:")
    print("   http://localhost:8000")
    
    print("\n4. 🏗️ Try AWS Terraform tools:")
    print("   - Search AWS provider docs")
    print("   - Analyze Terraform modules")
    print("   - Run Terraform commands")
    print("   - Security scanning with Checkov")
    
    print("\n5. 📖 See terraform_mcp_config_example.txt for:")
    print("   - MCP client configuration examples")
    print("   - Available tools and features")
    print("   - Prerequisites and setup notes")
    
    print("\n📚 Documentation:")
    print("   - AWS Terraform MCP Server: https://awslabs.github.io/mcp/servers/terraform-mcp-server/")
    print("   - AWS MCP Servers: https://awslabs.github.io/mcp/")

def main():
    """Main setup function."""
    print("🔧 AWS Terraform MCP Integration Setup")
    print("=" * 50)
    
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed. Please install missing tools.")
        sys.exit(1)
    
    if not install_dependencies():
        print("\n❌ Dependency installation failed.")
        sys.exit(1)
    
    if not test_terraform_server():
        print("\n⚠️  Terraform server test failed, but continuing...")
    
    if not create_example_config():
        print("\n⚠️  Config file creation failed, but continuing...")
    
    print_next_steps()

if __name__ == "__main__":
    main() 