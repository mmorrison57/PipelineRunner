import os
import base64
import yaml
import requests
import json
import datetime
from fastmcp import FastMCP  # MCP server SDK

# Load pipeline metadata from config.yaml
def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {p["name"]: p for p in data.get("pipelines", [])}

# Update CONFIG_PATH as needed
CONFIG_PATH = r"Q:\wagit\AI\AdoMcp\config.yaml"
pipelines = load_config(CONFIG_PATH)

# Initialize FastMCP server
dependencies = ["requests", "PyYAML"]
mcp = FastMCP(
    name="ado-pipelines",
    version="0.1.1",  # bump version to refresh manifest
    dependencies=dependencies,
)

# Helper to dump responses
def dump_response(prefix: str, data):
    os.makedirs("responses", exist_ok=True)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{prefix}_{timestamp}.json"
    path = os.path.join("responses", filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return path

@mcp.tool(
    name="list_runs",
    description="List recent Azure DevOps pipeline runs (local limit to 'top')."
)
def list_runs(name: str, top: int) -> dict:
    p = pipelines.get(name)
    if not p:
        raise ValueError(f"Pipeline '{name}' not in config.yaml")

    pat = os.getenv("AZURE_DEVOPS_PAT") or os.getenv("AZURE_DEVOPS_EXT_PAT")
    if not pat:
        raise ValueError("AZURE_DEVOPS_PAT env var not set")

    token = base64.b64encode(f":{pat}".encode()).decode()
    headers = {"Authorization": f"Basic {token}"}

    # Call ADO List Runs (no server-side $top)
    url = (
        f"https://dev.azure.com/{p['organization']}/{p['project']}"
        f"/_apis/pipelines/{p['pipelineID']}/runs?api-version=7.1"
    )
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    # Apply local limit
    data["value"] = data.get("value", [])[:top]

    # Dump to responses folder
    dump_path = dump_response("list_runs", data)
    # You can log or return the dump_path if desired
    return data

@mcp.tool(
    name="trigger_bulk",
    description="Trigger the configured pipeline 'count' times on its branch."
)
def trigger_bulk(name: str, count: int) -> list:
    p = pipelines.get(name)
    if not p:
        raise ValueError(f"Pipeline '{name}' not in config.yaml")
    branch = p.get("branch")
    if not branch:
        raise ValueError(f"Pipeline '{name}' missing 'branch' in config.yaml")

    pat = os.getenv("AZURE_DEVOPS_PAT") or os.getenv("AZURE_DEVOPS_EXT_PAT")
    if not pat:
        raise ValueError("AZURE_DEVOPS_PAT env var not set")

    token = base64.b64encode(f":{pat}".encode()).decode()
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }

    url = (
        f"https://dev.azure.com/{p['organization']}/{p['project']}"
        f"/_apis/pipelines/{p['pipelineID']}/runs?api-version=7.1"
    )
    body = {"resources": {"repositories": {"self": {"refName": branch}}}}

    results = []
    for _ in range(count):
        resp = requests.post(url, headers=headers, json=body, timeout=10)
        resp.raise_for_status()
        results.append(resp.json())

    # Dump bulk trigger responses
    dump_path = dump_response("trigger_bulk", results)
    return results

if __name__ == "__main__":
    # Run the MCP server over stdio
    mcp.run()
