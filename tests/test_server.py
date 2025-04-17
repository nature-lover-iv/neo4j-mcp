#!/usr/bin/env python3
"""
Unit tests for the Neo4j MCP server module.
"""
import unittest
from unittest.mock import patch, MagicMock, AsyncMock

import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

import mcp.types as types
from custom_neo4j_mcp.core.server import Neo4jMCPServer


class TestNeo4jMCPServer(unittest.TestCase):
    """
    Test cases for the Neo4jMCPServer class.
    """
    
    @patch('custom_neo4j_mcp.core.server.Neo4jDatabase')
    def test_init(self, mock_db_class):
        """
        Test initializing the server.
        """
        # Set up the mock
        mock_db = MagicMock()
        mock_db_class.return_value = mock_db
        
        # Create the server
        server = Neo4jMCPServer(
            uri="bolt://example.com:7687",
            username="user",
            password="pass",
            database="test",
            server_name="test-server",
            server_version="1.0.0"
        )
        
        # Check that the database was created with the correct arguments
        mock_db_class.assert_called_once_with(
            uri="bolt://example.com:7687",
            username="user",
            password="pass",
            database="test"
        )
        
        # Check that the server name and version were set correctly
        self.assertEqual(server.server_name, "test-server")
        self.assertEqual(server.server_version, "1.0.0")
        
    @patch('custom_neo4j_mcp.core.server.Neo4jDatabase')
    def test_get_tools(self, mock_db_class):
        """
        Test getting the list of available tools.
        """
        # Set up the mock
        mock_db = MagicMock()
        mock_db_class.return_value = mock_db
        
        # Create the server
        server = Neo4jMCPServer()
        
        # Get the tools
        tools = server.get_tools()
        
        # Check that the tools list is not empty
        self.assertGreater(len(tools), 0)
        
        # Check that all tools have the required attributes
        for tool in tools:
            self.assertIsInstance(tool, types.Tool)
            self.assertTrue(hasattr(tool, 'name'))
            self.assertTrue(hasattr(tool, 'description'))
            self.assertTrue(hasattr(tool, 'inputSchema'))
            
    @patch('custom_neo4j_mcp.core.server.Neo4jDatabase')
    async def test_get_schema(self, mock_db_class):
        """
        Test getting the schema from the server.
        """
        # Set up the mock
        mock_db = MagicMock()
        mock_db_class.return_value = mock_db
        mock_db.get_schema.return_value = {"Person": {"properties": {"name": {"type": "STRING"}}}}
        mock_db.get_basic_schema.return_value = {"nodes": {"Person": {"properties": {"name": {"type": "unknown"}}}}}
        
        # Create the server
        server = Neo4jMCPServer()
        
        # Test with detailed=True
        result = await server.get_schema({"detailed": True})
        
        # Check that the result is correct
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], types.TextContent)
        self.assertEqual(result[0].type, "text")
        
        # Parse the JSON in the result
        schema = json.loads(result[0].text)
        self.assertEqual(schema, {"Person": {"properties": {"name": {"type": "STRING"}}}})
        
        # Test with detailed=False
        result = await server.get_schema({"detailed": False})
        
        # Check that the result is correct
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], types.TextContent)
        self.assertEqual(result[0].type, "text")
        
        # Parse the JSON in the result
        schema = json.loads(result[0].text)
        self.assertEqual(schema, {"nodes": {"Person": {"properties": {"name": {"type": "unknown"}}}}})
        
    @patch('custom_neo4j_mcp.core.server.Neo4jDatabase')
    async def test_execute_read_query(self, mock_db_class):
        """
        Test executing a read query on the server.
        """
        # Set up the mock
        mock_db = MagicMock()
        mock_db_class.return_value = mock_db
        mock_db.run_query.return_value = [{"name": "Alice"}]
        
        # Create the server
        server = Neo4jMCPServer()
        
        # Test with a valid query
        result = await server.execute_read_query({"query": "MATCH (n) RETURN n.name AS name", "params": {"param": "value"}})
        
        # Check that the result is correct
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], types.TextContent)
        self.assertEqual(result[0].type, "text")
        
        # Parse the JSON in the result
        data = json.loads(result[0].text)
        self.assertEqual(data, [{"name": "Alice"}])
        
        # Check that the query was run with the correct arguments
        mock_db.run_query.assert_called_once_with("MATCH (n) RETURN n.name AS name", {"param": "value"})
        
        # Test with no query
        result = await server.execute_read_query({"params": {"param": "value"}})
        
        # Check that the result is correct
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], types.TextContent)
        self.assertEqual(result[0].type, "text")
        self.assertEqual(result[0].text, "No query provided")
        
    @patch('custom_neo4j_mcp.core.server.Neo4jDatabase')
    async def test_execute_write_query(self, mock_db_class):
        """
        Test executing a write query on the server.
        """
        # Set up the mock
        mock_db = MagicMock()
        mock_db_class.return_value = mock_db
        mock_db.run_write_query.return_value = {
            "nodes_created": 1,
            "nodes_deleted": 0,
            "relationships_created": 0,
            "relationships_deleted": 0,
            "properties_set": 2
        }
        
        # Create the server
        server = Neo4jMCPServer()
        
        # Test with a valid query
        result = await server.execute_write_query({"query": "CREATE (n:Person {name: 'Alice', age: 30})", "params": {"param": "value"}})
        
        # Check that the result is correct
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], types.TextContent)
        self.assertEqual(result[0].type, "text")
        
        # Parse the JSON in the result
        data = json.loads(result[0].text)
        self.assertEqual(data, {
            "nodes_created": 1,
            "nodes_deleted": 0,
            "relationships_created": 0,
            "relationships_deleted": 0,
            "properties_set": 2
        })
        
        # Check that the query was run with the correct arguments
        mock_db.run_write_query.assert_called_once_with("CREATE (n:Person {name: 'Alice', age: 30})", {"param": "value"})
        
        # Test with no query
        result = await server.execute_write_query({"params": {"param": "value"}})
        
        # Check that the result is correct
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], types.TextContent)
        self.assertEqual(result[0].type, "text")
        self.assertEqual(result[0].text, "No query provided")
        
    @patch('custom_neo4j_mcp.core.server.Neo4jDatabase')
    async def test_get_database_statistics(self, mock_db_class):
        """
        Test getting database statistics from the server.
        """
        # Set up the mock
        mock_db = MagicMock()
        mock_db_class.return_value = mock_db
        mock_db.get_node_count.return_value = 10
        mock_db.get_relationship_count.return_value = 20
        mock_db.get_database_info.return_value = {
            "version": "5.0.0",
            "edition": "community",
            "database_name": "neo4j",
            "address": "bolt://localhost:7687"
        }
        
        # Create the server
        server = Neo4jMCPServer()
        
        # Get the statistics
        result = await server.get_database_statistics({})
        
        # Check that the result is correct
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], types.TextContent)
        self.assertEqual(result[0].type, "text")
        
        # Parse the JSON in the result
        stats = json.loads(result[0].text)
        self.assertEqual(stats, {
            "node_count": 10,
            "relationship_count": 20,
            "database_info": {
                "version": "5.0.0",
                "edition": "community",
                "database_name": "neo4j",
                "address": "bolt://localhost:7687"
            }
        })
        
    @patch('custom_neo4j_mcp.core.server.Neo4jDatabase')
    async def test_find_nodes(self, mock_db_class):
        """
        Test finding nodes with the server.
        """
        # Set up the mock
        mock_db = MagicMock()
        mock_db_class.return_value = mock_db
        mock_db.run_query.return_value = [{"n": {"name": "Alice", "age": 30}}]
        
        # Create the server
        server = Neo4jMCPServer()
        
        # Test with a valid label and properties
        result = await server.find_nodes({
            "label": "Person",
            "properties": {"name": "Alice"},
            "limit": 5
        })
        
        # Check that the result is correct
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], types.TextContent)
        self.assertEqual(result[0].type, "text")
        
        # Parse the JSON in the result
        data = json.loads(result[0].text)
        self.assertEqual(data, [{"n": {"name": "Alice", "age": 30}}])
        
        # Check that the query was run with the correct arguments
        mock_db.run_query.assert_called_once()
        query_arg = mock_db.run_query.call_args[0][0]
        self.assertIn("MATCH (n:Person)", query_arg)
        self.assertIn("WHERE n.name = 'Alice'", query_arg)
        self.assertIn("LIMIT 5", query_arg)
        
        # Test with no label
        result = await server.find_nodes({
            "properties": {"name": "Alice"},
            "limit": 5
        })
        
        # Check that the result is correct
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], types.TextContent)
        self.assertEqual(result[0].type, "text")
        self.assertEqual(result[0].text, "Node label is required")


if __name__ == "__main__":
    unittest.main()
