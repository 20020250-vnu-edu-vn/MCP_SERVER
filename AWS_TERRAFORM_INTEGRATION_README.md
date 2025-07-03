# AWS Terraform MCP Integration

This project integrates the [AWS Terraform MCP Server](https://awslabs.github.io/mcp/servers/terraform-mcp-server/) into your existing MCP tools web demo, providing powerful AWS infrastructure and Terraform capabilities through a web interface.

## 🚀 Quick Start

1. **Run the setup script:**
   ```bash
   python setup_terraform_demo.py
   ```

2. **Configure AWS credentials:**
   ```bash
   aws configure
   # OR set environment variables
   export AWS_ACCESS_KEY_ID=your-key
   export AWS_SECRET_ACCESS_KEY=your-secret
   export AWS_DEFAULT_REGION=us-east-1
   ```

3. **Start the demo:**
   ```bash
   python demo_mcp_tools.py
   ```

4. **Open your browser:**
   ```
   http://localhost:8000
   ```

## 🔧 What's New

### Enhanced Web Interface
- **Tool Categorization**: Visual categories (Math, Time, Weather, Terraform/AWS)
- **Tool Filtering**: Search and filter tools by name or description
- **Enhanced UI**: Better icons, categories, and improved layout
- **AWS Examples**: Quick test buttons for Terraform/AWS tools

### AWS Terraform MCP Server Integration
The integration adds the following capabilities:

#### 🏗️ **Infrastructure as Code**
- **Terraform Best Practices**: AWS Well-Architected guidance
- **Security-First Workflow**: Integrated Checkov security scanning
- **AWSCC Provider Support**: Consistent AWS API behavior

#### 📚 **Documentation & Research**
- **AWS Provider Docs**: Search AWS and AWSCC provider resources
- **Module Analysis**: Analyze Terraform Registry modules
- **AWS-IA GenAI Modules**: Specialized AI/ML infrastructure modules

#### ⚡ **Workflow Execution**
- **Terraform Commands**: Run init, plan, validate, apply, destroy
- **Terragrunt Support**: Multi-module operations with run-all
- **Security Scanning**: Checkov integration for compliance

### Available Tools

The AWS Terraform MCP Server provides these tools (exact names may vary):

| Tool Category | Example Tools | Description |
|---------------|---------------|-------------|
| **Documentation** | `SearchAwsProviderDocs` | Search AWS Terraform provider documentation |
| **Security** | `RunCheckovScan` | Security and compliance scanning |
| **Modules** | `SearchSpecificAwsIaModules` | AI/ML focused AWS infrastructure modules |
| **Workflow** | `ExecuteTerraformCommand` | Run Terraform commands directly |
| **Analysis** | `SearchUserProvidedModule` | Analyze any Terraform registry module |

## 🛠️ Prerequisites

### Required Tools
- **Python 3.10+**: For running the web demo
- **uv/uvx**: Package manager for MCP server installation
- **AWS CLI**: For credential configuration (optional)

### Optional Tools (for full functionality)
- **Terraform CLI**: For workflow execution features
- **Checkov**: For security scanning (`pip install checkov`)

### AWS Setup
1. **AWS Account**: With appropriate permissions
2. **AWS Credentials**: Configured via `aws configure` or environment variables
3. **IAM Permissions**: Depending on what Terraform operations you plan to run

## 🎯 Usage Examples

### 1. Search AWS Provider Documentation
```javascript
// In the web interface, use:
Tool: SearchAwsProviderDocs
Parameters: {
  "asset_name": "aws_s3_bucket",
  "asset_type": "resource"
}
```

### 2. Analyze Terraform Modules
```javascript
// Search for AI/ML modules:
Tool: SearchSpecificAwsIaModules
Parameters: {
  "query": "bedrock"
}
```

### 3. Security Scanning
```javascript
// Scan Terraform code:
Tool: RunCheckovScan
Parameters: {
  "working_directory": "/path/to/terraform/code"
}
```

### 4. Terraform Workflow
```javascript
// Initialize Terraform:
Tool: ExecuteTerraformCommand
Parameters: {
  "command": "init",
  "working_directory": "/path/to/terraform/code"
}
```

## 🔒 Security Considerations

### AWS Credentials
- Credentials are used locally and never sent to external services
- Use IAM roles with least privilege principle
- Consider using temporary credentials via AWS STS

### Terraform Operations
- **Read-only by default**: Many tools are read-only for safety
- **Review before apply**: Always review Terraform plans before applying
- **Use workspaces**: Separate dev/staging/prod environments

### Checkov Scanning
- Review all security findings before proceeding
- Fix issues rather than ignoring them when possible
- Document justifications for any necessary exceptions

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │    │   FastAPI App   │    │  MCP Client     │
│                 │    │                 │    │                 │
│ - Tool Interface│◄──►│ - HTTP API      │◄──►│ - Multi-server  │
│ - Parameters    │    │ - Tool Execution│    │ - Coordination  │
│ - Results       │    │ - Error Handling│    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                       ┌─────────────────────────────────┼─────────────────────────────────┐
                       │                                 │                                 │
                       ▼                                 ▼                                 ▼
              ┌─────────────────┐              ┌─────────────────┐              ┌─────────────────┐
              │   Math Server   │              │ Weather Server  │              │Terraform Server │
              │                 │              │                 │              │                 │
              │ - Add/Subtract  │              │ - Get Weather   │              │ - AWS Docs      │
              │ - Multiply/Div  │              │ - Location API  │              │ - Terraform CLI │
              │                 │              │                 │              │ - Checkov Scan  │
              └─────────────────┘              └─────────────────┘              └─────────────────┘
```

## 🔧 Configuration

### MCP Client Configuration
The demo automatically configures the AWS Terraform MCP server, but you can also use it with other MCP clients:

```json
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
```

### Environment Variables
```bash
# AWS Configuration
export AWS_PROFILE=your-aws-profile
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret

# MCP Configuration  
export FASTMCP_LOG_LEVEL=ERROR
```

## 🐛 Troubleshooting

### Common Issues

1. **uvx not found**
   ```bash
   pip install uv
   ```

2. **AWS credentials not configured**
   ```bash
   aws configure
   # OR set environment variables
   ```

3. **Terraform tools not working**
   - Ensure AWS credentials are properly configured
   - Check if you have necessary AWS permissions
   - Verify the working directory exists and contains Terraform files

4. **Connection errors**
   - Check if the MCP server is running
   - Verify network connectivity
   - Look at server logs for detailed error messages

### Debug Mode
To enable debug logging:
```bash
export FASTMCP_LOG_LEVEL=DEBUG
python demo_mcp_tools.py
```

## 📚 Resources

- **AWS Terraform MCP Server**: https://awslabs.github.io/mcp/servers/terraform-mcp-server/
- **AWS MCP Servers**: https://awslabs.github.io/mcp/
- **Model Context Protocol**: https://modelcontextprotocol.io/
- **AWS Terraform Provider**: https://registry.terraform.io/providers/hashicorp/aws/
- **Checkov Documentation**: https://www.checkov.io/

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project follows the same license as the parent project. See LICENSE file for details.

---

**Need help?** Check the troubleshooting section above or refer to the [AWS Terraform MCP Server documentation](https://awslabs.github.io/mcp/servers/terraform-mcp-server/). 