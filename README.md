# AdoMcp Tool

## Overview
The AdoMcp tool is designed to interact with Azure DevOps pipelines, providing functionality to trigger and monitor pipeline runs. It simplifies the process of managing pipelines by offering a streamlined interface for common tasks.

## Current Capabilities

1. **Trigger Pipeline Runs**
   - The tool allows users to initiate pipeline runs for configured pipelines. For example, the `Linux CI/CD` pipeline can be triggered directly from the tool in batches (so Amber Renton can kick off 10 runs at a time!! No more forever clicking :)).

2. **Monitor Pipeline Runs**
   - Users can monitor the status and results of pipeline runs, including accessing detailed build results through generated links.

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
- Azure DevOps access permissions for the configured pipelines
- ADO PAT Token with Pipeline resources: https://msazure.visualstudio.com/_usersSettings/tokens
     - Once you have a token, run `setx AZURE_DEVOPS_EXT_PAT "<your_pat_here>"` from cmd prompt 

## Usage
1. Configure the `config.yaml` file with the desired pipelines.
2. Use the tool to trigger or monitor pipeline runs.

## Steps to Start MCP Server
1. Open the project folder in Visual Studio Code (VSCode).
2. Ensure Python 3.9 or later is installed and set up in your environment.
3. Open VSCode command pallate and type "MCP" - select add server.
4. Run the following command to start the MCP server (may require using full python file path):
   ```bash
   python server.py
   ```
5. Use github copilot chat in agent mode.

## Example Usage
* `Trigger 3 runs of the integration test pipeline` 
* `List the most recent 5 runs of the integration test pipeline` (less useful)
* `Kick off my stampy`


## Random Note
* I built this using github copilot in Agent mode in under an hour. Agent mode is very useful for quick POCs and validation. This is my example of automating something that we spend time on which could be optimized. Just 1 example!
* Obviously this could also just be a script you run where you pass in some parameters to execute a pipeline. But the demonstration here is that with MCP we can build tools which we call from copilot / NLP. Another thought I had is this but with AntaresCMD commands. Imagine asking copilot to spin up a site with dynamic cache and http logging enabled - and let it run! Just one of many thoughts...