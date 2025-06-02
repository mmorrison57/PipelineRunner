#!/usr/bin/env python3
"""
Simple Azure DevOps MCP Server - Fast and Direct
No complex auth checking, just tries to run commands directly.
"""

import os
import yaml
import json
import datetime
import logging
import subprocess
import re
from typing import Optional, Dict, List, Any
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")

# Simple config loader
def load_pipelines() -> Dict[str, Dict[str, Any]]:
    """Load pipelines from config.yaml"""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return {p["name"]: p for p in data.get("pipelines", [])}
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}

# Simple pipeline finder using regex
def find_pipeline(query: str, pipelines: Dict[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Find pipeline using simple string matching"""
    query_lower = query.lower().strip()
    
    # Try exact match first
    for name, config in pipelines.items():
        if name.lower() == query_lower:
            return config
    
    # Try partial match
    for name, config in pipelines.items():
        if query_lower in name.lower():
            return config
    
    # Try regex pattern matching for common abbreviations
    patterns = [
        (r'^int', 'integration'),  # "int" -> "integration"
        (r'^deploy', 'deploy'),
        (r'^test', 'test'),
        (r'^build', 'build')
    ]
    
    for pattern, replacement in patterns:
        if re.match(pattern, query_lower):
            for name, config in pipelines.items():
                if replacement in name.lower():
                    return config
    
    return None

# Simple Azure CLI runner
def run_az_direct(command: List[str]) -> Dict[str, Any]:
    """Run Azure CLI command directly, try auth if it fails"""
    
    # Try common az.cmd path first
    az_path = r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
    if not os.path.exists(az_path):
        az_path = "az"  # Try PATH
    
    if command[0] == "az":
        command[0] = az_path
    
    try:
        logger.info(f"Running: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True, timeout=30, check=False)
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout) if result.stdout.strip() else {}
                return {"success": True, "data": data}
            except json.JSONDecodeError:
                return {"success": True, "data": {"output": result.stdout}}
        else:
            error = result.stderr.strip() or result.stdout.strip()
            
            # If auth error, suggest login
            if any(keyword in error.lower() for keyword in ['login', 'authenticate', 'credential', 'unauthorized']):
                return {
                    "success": False,
                    "error": error,
                    "suggestion": "Run 'az login' and 'az extension add --name azure-devops' if needed"
                }
            
            return {"success": False, "error": error}
            
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Initialize MCP server
mcp = FastMCP(name="ado-simple", version="1.0.0", dependencies=["PyYAML"])

@mcp.tool(
    name="bb7_trigger_bulk",
    description="Trigger pipeline multiple times. Use pipeline name or abbreviation (e.g. 'int' for integration)."
)
def bb7_trigger_bulk(name: str, count: int, branch: Optional[str] = None) -> List[Dict[str, Any]]:
    """Trigger pipeline runs directly"""
    
    # Load pipelines
    pipelines = load_pipelines()
    if not pipelines:
        return [{"error": "No pipelines configured"}]
    
    # Find pipeline
    pipeline = find_pipeline(name, pipelines)
    if not pipeline:
        available = get_pipeline_names()
        return [{
            "error": f"Pipeline '{name}' not found",
            "available": available
        }]
    
    # Determine branch
    target_branch = branch or pipeline.get("branch", "main")
    
    results = []
    for i in range(count):
        command = [
            "az", "pipelines", "run",
            "--organization", f"https://dev.azure.com/{pipeline['organization']}",
            "--project", pipeline["project"],
            "--id", str(pipeline["pipelineID"]),
            "--branch", target_branch,
            "--output", "json"
        ]
        
        result = run_az_direct(command)
        
        if result["success"]:
            run_data = result["data"]
            results.append({
                "success": True,
                "run_number": i + 1,
                "pipeline_name": name,
                "branch": target_branch,
                "run_id": run_data.get("id"),
                "url": run_data.get("url")
            })
        else:
            results.append({
                "success": False,
                "run_number": i + 1,
                "error": result["error"],
                "suggestion": result.get("suggestion")
            })
            
            # Stop on auth errors
            if result.get("suggestion"):
                break
    
    return results

@mcp.tool(
    name="bb7_list_runs",
    description="List recent pipeline runs"
)
def bb7_list_runs(name: str, top: int = 10) -> Dict[str, Any]:
    """List pipeline runs"""
    
    pipelines = load_pipelines()
    pipeline = find_pipeline(name, pipelines)
    
    if not pipeline:
        return {"error": f"Pipeline '{name}' not found", "available": get_pipeline_names()}
    
    command = [
        "az", "pipelines", "runs", "list",
        "--organization", f"https://dev.azure.com/{pipeline['organization']}",
        "--project", pipeline["project"],
        "--pipeline-ids", str(pipeline["pipelineID"]),
        "--top", str(top),
        "--output", "json"
    ]
    
    result = run_az_direct(command)
    
    if result["success"]:
        return {
            "success": True,
            "pipeline": name,
            "runs": result["data"],
            "count": len(result["data"]) if isinstance(result["data"], list) else 0
        }
    else:
        return {
            "success": False,
            "error": result["error"],
            "suggestion": result.get("suggestion")
        }

# Simple function to list available pipelines
def list_pipelines_simple() -> None:
    """Print all configured pipelines in a simple format"""
    pipelines = load_pipelines()
    
    if not pipelines:
        print("No pipelines configured")
        return
    
    print(f"Available pipelines ({len(pipelines)} total):")
    print("-" * 50)
    
    for name, config in pipelines.items():
        print(f"Name: {name}")
        print(f"  Organization: {config.get('organization', 'N/A')}")
        print(f"  Project: {config.get('project', 'N/A')}")
        print(f"  Pipeline ID: {config.get('pipelineID', 'N/A')}")
        print(f"  Branch: {config.get('branch', 'N/A')}")
        print()

def get_pipeline_names() -> List[str]:
    """Get a simple list of pipeline names"""
    pipelines = load_pipelines()
    return list(pipelines.keys())

if __name__ == "__main__":
    # For testing, you can call the simple functions directly
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        list_pipelines_simple()
    else:
        mcp.run()
