#!/usr/bin/env python3
"""
Integration tests for the Neo4j MCP server.

These tests require a running Neo4j database. They will create and delete data in the database,
so they should be run on a test database, not a production database.

To run these tests:
1. Start a Neo4j database
2. Set the NEO4J_URL, NEO4J_USERNAME, and NEO4J_PASSWORD environment variables
3. Run the tests with pytest: pytest -xvs tests/test_integration.py
"""
import os
import sys
import json
import asyncio
import unittest
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

import mcp.types as types
from custom_neo4j_mcp.core.server import Neo4jMCPServer
from custom_neo4j_mcp.core.database import Neo4jDatabase


class TestNeo4jMCPServerIntegration(unittest.TestCase):
    """
    Integration tests for the Neo4jMCPServer class.
    
    These tests require a running Neo4j database. They will create and delete data in the database,
    so they should be run on a test database, not a production database.
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Set up the test class.
        """
        # Get Neo4j connection details from environment variables
        cls.neo4j_url = os.environ.get("NEO4J_URL", "bolt://localhost:7687")
        cls.neo4j_username = os.environ.get("NEO4J_USERNAME", "neo4j")
        cls.neo4j_password = os.environ.get("NEO4J_PASSWORD", "ihorek12345")
        
        # Create the database
        cls.db = Neo4jDatabase(
            uri=cls.neo4j_url,
            username=cls.neo4j_username,
            password=cls.neo4j_password
        )
        
        # Create the server
        cls.server = Neo4jMCPServer(
            uri=cls.neo4j_url,
            username=cls.neo4j_username,
            password=cls.neo4j_password
        )
        
        # Clear the database
        cls.db.run_write_query("MATCH (n) DETACH DELETE n")
        
    @classmethod
    def tearDownClass(cls):
        """
        Tear down the test class.
        """
        # Clear the database
        cls.db.run_write_query("MATCH (n) DETACH DELETE n")
        
        # Close the database connection
        cls.db.close()
        
    def setUp(self):
        """
        Set up each test.
        """
        # Clear the database
        self.db.run_write_query("MATCH (n) DETACH DELETE n")
        
        # Create some test data
        self.db.run_write_query("""
        CREATE (alice:Person {name: 'Alice', age: 30})
        CREATE (bob:Person {name: 'Bob', age: 40})
        CREATE (charlie:Person {name: 'Charlie', age: 25})
        CREATE (alice)-[:KNOWS {since: 2020}]->(bob)
        CREATE (bob)-[:KNOWS {since: 2021}]->(charlie)
        CREATE (alice)-[:WORKS_WITH {project: 'Neo4j MCP'}]->(charlie)
        """)
        
    def tearDown(self):
        """
        Tear down each test.
        """
        # Clear the database
        self.db.run_write_query("MATCH (n) DETACH DELETE n")
        
    async def test_get_schema(self):
        """
        Test getting the schema from the server.
        """
        # Get the schema
        result = await self.server.get_schema({"detailed": False})
        
        # Check that the result is correct
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], types.TextContent)
        self.assertEqual(result[0].type, "text")
        
        # Parse the JSON in the result
        schema = json.loads(result[0].text)
        
        # Check that the schema contains the expected node labels
        self.assertIn("nodes", schema)
        self.assertIn("Person", schema["nodes"])
        
        # Check that the schema contains the expected relationship types
        self.assertIn("relationships", schema)
        self.assertTrue(any(rel["type"] == "KNOWS" for rel in schema["relationships"]))
        self.assertTrue(any(rel["type"] == "WORKS_WITH" for rel in schema["relationships"]))
        
    async def test_execute_read_query(self):
        """
        Test executing a read query on the server.
        """
        # Execute a read query
        result = await self.server.execute_read_query({
            "query": "MATCH (p:Person) RETURN p.name AS name, p.age AS age ORDER BY p.name"
        })
        
        # Check that the result is correct
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], types.TextContent)
        self.assertEqual(result[0].type, "text")
        
        # Parse the JSON in the result
        data = json.loads(result[0].text)
        
        # Check that the data contains the expected people
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["name"], "Alice")
        self.assertEqual(data[0]["age"], 30)
        self.assertEqual(data[1]["name"], "Bob")
        self.assertEqual(data[1]["age"], 40)
        self.assertEqual(data[2]["name"], "Charlie")
        self.assertEqual(data[2]["age"], 25)
        
    async def test_execute_write_query(self):
        """
        Test executing a write query on the server.
        """
        # Execute a write query
        result = await self.server.execute_write_query({
            "query": "CREATE (dave:Person {name: 'Dave', age: 35})"
        })
        
        # Check that the result is correct
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], types.TextContent)
        self.assertEqual(result[0].type, "text")
        
        # Parse the JSON in the result
        data = json.loads(result[0].text)
        
        # Check that the data contains the expected counters
        self.assertEqual(data["nodes_created"], 1)
        self.assertEqual(data["properties_set"], 2)
        
        # Check that the node was actually created
        result = self.db.run_query("MATCH (p:Person {name: 'Dave'}) RETURN p.name AS name, p.age AS age")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Dave")
        self.assertEqual(result[0]["age"], 35)
        
    async def test_get_database_statistics(self):
        """
        Test getting database statistics from the server.
        """
        # Get the statistics
        result = await self.server.get_database_statistics({})
        
        # Check that the result is correct
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], types.TextContent)
        self.assertEqual(result[0].type, "text")
        
        # Parse the JSON in the result
        stats = json.loads(result[0].text)
        
        # Check that the stats contain the expected counts
        self.assertEqual(stats["node_count"], 3)
        self.assertEqual(stats["relationship_count"], 3)
        
    async def test_find_nodes(self):
        """
        Test finding nodes with the server.
        """
        # Find nodes
        result = await self.server.find_nodes({
            "label": "Person",
            "properties": {"name": "Alice"},
            "limit": 10
        })
        
        # Check that the result is correct
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], types.TextContent)
        self.assertEqual(result[0].type, "text")
        
        # Parse the JSON in the result
        data = json.loads(result[0].text)
        
        # Check that the data contains the expected node
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["n"]["name"], "Alice")
        self.assertEqual(data[0]["n"]["age"], 30)
        
    async def test_find_relationships(self):
        """
        Test finding relationships with the server.
        """
        # Find relationships
        result = await self.server.find_relationships({
            "type": "KNOWS",
            "source_label": "Person",
            "target_label": "Person",
            "limit": 10
        })
        
        # Check that the result is correct
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], types.TextContent)
        self.assertEqual(result[0].type, "text")
        
        # Parse the JSON in the result
        data = json.loads(result[0].text)
        
        # Check that the data contains the expected relationships
        self.assertEqual(len(data), 2)
        
        # Check the first relationship
        self.assertEqual(data[0]["source"]["name"], "Alice")
        self.assertEqual(data[0]["r"]["since"], 2020)
        self.assertEqual(data[0]["target"]["name"], "Bob")
        
        # Check the second relationship
        self.assertEqual(data[1]["source"]["name"], "Bob")
        self.assertEqual(data[1]["r"]["since"], 2021)
        self.assertEqual(data[1]["target"]["name"], "Charlie")
        
    async def test_find_paths(self):
        """
        Test finding paths with the server.
        """
        # Find paths
        result = await self.server.find_paths({
            "start_label": "Person",
            "start_properties": {"name": "Alice"},
            "end_label": "Person",
            "end_properties": {"name": "Charlie"},
            "max_depth": 3,
            "limit": 10
        })
        
        # Check that the result is correct
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], types.TextContent)
        self.assertEqual(result[0].type, "text")
        
        # Parse the JSON in the result
        data = json.loads(result[0].text)
        
        # Check that the data contains the expected paths
        self.assertEqual(len(data), 2)
        
        # Check that both paths start with Alice and end with Charlie
        for path in data:
            self.assertEqual(path["nodes"][0]["name"], "Alice")
            self.assertEqual(path["nodes"][-1]["name"], "Charlie")
            
        # Check that one path goes through Bob
        bob_path = next((path for path in data if any(node["name"] == "Bob" for node in path["nodes"])), None)
        self.assertIsNotNone(bob_path)
        self.assertEqual(bob_path["length"], 2)
        
        # Check that one path is direct
        direct_path = next((path for path in data if len(path["nodes"]) == 2), None)
        self.assertIsNotNone(direct_path)
        self.assertEqual(direct_path["length"], 1)
        self.assertEqual(direct_path["relationships"][0]["project"], "Neo4j MCP")
        
    async def test_find_shortest_path(self):
        """
        Test finding the shortest path with the server.
        """
        # Find the shortest path
        result = await self.server.find_shortest_path({
            "start_label": "Person",
            "start_properties": {"name": "Alice"},
            "end_label": "Person",
            "end_properties": {"name": "Charlie"},
            "max_depth": 5
        })
        
        # Check that the result is correct
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], types.TextContent)
        self.assertEqual(result[0].type, "text")
        
        # Parse the JSON in the result
        data = json.loads(result[0].text)
        
        # Check that the data contains the expected path
        self.assertEqual(data["nodes"][0]["name"], "Alice")
        self.assertEqual(data["nodes"][-1]["name"], "Charlie")
        self.assertEqual(data["length"], 1)  # Direct path is shortest
        self.assertEqual(data["relationships"][0]["project"], "Neo4j MCP")
        
    async def test_create_and_drop_index(self):
        """
        Test creating and dropping an index with the server.
        """
        # Create an index
        result = await self.server.create_index({
            "label": "Person",
            "properties": ["name"],
            "name": "person_name_idx"
        })
        
        # Check that the result is correct
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], types.TextContent)
        self.assertEqual(result[0].type, "text")
        self.assertIn("Index created successfully", result[0].text)
        
        # Get the indexes
        result = await self.server.get_indexes({})
        
        # Check that the result is correct
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], types.TextContent)
        self.assertEqual(result[0].type, "text")
        
        # Parse the JSON in the result
        data = json.loads(result[0].text)
        
        # Check that the data contains the expected index
        self.assertTrue(any(idx.get("name") == "person_name_idx" for idx in data))
        
        # Drop the index
        result = await self.server.drop_index({
            "name": "person_name_idx"
        })
        
        # Check that the result is correct
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], types.TextContent)
        self.assertEqual(result[0].type, "text")
        self.assertIn("Index person_name_idx dropped successfully", result[0].text)
        
        # Get the indexes again
        result = await self.server.get_indexes({})
        
        # Check that the result is correct
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], types.TextContent)
        self.assertEqual(result[0].type, "text")
        
        # Parse the JSON in the result
        data = json.loads(result[0].text)
        
        # Check that the data does not contain the index
        self.assertFalse(any(idx.get("name") == "person_name_idx" for idx in data))


def run_tests():
    """
    Run the integration tests.
    """
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestNeo4jMCPServerIntegration)
    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == "__main__":
    # Run the tests asynchronously
    asyncio.run(run_tests())
