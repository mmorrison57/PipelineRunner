#!/usr/bin/env python3
"""
Setup script for Azure DevOps MCP server authentication.
This script helps configure all authentication methods for the AdoMcp tool.
"""

import subprocess
import sys
import os
import time

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_step(step_num, title):
    """Print a formatted step."""
    print(f"\n[Step {step_num}] {title}")
    print("-" * 40)

def run_command(command, description, required=True):
    """Run a command and return success status."""
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {description}: SUCCESS")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description}: FAILED")
            if result.stderr.strip():
                print(f"Error: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ {description}: TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {description}: ERROR - {e}")
        return False

def check_azure_cli():
    """Check if Azure CLI is installed."""
    print_step(1, "Checking Azure CLI Installation")
    
    success = run_command("az --version", "Azure CLI version check", required=False)
    
    if not success:
        print("\n⚠️ Azure CLI is not installed or not in PATH")
        print("Please install Azure CLI from: https://aka.ms/installazurecliwindows")
        print("After installation, restart your terminal and run this script again.")
        return False
    
    return True

def install_devops_extension():
    """Install Azure DevOps CLI extension."""
    print_step(2, "Installing Azure DevOps Extension")
    
    # Check if already installed
    result = subprocess.run("az extension list", shell=True, capture_output=True, text=True)
    if "azure-devops" in result.stdout:
        print("✅ Azure DevOps extension is already installed")
        return True
    
    success = run_command(
        "az extension add --name azure-devops", 
        "Azure DevOps extension installation"
    )
    
    return success

def azure_login():
    """Login to Azure CLI."""
    print_step(3, "Azure CLI Authentication")
    
    # Check if already logged in
    result = subprocess.run("az account show", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Already logged into Azure CLI")
        print("Current account:")
        print(result.stdout)
        
        choice = input("Do you want to login with a different account? (y/n): ").lower().strip()
        if choice != 'y':
            return True
    
    print("Starting Azure CLI login...")
    print("A browser window will open for authentication.")
    
    success = run_command("az login", "Azure CLI login")
    return success

def azure_devops_login():
    """Login to Azure DevOps with proper scope."""
    print_step(4, "Azure DevOps Scope Configuration")
    
    print("Configuring Azure CLI for Azure DevOps access...")
    print("This may open a browser window for additional authentication.")
    
    # Try the DevOps-specific login
    success = run_command(
        "az login --scope https://dev.azure.com//.default",
        "Azure DevOps scope configuration",
        required=False
    )
    
    if not success:
        print("⚠️ DevOps scope configuration failed.")
        print("This is normal - continuing with standard authentication.")
    
    return True

def configure_defaults():
    """Configure Azure DevOps defaults."""
    print_step(5, "Configuring Azure DevOps Defaults")
    
    success = run_command(
        "az devops configure --defaults organization=https://dev.azure.com/msazure",
        "Setting default organization to msazure"
    )
    
    return success

def test_authentication():
    """Test the authentication setup."""
    print_step(6, "Testing Authentication")
    
    print("Testing Azure DevOps access...")
    success = run_command(
        "az devops project list --organization https://dev.azure.com/msazure --query \"value[?name=='Antares'].{name:name}\" --output table",
        "Azure DevOps project access test",
        required=False
    )
    
    if success:
        print("✅ Azure DevOps authentication is working!")
    else:
        print("⚠️ Azure DevOps access test failed.")
        print("You may need to request access to the msazure organization.")
    
    return success

def test_mcp_authentication():
    """Test MCP server authentication."""
    print_step(7, "Testing MCP Server Authentication")
    
    try:
        # Import and test our authentication functions
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from server import check_authentication_methods
        
        print("Testing MCP server authentication methods...")
        result = check_authentication_methods()
        
        print(f"PAT Token: {'✅' if result['pat_token']['valid'] else '❌'}")
        print(f"Azure CLI: {'✅' if result['azure_cli']['valid'] else '❌'}")
        print(f"Preferred method: {result.get('preferred_method', 'None')}")
        
        if result.get('preferred_method'):
            print("✅ MCP server authentication is working!")
            return True
        else:
            print("⚠️ No valid authentication method found for MCP server.")
            print("Recommendations:")
            for rec in result.get('recommendations', []):
                print(f"  - {rec}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing MCP authentication: {e}")
        return False

def main():
    """Main setup function."""
    print_header("Azure DevOps MCP Server Setup")
    print("This script will help you configure authentication for the AdoMcp tool.")
    print("Please follow the steps below:")
    
    # Step 1: Check Azure CLI
    if not check_azure_cli():
        return False
    
    # Step 2: Install DevOps extension
    if not install_devops_extension():
        return False
    
    # Step 3: Azure login
    if not azure_login():
        return False
    
    # Step 4: DevOps scope login
    azure_devops_login()
    
    # Step 5: Configure defaults
    configure_defaults()
    
    # Step 6: Test Azure DevOps access
    test_authentication()
    
    # Step 7: Test MCP server authentication
    mcp_working = test_mcp_authentication()
    
    # Final summary
    print_header("Setup Complete")
    
    if mcp_working:
        print("🎉 Setup completed successfully!")
        print("Your MCP server is ready to use with Azure DevOps.")
        print()
        print("Next steps:")
        print("1. Start the MCP server: python server.py")
        print("2. Use GitHub Copilot to trigger pipelines:")
        print("   - 'Trigger 3 runs of the integration test pipeline'")
        print("   - 'List the most recent 5 runs of the integration test pipeline'")
    else:
        print("⚠️ Setup completed with some issues.")
        print("The MCP server may still work, but some features might be limited.")
        print()
        print("To generate a PAT token manually:")
        print("1. Visit: https://dev.azure.com/_usersSettings/tokens")
        print("2. Create a token with 'Build: Read & execute' permissions")
        print("3. Set environment variable: setx AZURE_DEVOPS_EXT_PAT \"<your_token>\"")
        print("4. Restart your terminal and test again")

if __name__ == "__main__":
    main()
