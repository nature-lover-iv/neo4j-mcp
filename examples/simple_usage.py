#!/usr/bin/env python3
"""
Simple example of using the Neo4j MCP server.

This script demonstrates how to:
1. Connect to a Neo4j database
2. Create some sample data
3. Query the data
4. Find paths between nodes
"""
import os
import sys
import asyncio
import json
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_neo4j_mcp.core.database import Neo4jDatabase

async def main():
    # Connect to Neo4j
    print("Connecting to Neo4j...")
    db = Neo4jDatabase(
        uri=os.environ.get("NEO4J_URL", "bolt://localhost:7687"),
        username=os.environ.get("NEO4J_USERNAME", "neo4j"),
        password=os.environ.get("NEO4J_PASSWORD", "password")
    )
    
    # Create some sample data
    print("\nCreating sample data...")
    
    # Clear existing data
    db.run_write_query("MATCH (n) DETACH DELETE n")
    
    # Create people
    create_people_query = """
    CREATE (alice:Person {name: 'Alice', age: 30})
    CREATE (bob:Person {name: 'Bob', age: 40})
    CREATE (charlie:Person {name: 'Charlie', age: 25})
    CREATE (dave:Person {name: 'Dave', age: 35})
    """
    db.run_write_query(create_people_query)
    
    # Create relationships
    create_relationships_query = """
    MATCH (alice:Person {name: 'Alice'}), (bob:Person {name: 'Bob'})
    CREATE (alice)-[:KNOWS {since: 2020}]->(bob)
    
    MATCH (bob:Person {name: 'Bob'}), (charlie:Person {name: 'Charlie'})
    CREATE (bob)-[:KNOWS {since: 2021}]->(charlie)
    
    MATCH (charlie:Person {name: 'Charlie'}), (dave:Person {name: 'Dave'})
    CREATE (charlie)-[:KNOWS {since: 2022}]->(dave)
    
    MATCH (alice:Person {name: 'Alice'}), (dave:Person {name: 'Dave'})
    CREATE (alice)-[:WORKS_WITH {project: 'Neo4j MCP'}]->(dave)
    """
    db.run_write_query(create_relationships_query)
    
    # Get node count
    node_count = db.get_node_count()
    print(f"Created {node_count} nodes")
    
    # Get relationship count
    rel_count = db.get_relationship_count()
    print(f"Created {rel_count} relationships")
    
    # Get schema
    print("\nGetting schema...")
    schema = db.get_basic_schema()
    print(json.dumps(schema, indent=2))
    
    # Query all people
    print("\nQuerying all people...")
    people_query = "MATCH (p:Person) RETURN p.name AS name, p.age AS age ORDER BY p.name"
    people = db.run_query(people_query)
    print(json.dumps(people, indent=2))
    
    # Find paths between Alice and Charlie
    print("\nFinding paths between Alice and Charlie...")
    paths_query = """
    MATCH path = (alice:Person {name: 'Alice'})-[*1..3]->(charlie:Person {name: 'Charlie'})
    RETURN path
    LIMIT 1
    """
    
    with db.get_session() as session:
        result = session.run(paths_query)
        record = result.single()
        
        if record:
            path = record["path"]
            path_data = {
                "nodes": [dict(node.items()) for node in path.nodes],
                "relationships": [dict(rel.items()) for rel in path.relationships],
                "length": len(path.relationships)
            }
            print(json.dumps(path_data, indent=2))
        else:
            print("No path found")
    
    # Close the connection
    db.close()
    print("\nDone!")

if __name__ == "__main__":
    asyncio.run(main())
