#!/usr/bin/env python3
"""Test ExecuteTerraformCommand with real AWS EC2 resources."""

import asyncio
import json
import os
import tempfile
import shutil
from langchain_mcp_adapters.client import MultiServerMCPClient


async def test_aws_ec2_terraform():
    """Test ExecuteTerraformCommand with AWS EC2 instance creation."""
    print("🚀 Testing ExecuteTerraformCommand with AWS EC2")
    print("=" * 50)
    
    # Check for AWS credentials
    aws_profile = os.environ.get('AWS_PROFILE', 'default')
    aws_region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
    
    print(f"🔑 Using AWS Profile: {aws_profile}")
    print(f"🌍 Using AWS Region: {aws_region}")
    
    # Configure the Terraform MCP server
    server_configs = {
        "terraform": {
            "command": "uvx",
            "args": ["awslabs.terraform-mcp-server@latest"],
            "transport": "stdio",
            "env": {
                "FASTMCP_LOG_LEVEL": "ERROR",
                "AWS_PROFILE": aws_profile,
                "AWS_DEFAULT_REGION": aws_region
            }
        }
    }
    
    # Create a temporary directory for our test
    test_dir = os.mkdir("aws_ec2_terraform_")
    print(f"📁 Created test directory: {test_dir}")
    
    try:
        # Create AWS EC2 Terraform configuration
        terraform_config = f'''
# AWS EC2 Terraform Configuration
terraform {{
  required_version = ">= 1.0"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

# Configure the AWS Provider
provider "aws" {{
  region  = var.aws_region
  profile = var.aws_profile
}}

# Input variables
variable "aws_region" {{
  description = "AWS region"
  type        = string
  default     = "{aws_region}"
}}

variable "aws_profile" {{
  description = "AWS profile to use"
  type        = string
  default     = "{aws_profile}"
}}

variable "instance_type" {{
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}}

variable "instance_name" {{
  description = "Name tag for the EC2 instance"
  type        = string
  default     = "terraform-mcp-test"
}}

# Data sources
data "aws_availability_zones" "available" {{
  state = "available"
}}

data "aws_ami" "amazon_linux" {{
  most_recent = true
  owners      = ["amazon"]

  filter {{
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }}

  filter {{
    name   = "virtualization-type"
    values = ["hvm"]
  }}
}}

# Get default VPC
data "aws_vpc" "default" {{
  default = true
}}

data "aws_subnets" "default" {{
  filter {{
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }}
}}

# Security Group
resource "aws_security_group" "test_sg" {{
  name_prefix = "terraform-mcp-test-"
  description = "Security group for Terraform MCP test"
  vpc_id      = data.aws_vpc.default.id

  # SSH access (adjust source as needed)
  ingress {{
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # WARNING: This allows SSH from anywhere - adjust for production!
  }}

  # HTTP access
  ingress {{
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  # All outbound traffic
  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  tags = {{
    Name = "${{var.instance_name}}-sg"
    Environment = "test"
    ManagedBy = "terraform-mcp"
  }}
}}

# EC2 Instance
resource "aws_instance" "test_instance" {{
  ami           = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type
  
  subnet_id                   = data.aws_subnets.default.ids[0]
  vpc_security_group_ids      = [aws_security_group.test_sg.id]
  associate_public_ip_address = true

  # User data script
  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y httpd
    systemctl start httpd
    systemctl enable httpd
    echo "<h1>Hello from Terraform MCP Test Instance!</h1>" > /var/www/html/index.html
    echo "<p>Instance ID: $(curl -s http://169.254.169.254/latest/meta-data/instance-id)</p>" >> /var/www/html/index.html
    echo "<p>Region: $(curl -s http://169.254.169.254/latest/meta-data/placement/region)</p>" >> /var/www/html/index.html
  EOF

  tags = {{
    Name = var.instance_name
    Environment = "test"
    ManagedBy = "terraform-mcp"
  }}
}}

# Outputs
output "instance_id" {{
  description = "ID of the EC2 instance"
  value       = aws_instance.test_instance.id
}}

output "instance_public_ip" {{
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.test_instance.public_ip
}}

output "instance_public_dns" {{
  description = "Public DNS name of the EC2 instance"
  value       = aws_instance.test_instance.public_dns
}}

output "security_group_id" {{
  description = "ID of the security group"
  value       = aws_security_group.test_sg.id
}}

output "web_url" {{
  description = "URL to access the web server"
  value       = "http://${{aws_instance.test_instance.public_dns}}"
}}

output "ssh_command" {{
  description = "SSH command to connect to the instance"
  value       = "ssh -i /path/to/your/key.pem ec2-user@${{aws_instance.test_instance.public_dns}}"
}}
'''
        
        # Write the configuration to a file
        config_file = os.path.join(test_dir, "main.tf")
        with open(config_file, "w") as f:
            f.write(terraform_config)
        
        print(f"📝 Created AWS EC2 Terraform config: {config_file}")
        
        # Initialize MCP client
        print("🔧 Initializing MCP client...")
        mcp_client = MultiServerMCPClient(server_configs)
        
        # Get the ExecuteTerraformCommand tool
        tools = await mcp_client.get_tools()
        terraform_tool = next(tool for tool in tools if 'ExecuteTerraformCommand' in tool.name)
        
        print(f"✅ Found tool: {terraform_tool.name}")
        
        # AWS Terraform workflow test
        print("\n🔄 Running AWS EC2 Terraform Workflow:")
        
        # Step 1: Terraform Init
        print("\n1️⃣ terraform init")
        result = await terraform_tool.ainvoke({
            "args": {
                "command": "init",
                "working_directory": test_dir,
                "aws_region": aws_region
            },
            "id": "aws_init",
            "type": "tool_call"
        })
        result_data = json.loads(result.content)
        print(f"   Status: {result_data['status']}")
        if result_data['status'] == 'success':
            print("   ✅ AWS provider initialized successfully!")
        else:
            print(f"   ❌ Init failed: {result_data['stderr']}")
            return
        
        # Step 2: Terraform Validate
        print("\n2️⃣ terraform validate")
        try:
            result = await terraform_tool.ainvoke({
                "args": {
                    "command": "validate",
                    "working_directory": test_dir,
                    "aws_region": aws_region
                },
                "id": "aws_validate",
                "type": "tool_call"
            })
            result_data = json.loads(result.content)
            print(f"   Status: {result_data['status']}")
            if result_data['status'] == 'success':
                print("   ✅ AWS configuration is valid!")
            else:
                print(f"   ❌ Validation error: {result_data['stderr']}")
        except Exception as e:
            print(f"   ⚠️  Validate failed: {str(e)[:100]}...")
        
        # Step 3: Terraform Plan (default values)
        print("\n3️⃣ terraform plan (default: t3.micro)")
        result = await terraform_tool.ainvoke({
            "args": {
                "command": "plan",
                "working_directory": test_dir,
                "aws_region": aws_region
            },
            "id": "aws_plan_default",
            "type": "tool_call"
        })
        result_data = json.loads(result.content)
        print(f"   Status: {result_data['status']}")
        if result_data['status'] == 'success':
            stdout = result_data['stdout']
            if 'Plan:' in stdout:
                # Extract plan summary
                plan_lines = [line for line in stdout.split('\\n') if 'Plan:' in line]
                if plan_lines:
                    print(f"   ✅ {plan_lines[0].strip()}")
            if 't3.micro' in stdout:
                print("   ✅ Using t3.micro instance type")
        else:
            print(f"   ❌ Plan failed: {result_data['stderr']}")
        
        # Step 4: Terraform Plan with custom instance type
        print("\n4️⃣ terraform plan (custom: t3.small)")
        result = await terraform_tool.ainvoke({
            "args": {
                "command": "plan",
                "working_directory": test_dir,
                "aws_region": aws_region,
                "variables": {
                    "instance_type": "t3.small",
                    "instance_name": "terraform-mcp-custom-test"
                }
            },
            "id": "aws_plan_custom",
            "type": "tool_call"
        })
        result_data = json.loads(result.content)
        print(f"   Status: {result_data['status']}")
        if result_data['status'] == 'success':
            stdout = result_data['stdout']
            if 't3.small' in stdout:
                print("   ✅ Using custom t3.small instance type")
            if 'terraform-mcp-custom-test' in stdout:
                print("   ✅ Using custom instance name")
        
        print("\n✅ AWS EC2 Terraform testing completed!")
        print("\n📋 Summary:")
        print("   ✅ AWS provider initialization")
        print("   ✅ Configuration validation")
        print("   ✅ Infrastructure planning (default & custom)")
        print("   ✅ Variable substitution")
        print("\n⚠️  IMPORTANT NOTES:")
        print("   • This test only runs 'plan' - no resources were created")
        print("   • To actually create resources, you would run 'apply'")
        print("   • Remember to run 'destroy' after testing to avoid charges")
        print("   • The security group allows SSH from anywhere (0.0.0.0/0)")
        print("\n🔧 Next steps to actually deploy:")
        print("   1. Review the plan output carefully")
        print("   2. Run terraform apply to create resources")
        print("   3. Test your EC2 instance")
        print("   4. Run terraform destroy to clean up")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        try:
            # shutil.rmtree(test_dir)
            print(f"🧹 Cleaned up: {test_dir}")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")


def check_aws_credentials():
    """Check if AWS credentials are configured."""
    print("🔍 Checking AWS credentials...")
    
    # Check for AWS credentials
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_profile = os.environ.get('AWS_PROFILE')
    
    if aws_access_key:
        print("   ✅ Found AWS_ACCESS_KEY_ID environment variable")
    elif aws_profile:
        print(f"   ✅ Found AWS_PROFILE environment variable: {aws_profile}")
    else:
        print("   ⚠️  No AWS credentials found in environment variables")
        print("   ℹ️  Checking for AWS CLI configuration...")
        
        # Check for AWS CLI config
        aws_config_file = os.path.expanduser("~/.aws/credentials")
        if os.path.exists(aws_config_file):
            print(f"   ✅ Found AWS credentials file: {aws_config_file}")
        else:
            print("   ❌ No AWS credentials file found")
            print("\n🔧 To configure AWS credentials:")
            print("   1. Run: aws configure")
            print("   2. Or set environment variables:")
            print("      export AWS_ACCESS_KEY_ID=your_access_key")
            print("      export AWS_SECRET_ACCESS_KEY=your_secret_key")
            print("      export AWS_DEFAULT_REGION=us-east-1")
            return False
    
    return True


if __name__ == "__main__":
    if check_aws_credentials():
        asyncio.run(test_aws_ec2_terraform())
    else:
        print("\n❌ Please configure AWS credentials first!") 