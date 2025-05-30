#!/usr/bin/env python3
"""
Test script to trigger the integration pipeline with a specific branch.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import run_az_command, check_azure_cli_auth, pipelines, dump_response

def trigger_integration_with_branch(branch_name: str):
    """Trigger the integration pipeline with a specific branch."""
    
    print(f"🚀 Testing integration pipeline trigger with branch: {branch_name}")
    
    # Get pipeline config
    pipeline_name = "integration"
    p = pipelines.get(pipeline_name)
    if not p:
        print(f"❌ Pipeline '{pipeline_name}' not found in config")
        return False
    
    print(f"📋 Pipeline Config:")
    print(f"  - Name: {pipeline_name}")
    print(f"  - Organization: {p['organization']}")
    print(f"  - Project: {p['project']}")
    print(f"  - Pipeline ID: {p['pipelineID']}")
    print(f"  - Configured Branch: {p['branch']}")
    print(f"  - Override Branch: {branch_name}")
    
    # Check Azure CLI authentication
    print(f"\n🔐 Checking Azure CLI authentication...")
    auth_check = check_azure_cli_auth()
    if not auth_check["authenticated"]:
        print(f"❌ Authentication failed: {auth_check}")
        return False
    
    print(f"✅ Authenticated successfully")
    
    # Build Azure CLI command with branch override
    command = [
        "az", "pipelines", "run",
        "--organization", f"https://dev.azure.com/{p['organization']}",
        "--project", p["project"],
        "--id", str(p["pipelineID"]),
        "--branch", branch_name,  # Use the specified branch instead of config
        "--output", "json"
    ]
    
    print(f"\n🔨 Running Azure CLI command:")
    print(f"  {' '.join(command)}")
    
    # Run the command
    result = run_az_command(command)
    
    if result["success"]:
        run_data = result["data"]
        print(f"\n✅ Pipeline triggered successfully!")
        print(f"  - Run ID: {run_data.get('id')}")
        print(f"  - Run Name: {run_data.get('name')}")
        print(f"  - State: {run_data.get('state')}")
        print(f"  - Created: {run_data.get('createdDate')}")
        print(f"  - URL: {run_data.get('url')}")
        
        web_url = run_data.get("_links", {}).get("web", {}).get("href")
        if web_url:
            print(f"  - Web URL: {web_url}")
        
        # Dump response for debugging
        dump_response("trigger_integration_test", result["data"])
        
        return True
    else:
        print(f"\n❌ Pipeline trigger failed:")
        print(f"  Error: {result['error']}")
        if "exit_code" in result:
            print(f"  Exit Code: {result['exit_code']}")
        return False

if __name__ == "__main__":
    branch = sys.argv[1] if len(sys.argv) > 1 else "dev"
    success = trigger_integration_with_branch(branch)
    sys.exit(0 if success else 1)
