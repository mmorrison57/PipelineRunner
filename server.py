#!/usr/bin/env python3
"""
Simplified Azure DevOps MCP Server - Performance Optimized
Focuses only on pipeline name matching and execution using config.yaml data.
Removed git repository checking to improve MCP server performance.
"""

import os
import yaml
import json
import datetime
import logging
import subprocess
import uuid
from pathlib import Path
from typing import Optional, Dict, List, Any
from fastmcp import FastMCP  # MCP server SDK

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Base directory for all file operations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load pipeline metadata from config.yaml
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")

def load_config(path: str) -> Dict[str, Dict[str, Any]]:
    """Load pipeline configuration from YAML file."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    pipelines = {p["name"]: p for p in data.get("pipelines", [])}
    
    return pipelines

# Initialize FastMCP server
dependencies = ["PyYAML"]
mcp = FastMCP(
    name="ado-pipelines-cli",
    version="0.3.0",  # New version for simplified, performance-optimized implementation
    dependencies=dependencies,
)

# Helper to dump responses into cwd/responses
def dump_response(prefix: str, data: Any) -> str:
    """Dump response data to responses directory."""
    logging.info(f"Dumping response with prefix: {prefix}")
    responses_dir = os.path.join(BASE_DIR, "responses")
    os.makedirs(responses_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{prefix}_{timestamp}.json"
    path = os.path.join(responses_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    logging.info(f"Response dumped to: {path}")
    return path

def find_azure_cli_path() -> Optional[str]:
    """Find the Azure CLI executable path with optimized search."""
    # Try the most common Windows path first (fastest)
    primary_path = r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
    
    try:
        result = subprocess.run(
            [primary_path, "--version"],
            capture_output=True,
            text=True,
            timeout=5,  # Quick timeout for path testing
            check=False
        )
        if result.returncode == 0:
            logger.info(f"Found Azure CLI at: {primary_path}")
            return primary_path
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    
    # Fall back to other paths only if primary fails
    fallback_paths = [
        r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
        "az.cmd",  # If in PATH
        "az"       # Linux/Mac style
    ]
    
    for path in fallback_paths:
        try:
            result = subprocess.run(
                [path, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False
            )
            if result.returncode == 0:
                logger.info(f"Found Azure CLI at: {path}")
                return path
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            continue
    
    logger.error("Azure CLI not found in any common locations")
    return None

# Cache the Azure CLI path and auth status
_azure_cli_path = None
_auth_status_cache = None
_auth_cache_time = None
AUTH_CACHE_DURATION = 300  # 5 minutes

def run_az_command(command: List[str]) -> Dict[str, Any]:
    """
    Run an Azure CLI command and return the result.
    
    Args:
        command: List of command parts (e.g., ['az', 'pipelines', 'run', '--name', 'test'])
        
    Returns:
        Dictionary with 'success', 'data', and optionally 'error' fields
    """
    global _azure_cli_path
    
    try:
        # Find Azure CLI path if not cached
        if _azure_cli_path is None:
            _azure_cli_path = find_azure_cli_path()
            if _azure_cli_path is None:
                return {
                    "success": False,
                    "error": "Azure CLI not found. Please install Azure CLI from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
                }
        
        # Replace 'az' with the full path
        if command[0] == "az":
            command[0] = _azure_cli_path
        
        # Print to console for visibility in GitHub chat
        print(f"🔄 Executing Azure CLI command: {' '.join(command)}")
        logger.info(f"Running Azure CLI command: {' '.join(command)}")
        
        # Run the command with shorter timeout for better responsiveness
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,  # Reduced from 60 to 30 seconds
            check=False  # Don't raise exception on non-zero exit
        )
        
        if result.returncode == 0:
            # Success - parse JSON output
            try:
                data = json.loads(result.stdout) if result.stdout.strip() else {}
                return {"success": True, "data": data}
            except json.JSONDecodeError:
                # If not JSON, return raw output
                return {"success": True, "data": {"output": result.stdout}}
        else:
            # Error
            error_msg = result.stderr.strip() or result.stdout.strip()
            logger.error(f"Azure CLI command failed: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "exit_code": result.returncode
            }
            
    except subprocess.TimeoutExpired:
        logger.error("Azure CLI command timed out")
        return {"success": False, "error": "Command timed out after 30 seconds"}
    except Exception as e:
        logger.error(f"Error running Azure CLI command: {e}")
        return {"success": False, "error": str(e)}

def check_azure_cli_auth() -> Dict[str, Any]:
    """Check if Azure CLI is authenticated and can access Azure DevOps. Uses caching to improve performance."""
    global _auth_status_cache, _auth_cache_time
    
    # Check if we have a valid cached result
    current_time = datetime.datetime.now().timestamp()
    if (_auth_status_cache is not None and 
        _auth_cache_time is not None and 
        current_time - _auth_cache_time < AUTH_CACHE_DURATION):
        logger.info("Using cached authentication status")
        return _auth_status_cache
    
    logger.info("Checking Azure CLI authentication (not cached)")
    
    # Check if az command is available
    result = run_az_command(["az", "--version"])
    if not result["success"]:
        auth_result = {
            "authenticated": False,
            "error": "Azure CLI not found. Please install Azure CLI first.",
            "install_instructions": "Visit https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        }
        _auth_status_cache = auth_result
        _auth_cache_time = current_time
        return auth_result
    
    # Check if logged in
    result = run_az_command(["az", "account", "show"])
    if not result["success"]:
        auth_result = {
            "authenticated": False,
            "error": "Not logged into Azure CLI. Please run 'az login' first.",
            "suggestion": "Run 'az login' to authenticate with Azure"
        }
        _auth_status_cache = auth_result
        _auth_cache_time = current_time
        return auth_result
    
    # Check if Azure DevOps extension is available
    result = run_az_command(["az", "extension", "show", "--name", "azure-devops"])
    if not result["success"]:
        auth_result = {
            "authenticated": False,
            "error": "Azure DevOps extension not installed.",
            "suggestion": "Run 'az extension add --name azure-devops' to install the extension"
        }
        _auth_status_cache = auth_result
        _auth_cache_time = current_time
        return auth_result
    
    # All checks passed - cache the positive result
    auth_result = {"authenticated": True, "account": result["data"]}
    _auth_status_cache = auth_result
    _auth_cache_time = current_time
    
    return auth_result

# Load pipeline configuration
pipelines = load_config(CONFIG_PATH)

@mcp.tool(
    name="bb7_list_runs",
    description="List recent Azure DevOps pipeline runs (local limit to 'top')."
)
def bb7_list_runs(name: str, top: int) -> Dict[str, Any]:
    """
    List recent pipeline runs using Azure CLI.
    
    Args:
        name: Pipeline name from config.yaml
        top: Maximum number of runs to return
        
    Returns:
        Dictionary with pipeline run data or error information
    """
    # Check if pipeline exists in config
    p = pipelines.get(name)
    if not p:
        return {
            "error": f"Pipeline '{name}' not found in config.yaml",
            "available_pipelines": list(pipelines.keys())
        }
    
    # Check Azure CLI authentication
    auth_check = check_azure_cli_auth()
    if not auth_check["authenticated"]:
        return auth_check
    
    # Build Azure CLI command
    command = [
        "az", "pipelines", "runs", "list",
        "--organization", f"https://dev.azure.com/{p['organization']}",
        "--project", p["project"],
        "--pipeline-ids", str(p["pipelineID"]),
        "--top", str(top),
        "--output", "json"
    ]
    
    # Run the command
    result = run_az_command(command)
    
    if result["success"]:
        # Dump response for debugging
        dump_response("list_runs", result["data"])
        return {
            "success": True,
            "pipeline_name": name,
            "runs": result["data"],
            "count": len(result["data"]) if isinstance(result["data"], list) else 0
        }
    else:
        return {
            "error": f"Failed to list pipeline runs: {result['error']}",
            "pipeline_name": name,
            "suggestion": "Check if you have access to the specified Azure DevOps organization and project"
        }

@mcp.tool(
    name="bb7_trigger_bulk",
    description="Trigger the configured pipeline 'count' times using the branch specified in config.yaml. Optionally override with a different branch."
)
def bb7_trigger_bulk(name: str, count: int, branch: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Trigger multiple pipeline runs using Azure CLI.
    
    Args:
        name: Pipeline name from config.yaml
        count: Number of times to trigger the pipeline
        branch: Optional branch override (uses config branch if not specified)
        
    Returns:
        List of results for each trigger attempt
    """
    # Check if pipeline exists in config
    p = pipelines.get(name)
    if not p:
        return [{
            "error": f"Pipeline '{name}' not found in config.yaml",
            "available_pipelines": list(pipelines.keys())
        }]
    
    # Determine which branch to use
    target_branch = branch if branch else p.get("branch")
    
    if not target_branch:
        return [{
            "error": f"Pipeline '{name}' missing 'branch' in config.yaml and no branch specified",
            "pipeline_config": p
        }]
    
    # Check Azure CLI authentication
    auth_check = check_azure_cli_auth()
    if not auth_check["authenticated"]:
        return [auth_check]
    
    results = []
    
    for i in range(count):
        # Build Azure CLI command for each run
        command = [
            "az", "pipelines", "run",
            "--organization", f"https://dev.azure.com/{p['organization']}",
            "--project", p["project"],
            "--id", str(p["pipelineID"]),
            "--branch", target_branch,
            "--output", "json"
        ]
        
        # Add variables if specified in config
        if "variables" in p and p["variables"]:
            for var_name, var_value in p["variables"].items():
                command.extend(["--variables", f"{var_name}={var_value}"])
        
        # Run the command
        result = run_az_command(command)
        
        if result["success"]:
            run_data = result["data"]
            results.append({
                "success": True,
                "run_number": i + 1,
                "pipeline_name": name,
                "branch_used": target_branch,
                "run_id": run_data.get("id"),
                "run_name": run_data.get("name"),
                "state": run_data.get("state"),
                "created_date": run_data.get("createdDate"),
                "url": run_data.get("url"),
                "web_url": run_data.get("_links", {}).get("web", {}).get("href")
            })
        else:
            error_result = {
                "success": False,
                "run_number": i + 1,
                "pipeline_name": name,
                "error": result["error"]
            }
            results.append(error_result)
            
            # If authentication fails, stop trying
            if "authentication" in result["error"].lower() or "unauthorized" in result["error"].lower():
                logger.warning("Authentication error detected, stopping bulk trigger")
                break
    
    # Dump bulk trigger responses
    dump_response("trigger_bulk", results)
    
    return results

@mcp.tool(
    name="check_azure_cli_status",
    description="Check Azure CLI installation, authentication, and Azure DevOps access."
)
def check_azure_cli_status() -> Dict[str, Any]:
    """
    Check the status of Azure CLI and Azure DevOps access.
    
    Returns:
        Dictionary with status information and recommendations
    """
    status = {
        "azure_cli_installed": False,
        "authenticated": False,
        "devops_extension_installed": False,
        "account_info": None,
        "recommendations": []
    }
    
    # Check if Azure CLI is installed
    result = run_az_command(["az", "--version"])
    if result["success"]:
        status["azure_cli_installed"] = True
        status["recommendations"].append("✅ Azure CLI is installed")
    else:
        status["recommendations"].append("❌ Azure CLI not found - install from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        return status
    
    # Check authentication
    result = run_az_command(["az", "account", "show"])
    if result["success"]:
        status["authenticated"] = True
        status["account_info"] = result["data"]
        status["recommendations"].append(f"✅ Authenticated as {result['data'].get('user', {}).get('name', 'unknown')}")
    else:
        status["recommendations"].append("❌ Not authenticated - run 'az login' to authenticate")
        return status
    
    # Check Azure DevOps extension
    result = run_az_command(["az", "extension", "show", "--name", "azure-devops"])
    if result["success"]:
        status["devops_extension_installed"] = True
        status["recommendations"].append("✅ Azure DevOps extension is installed")
    else:
        status["recommendations"].append("❌ Azure DevOps extension not installed - run 'az extension add --name azure-devops'")
        return status
    
    # All checks passed
    status["overall_status"] = "ready"
    status["recommendations"].append("🎉 Azure CLI is ready for Azure DevOps pipeline operations!")
    
    return status

@mcp.tool(
    name="list_available_pipelines",
    description="List all pipelines configured in config.yaml"
)
def list_available_pipelines() -> Dict[str, Any]:
    """
    List all pipelines available in the configuration.
    
    Returns:
        Dictionary with pipeline information
    """
    if not pipelines:
        return {
            "error": "No pipelines found in config.yaml",
            "config_path": CONFIG_PATH
        }
    
    pipeline_list = []
    for name, config in pipelines.items():
        pipeline_list.append({
            "name": name,
            "organization": config.get("organization"),
            "project": config.get("project"),
            "pipeline_id": config.get("pipelineID"),
            "branch": config.get("branch"),
            "has_variables": bool(config.get("variables"))
        })
    
    return {
        "total_pipelines": len(pipeline_list),
        "pipelines": pipeline_list,
        "config_path": CONFIG_PATH
    }

@mcp.tool(
    name="test_pipeline_access",
    description="Test access to a specific pipeline using Azure CLI"
)
def test_pipeline_access(name: str) -> Dict[str, Any]:
    """
    Test if we can access and get information about a specific pipeline.
    
    Args:
        name: Pipeline name from config.yaml
        
    Returns:
        Dictionary with test results
    """
    # Check if pipeline exists in config
    p = pipelines.get(name)
    if not p:
        return {
            "error": f"Pipeline '{name}' not found in config.yaml",
            "available_pipelines": list(pipelines.keys())
        }
    
    # Check Azure CLI authentication
    auth_check = check_azure_cli_auth()
    if not auth_check["authenticated"]:
        return auth_check
    
    # Try to get pipeline information
    command = [
        "az", "pipelines", "show",
        "--organization", f"https://dev.azure.com/{p['organization']}",
        "--project", p["project"],
        "--id", str(p["pipelineID"]),
        "--output", "json"
    ]
    
    result = run_az_command(command)
    
    if result["success"]:
        pipeline_info = result["data"]
        return {
            "success": True,
            "pipeline_name": name,
            "pipeline_info": {
                "id": pipeline_info.get("id"),
                "name": pipeline_info.get("name"),
                "path": pipeline_info.get("path"),
                "repository": pipeline_info.get("repository", {}).get("name"),
                "queue_status": pipeline_info.get("queueStatus"),
                "type": pipeline_info.get("type")
            },
            "access_test": "✅ Pipeline is accessible and information retrieved successfully"
        }
    else:
        return {
            "success": False,
            "pipeline_name": name,
            "error": result["error"],
            "access_test": "❌ Failed to access pipeline",
            "suggestion": "Check if the pipeline ID, organization, and project are correct, and you have permissions"
        }

@mcp.tool(
    name="clear_auth_cache",
    description="Clear the authentication cache to force re-checking Azure CLI status"
)
def clear_auth_cache() -> Dict[str, Any]:
    """Clear the authentication cache to force fresh auth checks."""
    global _auth_status_cache, _auth_cache_time
    
    _auth_status_cache = None
    _auth_cache_time = None
    
    return {
        "success": True,
        "message": "Authentication cache cleared. Next tool call will re-check Azure CLI status."
    }

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
