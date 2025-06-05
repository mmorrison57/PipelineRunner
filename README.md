# AdoMcp Tool

## Overview
The AdoMcp tool is a Model Context Protocol (MCP) server that interacts with Azure DevOps pipelines using the Azure CLI. It provides functionality to trigger and monitor pipeline runs through natural language commands in GitHub Copilot, eliminating the need for manual pipeline management through the Azure DevOps web interface.

## Current Capabilities

1. **Trigger Pipeline Runs**
   - Initiate pipeline runs for configured pipelines using Azure CLI commands
   - Support for bulk pipeline runs (e.g., trigger 10 runs at once)
   - Pass custom variables and parameters to pipeline runs
   - No more manual clicking in the Azure DevOps UI!

2. **Monitor Pipeline Runs**
   - List recent pipeline runs with status and results
   - Access detailed build information and logs
   - Monitor pipeline execution progress

## Configuration
The tool uses a `config.yaml` file to define the pipelines it interacts with. Each pipeline entry includes:
- `name`: The name of the pipeline. This can be any user-defined string for identification purposes. Make the names distinct enought that copilot recognizes which pipeline is the correct one.
- `organization`: The Azure DevOps organization.
- `project`: The Azure DevOps project.
- `pipelineID`: The unique ID of the pipeline.
- `branch`: The branch associated with the pipeline.

Example configuration:
```yaml
pipelines:
  - name: "(Dev) CI-Linux-Integration"
    organization: "msazure"
    project: "Antares"
    pipelineID: 331421
    branch: "user/mm/104-prev-state"
  - name: "mmorrison1 stampy"
    organization: "msazure"
    project: "Antares"
    pipelineID: 390216
    branch: "dev"
```

## Requirements
- Python 3.9 or later
- Azure CLI installed and configured
- Azure DevOps CLI extension (`azure-devops`)
- Azure DevOps access permissions for the configured pipelines
- Active Azure CLI authentication session

## Authentication Setup

The AdoMcp tool uses Azure CLI for authentication, which provides secure, automatic token management without requiring manual PAT token handling.

### Prerequisites

1. **Install Azure CLI**
   ```bash
   # Download and install from: https://aka.ms/installazurecliwindows
   # Or use package managers like winget, chocolatey, etc.
   ```

2. **Install Azure DevOps Extension**
   ```bash
   az extension add --name azure-devops
   ```

3. **Login to Azure CLI**
   ```bash
   # Standard Azure login
   az login
   
   # Login with DevOps scope (recommended for better API access)
   az login --scope https://dev.azure.com//.default
   ```

4. **Set Default Organization (Optional)**
   ```bash
   az devops configure --defaults organization=https://dev.azure.com/msazure
   ```

### Authentication Verification

The MCP server provides tools to verify your authentication status:
- `check_azure_cli_status` - Verify Azure CLI login and DevOps extension
- `test_pipeline_access` - Test access to configured pipelines
- `list_available_pipelines` - Show all configured pipelines

## Benefits of CLI-Based Approach

- **Secure Authentication**: Uses Azure CLI's secure authentication flow
- **No Token Management**: Eliminates PAT token creation, storage, and rotation
- **Better Error Handling**: Azure CLI provides clear, actionable error messages
- **Simplified Setup**: No manual token configuration required
- **Automatic Renewal**: Azure CLI handles token refresh automatically

## Usage
1. Configure the `config.yaml` file with the desired pipelines.
2. Ensure Azure CLI is installed and you're logged in.
3. Start the MCP server and use natural language commands through GitHub Copilot.

## Steps to Start MCP Server
1. Open the project folder in Visual Studio Code (VSCode).
2. Ensure Python 3.9 or later is installed and Azure CLI is configured.
3. Verify authentication: Run `az account show` to confirm you're logged in.
4. Open VSCode command palette and type "MCP" - select "Add Server".
5. Start the MCP server:
   ```bash
   python server.py
   ```
6. Use GitHub Copilot chat in agent mode.

## Example Usage
* `Trigger 3 runs of the integration test pipeline` 
* `List the most recent 5 runs of the integration test pipeline`
* `Kick off my stampy pipeline`

## Troubleshooting

### Common Issues

1. **Azure CLI not found**
   - Install Azure CLI from https://aka.ms/installazurecliwindows
   - Restart your terminal/VSCode after installation

2. **DevOps extension missing**
   ```bash
   az extension add --name azure-devops
   ```

3. **Authentication expired**
   ```bash
   az login --scope https://dev.azure.com//.default
   ```

4. **Pipeline access denied**
   - Verify you have permissions to the Azure DevOps project
   - Check that the pipeline IDs in `config.yaml` are correct

## Architecture Notes

This tool has been completely rewritten to use Azure CLI instead of direct HTTP API calls with PAT tokens. The benefits include:

- **Simplified Authentication**: No more PAT token management
- **Better Security**: Leverages Azure CLI's secure authentication flow  
- **Improved Reliability**: Azure CLI handles token refresh and error scenarios
- **Cleaner Code**: Eliminated complex HTTP request handling and token management logic


## Development Notes

* Built using GitHub Copilot in Agent mode for rapid prototyping and development
* Demonstrates automation of repetitive Azure DevOps tasks through natural language
* Showcases the power of MCP (Model Context Protocol) for creating AI-accessible tools
* Originally used HTTP API calls with PAT tokens, now completely rewritten to use Azure CLI for better security and maintainability

## Future Possibilities

This tool demonstrates how we can build natural language interfaces for complex DevOps tasks. Potential extensions:

- Integration with AntaresCMD commands (e.g., "spin up a site with dynamic cache and HTTP logging")
- Automated deployment workflows triggered by natural language
- Infrastructure management through conversational AI
- Integration with monitoring and alerting systems

The goal is to reduce manual clicking and provide intuitive automation through AI-powered tools!