# Neo4j Graph Knowledge Integration with LLMs

This document provides instructions on how to integrate Neo4j graph knowledge with Large Language Models (LLMs) using the Model Context Protocol (MCP).

## Overview

The Neo4j MCP integration allows LLMs to:

1. Query and understand project structures stored in Neo4j
2. Maintain context across different conversations
3. Track changes to projects over time
4. Work with multiple projects in the same Neo4j instance

## Setup

### Prerequisites

- Neo4j database (local or remote)
- Python 3.8+
- MCP-compatible LLM client (Claude, ChatGPT, etc.)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/neo4j-contrib/mcp-neo4j.git
   cd mcp-neo4j
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Configure Neo4j connection:
   ```bash
   # Edit config.py with your Neo4j credentials
   ```

4. Start the MCP server:
   ```bash
   python -m custom_neo4j_mcp.main
   ```

## Project Configuration

Each project should have a configuration file (`project_config.json`) with the following structure:

```json
{
  "project_name": "your-project-name",
  "neo4j_uri": "neo4j://localhost:7687",
  "neo4j_auth": ["neo4j", "password"],
  "description": "Project description",
  "repository": "https://github.com/your/repository",
  "created_at": "2025-04-17T21:20:00Z",
  "tags": ["tag1", "tag2"]
}
```

## Graph Structure

The graph representation follows this structure:

1. **Project Node**: Top-level node representing the project
2. **Component Nodes**: High-level architectural components
3. **Module Nodes**: Code modules implementing components
4. **File Nodes**: Source code files
5. **Function/Struct Nodes**: Functions and data structures
6. **Documentation Nodes**: Documentation files
7. **ChangeLog Nodes**: Records of changes made to the project

All nodes (except Project) have:
- A `project` property with the project name
- A `ProjectNode` label for easy filtering

## Creating and Updating the Graph

Use the `GraphUpdater` class to create and update the graph:

```python
from custom_neo4j_mcp.utils.graph_updater import GraphUpdater, load_project_config

# Load project configuration
config = load_project_config("project_config.json")

# Create updater with project information
updater = GraphUpdater(
    uri=config.get("neo4j_uri"),
    auth=tuple(config.get("neo4j_auth")),
    project_name=config.get("project_name")
)

# Initialize project in Neo4j
updater.initialize_project()

# Add components, files, functions, etc.
updater.create_component("ComponentName", "Component description")
updater.create_file("path/to/file.py", "File description")
updater.add_function(
    name="function_name",
    file_path="path/to/file.py",
    description="Function description",
    component_name="ComponentName"
)

# Log changes
updater.add_change_log(
    description="Added new component",
    change_type="FEATURE",
    author="developer",
    affected_components=["ComponentName"],
    modified_files=["path/to/file.py"],
    added_functions=["function_name"]
)
```

## Working with Multiple Projects

To work with multiple projects in the same Neo4j instance:

1. Create a configuration file for each project
2. Initialize each project with a unique name
3. When querying the graph, always filter by project name

Example:

```python
# Initialize first project
updater1 = GraphUpdater(project_name="project1")
updater1.initialize_project()

# Initialize second project
updater2 = GraphUpdater(project_name="project2")
updater2.initialize_project()

# Switch between projects as needed
```

## LLM Integration

### MCP Server Configuration

1. Add the Neo4j MCP server to your MCP client configuration:

```json
{
  "servers": [
    {
      "name": "github.com/neo4j-contrib/mcp-neo4j",
      "command": "python -m custom_neo4j_mcp.main"
    }
  ]
}
```

2. Provide LLMs with the `neo4j_graph_instructions.md` file to guide their interactions with the graph.

### Example Queries

LLMs can use the following Cypher queries to understand the project:

```cypher
// Get project information
MATCH (p:Project {name: $project_name})
RETURN p.name, p.description, p.created_at

// Get components
MATCH (c:Component:ProjectNode {project: $project_name})
RETURN c.name, c.description

// Get component relationships
MATCH (c1:Component:ProjectNode {project: $project_name})-[r:INTERACTS_WITH]->(c2:Component:ProjectNode {project: $project_name})
RETURN c1.name, c2.name, r.type

// Trace function calls
MATCH (f:Function:ProjectNode {name: $function_name, project: $project_name})
MATCH path = (f)-[:CALLS*1..3]->(other:Function:ProjectNode {project: $project_name})
RETURN [node in nodes(path) | node.name] as call_chain
```

## Best Practices

1. **Initialize Projects**: Always initialize projects before adding nodes
2. **Tag Existing Nodes**: Use `tag_nodes_with_project()` to tag existing nodes with project information
3. **Use Project Filtering**: Always filter queries by project name
4. **Log Changes**: Record all significant changes to the project
5. **Update Documentation**: Keep documentation nodes up to date

## Troubleshooting

- **Connection Issues**: Verify Neo4j credentials and database status
- **Missing Nodes**: Check that nodes have the correct project property and ProjectNode label
- **Query Performance**: Add indexes for frequently queried properties:
  ```cypher
  CREATE INDEX ON :ProjectNode(project)
  CREATE INDEX ON :Component(name, project)
  CREATE INDEX ON :Function(name, project)
  ```

## Example Scripts

See the `examples` directory for sample scripts:

- `create_graph.py`: Example script for creating a graph representation of a project
- `query_graph.py`: Example script for querying the graph
- `update_graph.py`: Example script for updating the graph after code changes

## Resources

- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/current/)
- [Model Context Protocol](https://modelcontextprotocol.io/introduction)
- [Neo4j MCP GitHub Repository](https://github.com/neo4j-contrib/mcp-neo4j)
