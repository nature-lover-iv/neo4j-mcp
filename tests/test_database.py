#!/usr/bin/env python3
"""
Unit tests for the Neo4j database module.
"""
import os
import unittest
from unittest.mock import patch, MagicMock

import sys
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_neo4j_mcp.core.database import Neo4jDatabase


class TestNeo4jDatabase(unittest.TestCase):
    """
    Test cases for the Neo4jDatabase class.
    """
    
    @patch('custom_neo4j_mcp.core.database.GraphDatabase')
    def test_init_with_default_values(self, mock_graph_db):
        """
        Test initializing the database with default values.
        """
        # Set up the mock
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        
        # Create the database
        db = Neo4jDatabase()
        
        # Check that the driver was created with the correct arguments
        mock_graph_db.driver.assert_called_once_with(
            "bolt://localhost:7687",
            auth=("neo4j", "")
        )
        
        # Check that verify_connectivity was called
        mock_driver.verify_connectivity.assert_called_once()
        
    @patch('custom_neo4j_mcp.core.database.GraphDatabase')
    def test_init_with_custom_values(self, mock_graph_db):
        """
        Test initializing the database with custom values.
        """
        # Set up the mock
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        
        # Create the database
        db = Neo4jDatabase(
            uri="bolt://example.com:7687",
            username="user",
            password="pass",
            database="test"
        )
        
        # Check that the driver was created with the correct arguments
        mock_graph_db.driver.assert_called_once_with(
            "bolt://example.com:7687",
            auth=("user", "pass")
        )
        
        # Check that verify_connectivity was called
        mock_driver.verify_connectivity.assert_called_once()
        
        # Check that the database was set correctly
        self.assertEqual(db.database, "test")
        
    @patch('custom_neo4j_mcp.core.database.GraphDatabase')
    def test_init_with_environment_variables(self, mock_graph_db):
        """
        Test initializing the database with environment variables.
        """
        # Set up the mock
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        
        # Set environment variables
        with patch.dict(os.environ, {
            "NEO4J_URL": "bolt://env.example.com:7687",
            "NEO4J_USERNAME": "env_user",
            "NEO4J_PASSWORD": "env_pass",
            "NEO4J_DATABASE": "env_test"
        }):
            # Create the database
            db = Neo4jDatabase()
            
            # Check that the driver was created with the correct arguments
            mock_graph_db.driver.assert_called_once_with(
                "bolt://env.example.com:7687",
                auth=("env_user", "env_pass")
            )
            
            # Check that verify_connectivity was called
            mock_driver.verify_connectivity.assert_called_once()
            
            # Check that the database was set correctly
            self.assertEqual(db.database, "env_test")
            
    @patch('custom_neo4j_mcp.core.database.GraphDatabase')
    def test_close(self, mock_graph_db):
        """
        Test closing the database connection.
        """
        # Set up the mock
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        
        # Create the database and close it
        db = Neo4jDatabase()
        db.close()
        
        # Check that the driver was closed
        mock_driver.close.assert_called_once()
        
        # Check that the driver was set to None
        self.assertIsNone(db._driver)
        
    @patch('custom_neo4j_mcp.core.database.GraphDatabase')
    def test_get_session(self, mock_graph_db):
        """
        Test getting a session from the database.
        """
        # Set up the mock
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        
        # Create the database and get a session
        db = Neo4jDatabase(database="test")
        db.get_session()
        
        # Check that the session was created with the correct arguments
        mock_driver.session.assert_called_once_with(database="test")
        
    @patch('custom_neo4j_mcp.core.database.GraphDatabase')
    def test_run_query(self, mock_graph_db):
        """
        Test running a query on the database.
        """
        # Set up the mock
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_record = MagicMock()
        
        mock_graph_db.driver.return_value = mock_driver
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_session.run.return_value = mock_result
        mock_result.__iter__.return_value = [mock_record]
        mock_record.data.return_value = {"name": "Alice"}
        
        # Create the database and run a query
        db = Neo4jDatabase()
        result = db.run_query("MATCH (n) RETURN n.name AS name", {"param": "value"})
        
        # Check that the session was created
        mock_driver.session.assert_called_once()
        
        # Check that the query was run with the correct arguments
        mock_session.run.assert_called_once_with("MATCH (n) RETURN n.name AS name", {"param": "value"})
        
        # Check that the result was processed correctly
        self.assertEqual(result, [{"name": "Alice"}])
        
    @patch('custom_neo4j_mcp.core.database.GraphDatabase')
    def test_run_write_query(self, mock_graph_db):
        """
        Test running a write query on the database.
        """
        # Set up the mock
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_summary = MagicMock()
        mock_counters = MagicMock()
        
        mock_graph_db.driver.return_value = mock_driver
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_session.run.return_value = mock_result
        mock_result.consume.return_value = mock_summary
        mock_summary.counters = mock_counters
        
        # Set up the counters
        mock_counters.nodes_created = 1
        mock_counters.nodes_deleted = 2
        mock_counters.relationships_created = 3
        mock_counters.relationships_deleted = 4
        mock_counters.properties_set = 5
        mock_counters.labels_added = 6
        mock_counters.labels_removed = 7
        mock_counters.indexes_added = 8
        mock_counters.indexes_removed = 9
        mock_counters.constraints_added = 10
        mock_counters.constraints_removed = 11
        
        # Create the database and run a write query
        db = Neo4jDatabase()
        result = db.run_write_query("CREATE (n:Person {name: 'Alice'})", {"param": "value"})
        
        # Check that the session was created
        mock_driver.session.assert_called_once()
        
        # Check that the query was run with the correct arguments
        mock_session.run.assert_called_once_with("CREATE (n:Person {name: 'Alice'})", {"param": "value"})
        
        # Check that the result was processed correctly
        self.assertEqual(result, {
            "nodes_created": 1,
            "nodes_deleted": 2,
            "relationships_created": 3,
            "relationships_deleted": 4,
            "properties_set": 5,
            "labels_added": 6,
            "labels_removed": 7,
            "indexes_added": 8,
            "indexes_removed": 9,
            "constraints_added": 10,
            "constraints_removed": 11
        })
        
    @patch('custom_neo4j_mcp.core.database.GraphDatabase')
    def test_get_schema(self, mock_graph_db):
        """
        Test getting the schema from the database.
        """
        # Set up the mock
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_record = MagicMock()
        
        mock_graph_db.driver.return_value = mock_driver
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_session.run.return_value = mock_result
        mock_result.single.return_value = mock_record
        mock_record.__getitem__.return_value = {"Person": {"properties": {"name": {"type": "STRING"}}}}
        
        # Create the database and get the schema
        db = Neo4jDatabase()
        schema = db.get_schema()
        
        # Check that the session was created
        mock_driver.session.assert_called_once()
        
        # Check that the query was run
        mock_session.run.assert_called_once()
        
        # Check that the result was processed correctly
        self.assertEqual(schema, {"Person": {"properties": {"name": {"type": "STRING"}}}})
        
    @patch('custom_neo4j_mcp.core.database.GraphDatabase')
    def test_get_basic_schema(self, mock_graph_db):
        """
        Test getting the basic schema from the database.
        """
        # Set up the mock
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_labels_result = MagicMock()
        mock_props_result = MagicMock()
        mock_rels_result = MagicMock()
        mock_rel_details_result = MagicMock()
        
        mock_graph_db.driver.return_value = mock_driver
        mock_driver.session.return_value.__enter__.return_value = mock_session
        
        # Set up the label query
        mock_session.run.side_effect = [
            mock_labels_result,  # For the labels query
            mock_props_result,   # For the properties query
            mock_rels_result,    # For the relationship types query
            mock_rel_details_result  # For the relationship details query
        ]
        
        # Set up the label result
        mock_label_record = MagicMock()
        mock_label_record.__getitem__.return_value = "Person"
        mock_labels_result.__iter__.return_value = [mock_label_record]
        
        # Set up the properties result
        mock_prop_record = MagicMock()
        mock_prop_record.__getitem__.return_value = "name"
        mock_props_result.__iter__.return_value = [mock_prop_record]
        
        # Set up the relationship types result
        mock_rel_record = MagicMock()
        mock_rel_record.__getitem__.return_value = "KNOWS"
        mock_rels_result.__iter__.return_value = [mock_rel_record]
        
        # Set up the relationship details result
        mock_rel_detail_record = MagicMock()
        mock_rel_detail_record.__getitem__.side_effect = lambda key: ["Person"] if key == "source_labels" else ["Person"] if key == "target_labels" else None
        mock_rel_details_result.__iter__.return_value = [mock_rel_detail_record]
        
        # Create the database and get the basic schema
        db = Neo4jDatabase()
        schema = db.get_basic_schema()
        
        # Check that the session was created
        self.assertEqual(mock_driver.session.call_count, 1)
        
        # Check that the queries were run
        self.assertEqual(mock_session.run.call_count, 4)
        
        # Check that the result was processed correctly
        self.assertEqual(schema, {
            "nodes": {
                "Person": {
                    "properties": {
                        "name": {"type": "unknown"}
                    }
                }
            },
            "relationships": [
                {
                    "type": "KNOWS",
                    "source": "Person",
                    "target": "Person"
                }
            ]
        })


if __name__ == "__main__":
    unittest.main()
