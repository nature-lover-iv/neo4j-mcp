# Using Neo4j MCP Server with Cline

This example demonstrates how to use the Neo4j MCP server with Cline.

## Setup

1. Install the Neo4j MCP server:

```bash
# Clone the repository
git clone https://github.com/nature-lover-iv/neo4j-mcp.git
cd neo4j-mcp

# Install the package
pip install -e .
```

2. Configure Cline to use the Neo4j MCP server:

Edit your `cline_mcp_settings.json` file (usually located at `~/.config/cline/cline_mcp_settings.json` or similar) and add the following:

```json
{
  "mcpServers": {
    "github.com/neo4j-contrib/mcp-neo4j": {
      "command": "neo4j-mcp",
      "args": [],
      "env": {
        "NEO4J_URL": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "your-password"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

3. Start Neo4j:

Make sure your Neo4j database is running. If you're using Neo4j Desktop, start your database from there. If you're using a standalone Neo4j installation, start it with:

```bash
neo4j start
```

4. Restart Cline to load the new MCP server.

## Example Prompts

Here are some example prompts you can use with Cline to interact with your Neo4j database:

### Get Database Schema

```
What's the schema of my Neo4j database?
```

### Create Data

```
Create a simple graph with 3 Person nodes named Alice, Bob, and Charlie, with ages 30, 40, and 25 respectively. Connect them with KNOWS relationships.
```

### Query Data

```
Show me all the Person nodes in my database.
```

### Find Paths

```
Find the shortest path between Alice and Charlie.
```

### Database Statistics

```
How many nodes and relationships are in my database?
```

### Create Indexes

```
Create an index on the name property of Person nodes.
```

## Example Conversation

Here's an example conversation with Cline using the Neo4j MCP server:

**User**: What's the schema of my Neo4j database?

**Cline**: I'll check the schema of your Neo4j database.

*Cline uses the get_neo4j_schema tool*

Your Neo4j database has the following schema:

- Node Labels:
  - Person

- Properties:
  - Person.name
  - Person.age

- Relationship Types:
  - KNOWS

**User**: Show me all the Person nodes.

**Cline**: Let me query all Person nodes in your database.

*Cline uses the read_neo4j_cypher tool*

Here are all the Person nodes in your database:

| name    | age |
|---------|-----|
| Alice   | 30  |
| Bob     | 40  |
| Charlie | 25  |

**User**: Find the shortest path between Alice and Charlie.

**Cline**: I'll find the shortest path between Alice and Charlie.

*Cline uses the find_shortest_path tool*

The shortest path from Alice to Charlie is:

Alice --[KNOWS]--> Bob --[KNOWS]--> Charlie

This path has a length of 2 relationships.

**User**: Create an index on the name property of Person nodes.

**Cline**: I'll create an index on the name property of Person nodes.

*Cline uses the create_index tool*

Index created successfully on :Person(name).
