import os
import base64
import yaml
import requests
import json
import datetime
from mcp.server.fastmcp import FastMCP

# Load pipeline metadata from config.yaml
# Note: use raw string for Windows paths
def load_config(path=r"Q:\wagit\AI\AdoMcp\config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {p["name"]: p for p in data.get("pipelines", [])}

pipelines = load_config()

# Initialize FastMCP server
dep = ["requests", "PyYAML"]
mcp = FastMCP(
    name="ado-pipelines",
    version="0.1.0",
    dependencies=dep,
)

@mcp.tool()
def list_runs(name: str, top: int) -> dict:
    """List recent Azure DevOps pipeline runs."""
    p = pipelines.get(name)
    if not p:
        raise ValueError(f"Pipeline '{name}' not found in config.yaml")

    pat = os.getenv("AZURE_DEVOPS_PAT") or os.getenv("AZURE_DEVOPS_EXT_PAT")
    if not pat:
        raise ValueError("Environment variable AZURE_DEVOPS_PAT is not set")

    # Construct Basic auth header
    token = base64.b64encode(f":{pat}".encode()).decode()
    headers = {"Authorization": f"Basic {token}"}

    # Call the ADO List Runs API (no $top param supported)
    url = (
        f"https://dev.azure.com/{p['organization']}/{p['project']}"
        f"/_apis/pipelines/{p['pipelineID']}/runs?api-version=7.1"
    )
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    response_json = resp.json()

    # Locally limit to `top` runs
    response_json["value"] = response_json.get("value", [])[:top]

    # Write a timestamped copy for debugging
    os.makedirs("responses", exist_ok=True)
    filename = os.path.join(
        "responses",
        f"list_runs_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(response_json, f, indent=2)
    return response_json

@mcp.tool()
def trigger_bulk(name: str, count: int) -> list:
    """Trigger the Azure DevOps pipeline `count` times in bulk."""
    p = pipelines.get(name)
    if not p:
        raise ValueError(f"Pipeline '{name}' not found in config.yaml")

    pat = os.getenv("AZURE_DEVOPS_PAT") or os.getenv("AZURE_DEVOPS_EXT_PAT")
    if not pat:
        raise ValueError("Environment variable AZURE_DEVOPS_PAT is not set")

    token = base64.b64encode(f":{pat}".encode()).decode()
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }

    url = (
        f"https://dev.azure.com/{p['organization']}/{p['project']}"
        f"/_apis/pipelines/{p['pipelineID']}/runs?api-version=7.1"
    )
    results = []
    for _ in range(count):
        resp = requests.post(url, headers=headers, timeout=10)
        resp.raise_for_status()
        results.append(resp.json())

    os.makedirs("responses", exist_ok=True)
    filename = os.path.join(
        "responses",
        f"trigger_bulk_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    return results

if __name__ == "__main__":
    # Run the MCP server over stdio
    mcp.run()
