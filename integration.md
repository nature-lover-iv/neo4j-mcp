# Neo4j Graph Knowledge Integration with LLMs

This document provides comprehensive instructions on how to integrate Neo4j graph knowledge with Large Language Models (LLMs) using the Model Context Protocol (MCP).

## Overview

The Neo4j MCP server enables LLMs to:

1. Query and understand project structures stored in Neo4j
2. Maintain context across different conversations
3. Track changes to projects over time
4. Work with multiple projects in the same Neo4j instance

## Setup as an MCP Server

### Prerequisites

- Neo4j database (local or remote)
- Python 3.8+
- MCP-compatible LLM client (Claude, Cline, ChatGPT, etc.)

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

3. Configure Neo4j connection in `custom_neo4j_mcp/utils/config.py`:
   ```python
   NEO4J_URI = "neo4j://localhost:7687"
   NEO4J_AUTH = ("neo4j", "your-password")
   ```

4. Start the MCP server:
   ```bash
   python -m custom_neo4j_mcp.main
   ```

### Configuring MCP Client

Add the Neo4j MCP server to your MCP client configuration file:

#### For Cline (Claude Desktop)

Edit `cline_mcp_settings.json`:

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

## Available MCP Tools

The Neo4j MCP server provides the following tools that LLMs can use:

### 1. Read Tools

- **get_neo4j_schema**: Get a list of all node types, their attributes, and relationships
- **get_database_info**: Get information about the Neo4j database
- **read_neo4j_cypher**: Execute Cypher read queries to retrieve data
- **get_database_statistics**: Get statistics about the Neo4j database
- **get_node_counts_by_label**: Get the number of nodes for each label
- **get_relationship_counts_by_type**: Get the number of relationships for each type
- **get_indexes**: Get all indexes in the database
- **get_constraints**: Get all constraints in the database
- **get_sample_data**: Get sample data for each node label
- **find_nodes**: Find nodes based on label and property conditions
- **find_relationships**: Find relationships based on type and property conditions
- **find_paths**: Find paths between nodes
- **find_shortest_path**: Find the shortest path between two nodes
- **find_all_paths**: Find all paths between two nodes

### 2. Write Tools

- **write_neo4j_cypher**: Execute updating Cypher queries to modify the database
- **create_index**: Create a new index in the database
- **create_constraint**: Create a new constraint in the database
- **drop_index**: Drop an index from the database
- **drop_constraint**: Drop a constraint from the database

## Using MCP Tools in LLM Conversations

### Tool Usage Pattern

When using the Neo4j MCP tools in an LLM conversation, follow this pattern:

1. **Tool Selection**: Choose the appropriate tool based on the task
2. **Parameter Preparation**: Prepare the required parameters for the tool
3. **Tool Execution**: Execute the tool and wait for the result
4. **Result Processing**: Process the result and continue the conversation

### Example: Reading Data with read_neo4j_cypher

```
<use_mcp_tool>
<server_name>github.com/neo4j-contrib/mcp-neo4j</server_name>
<tool_name>read_neo4j_cypher</tool_name>
<arguments>
{
  "query": "MATCH (c:Component:ProjectNode {project: 'evm-logs-canister'}) RETURN c.name as name, c.description as description"
}
</arguments>
</use_mcp_tool>
```

### Example: Writing Data with write_neo4j_cypher

```
<use_mcp_tool>
<server_name>github.com/neo4j-contrib/mcp-neo4j</server_name>
<tool_name>write_neo4j_cypher</tool_name>
<arguments>
{
  "query": "CREATE (c:Component:ProjectNode {name: 'NewComponent', description: 'A new component', project: 'evm-logs-canister'})"
}
</arguments>
</use_mcp_tool>
```

### Example: Getting Schema Information

```
<use_mcp_tool>
<server_name>github.com/neo4j-contrib/mcp-neo4j</server_name>
<tool_name>get_neo4j_schema</tool_name>
<arguments>
{
  "detailed": true
}
</arguments>
</use_mcp_tool>
```

## Project Configuration and Multi-Project Support

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

### Working with Multiple Projects

When working with multiple projects in the same Neo4j instance:

1. Always include the project name in your queries:
   ```cypher
   MATCH (n:ProjectNode {project: 'your-project-name'}) ...
   ```

2. Use the provided scripts to manage projects:
   - `create_new_project.py`: Create a new project
   - `tag_existing_nodes.py`: Tag existing nodes with project information
   - `query_project.py`: Query project information

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

## Best Practices for LLMs Using Neo4j MCP

1. **Start with Schema Understanding**: Begin by using `get_neo4j_schema` to understand the database structure
   ```
   <use_mcp_tool>
   <server_name>github.com/neo4j-contrib/mcp-neo4j</server_name>
   <tool_name>get_neo4j_schema</tool_name>
   <arguments>
   {
     "detailed": true
   }
   </arguments>
   </use_mcp_tool>
   ```

2. **Project Context**: Always identify the current project first
   ```
   <use_mcp_tool>
   <server_name>github.com/neo4j-contrib/mcp-neo4j</server_name>
   <tool_name>read_neo4j_cypher</tool_name>
   <arguments>
   {
     "query": "MATCH (p:Project) RETURN p.name as name, p.description as description"
   }
   </arguments>
   </use_mcp_tool>
   ```

3. **Use Project Filtering**: Always include project filtering in your queries
   ```
   <use_mcp_tool>
   <server_name>github.com/neo4j-contrib/mcp-neo4j</server_name>
   <tool_name>read_neo4j_cypher</tool_name>
   <arguments>
   {
     "query": "MATCH (n:ProjectNode {project: 'evm-logs-canister'}) ..."
   }
   </arguments>
   </use_mcp_tool>
   ```

4. **Explore Component Relationships**: Understand how components interact
   ```
   <use_mcp_tool>
   <server_name>github.com/neo4j-contrib/mcp-neo4j</server_name>
   <tool_name>read_neo4j_cypher</tool_name>
   <arguments>
   {
     "query": "MATCH (c1:Component:ProjectNode {project: 'evm-logs-canister'})-[r:INTERACTS_WITH]->(c2:Component:ProjectNode {project: 'evm-logs-canister'}) RETURN c1.name as from, c2.name as to"
   }
   </arguments>
   </use_mcp_tool>
   ```

5. **Track Changes**: Review recent changes to understand project evolution
   ```
   <use_mcp_tool>
   <server_name>github.com/neo4j-contrib/mcp-neo4j</server_name>
   <tool_name>read_neo4j_cypher</tool_name>
   <arguments>
   {
     "query": "MATCH (cl:ChangeLog:ProjectNode {project: 'evm-logs-canister'}) RETURN cl.id, cl.description, toString(cl.timestamp) as timestamp ORDER BY cl.timestamp DESC LIMIT 5"
   }
   </arguments>
   </use_mcp_tool>
   ```

6. **Record New Changes**: After making changes to the project, record them in the graph
   ```
   <use_mcp_tool>
   <server_name>github.com/neo4j-contrib/mcp-neo4j</server_name>
   <tool_name>write_neo4j_cypher</tool_name>
   <arguments>
   {
     "query": "CREATE (cl:ChangeLog:ProjectNode {id: 'CL-002', description: 'Added new feature', timestamp: datetime(), type: 'FEATURE', author: 'developer', project: 'evm-logs-canister'})"
   }
   </arguments>
   </use_mcp_tool>
   ```

## Troubleshooting

- **Connection Issues**: Verify Neo4j credentials and database status
- **Missing Nodes**: Check that nodes have the correct project property and ProjectNode label
- **Query Performance**: Use the created indexes for better performance:
  - Index on ProjectNode(project)
  - Index on Component(name, project)
  - Index on Function(name, project)

## Resources

- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/current/)
- [Model Context Protocol](https://modelcontextprotocol.io/introduction)
- [Neo4j MCP GitHub Repository](https://github.com/neo4j-contrib/mcp-neo4j)
