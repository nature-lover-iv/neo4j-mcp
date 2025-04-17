"""
Neo4j MCP server core module.
"""
import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Callable, Awaitable

import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions

from .database import Neo4jDatabase

logger = logging.getLogger(__name__)

class Neo4jMCPServer:
    """ 
    Neo4j MCP server class.
    Handles MCP server setup, tool registration, and request handling.
    """
    def __init__(
        self,
        uri: str = None,
        username: str = None,
        password: str = None,
        database: str = None,
        server_name: str = "neo4j-mcp-server",
        server_version: str = "0.1.0"
    ):
        """
        Initialize Neo4j MCP server.
        
        Args:
            uri: Neo4j connection URI (e.g., bolt://localhost:7687)
            username: Neo4j username
            password: Neo4j password
            database: Neo4j database name (default: None, uses the default database)
            server_name: MCP server name
            server_version: MCP server version
        """
        self.server_name = server_name
        self.server_version = server_version
        
        # Initialize MCP server
        self.server = Server(
            {
                "name": server_name,
                "version": server_version,
            },
            {
                "capabilities": {
                    "resources": {},
                    "tools": {},
                },
            }
        )
        
        # Initialize Neo4j database
        self.db = Neo4jDatabase(uri, username, password, database)
        
        # Set up tool handlers
        self.setup_tool_handlers()
        
        # Error handling
        self.server.onerror = lambda error: logger.error(f"[MCP Error] {error}")
        
    def setup_tool_handlers(self):
        """
        Set up MCP tool handlers.
        """
        # Register tool list handler
        @self.server.list_tools()
        async def handle_list_tools():
            return self.get_tools()
            
        # Register tool call handler
        @self.server.call_tool()
        async def handle_call_tool(name, arguments):
            try:
                # Schema tools
                if name == "get_neo4j_schema":
                    return await self.get_schema(arguments)
                elif name == "get_database_info":
                    return await self.get_database_info(arguments)
                    
                # Query tools
                elif name == "read_neo4j_cypher":
                    return await self.execute_read_query(arguments)
                elif name == "write_neo4j_cypher":
                    return await self.execute_write_query(arguments)
                elif name == "explain_neo4j_cypher":
                    return await self.explain_query(arguments)
                    
                # Database statistics tools
                elif name == "get_database_statistics":
                    return await self.get_database_statistics(arguments)
                elif name == "get_node_counts_by_label":
                    return await self.get_node_counts_by_label(arguments)
                elif name == "get_relationship_counts_by_type":
                    return await self.get_relationship_counts_by_type(arguments)
                    
                # Database management tools
                elif name == "get_indexes":
                    return await self.get_indexes(arguments)
                elif name == "get_constraints":
                    return await self.get_constraints(arguments)
                elif name == "create_index":
                    return await self.create_index(arguments)
                elif name == "create_constraint":
                    return await self.create_constraint(arguments)
                elif name == "drop_index":
                    return await self.drop_index(arguments)
                elif name == "drop_constraint":
                    return await self.drop_constraint(arguments)
                    
                # Data exploration tools
                elif name == "get_sample_data":
                    return await self.get_sample_data(arguments)
                elif name == "find_nodes":
                    return await self.find_nodes(arguments)
                elif name == "find_relationships":
                    return await self.find_relationships(arguments)
                elif name == "find_paths":
                    return await self.find_paths(arguments)
                    
                # Graph algorithms
                elif name == "find_shortest_path":
                    return await self.find_shortest_path(arguments)
                elif name == "find_all_paths":
                    return await self.find_all_paths(arguments)
                    
                else:
                    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                logger.error(f"Error handling tool call: {e}")
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]
                
    def get_tools(self) -> List[types.Tool]:
        """
        Get the list of available tools.
        
        Returns:
            List of MCP tools
        """
        return [
            # Schema tools
            types.Tool(
                name="get_neo4j_schema",
                description="Get a list of all node types in the graph database, their attributes with name, type, and relationships to other node types",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "detailed": {
                            "type": "boolean",
                            "description": "Whether to include detailed information about properties and relationships"
                        }
                    }
                }
            ),
            types.Tool(
                name="get_database_info",
                description="Get information about the Neo4j database, including version, edition, and address",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            
            # Query tools
            types.Tool(
                name="read_neo4j_cypher",
                description="Execute Cypher read queries to read data from the database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The Cypher query to execute"
                        },
                        "params": {
                            "type": "object",
                            "description": "Parameters for the query"
                        }
                    },
                    "required": ["query"]
                }
            ),
            types.Tool(
                name="write_neo4j_cypher",
                description="Execute updating Cypher queries to modify the database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The Cypher update query to execute"
                        },
                        "params": {
                            "type": "object",
                            "description": "Parameters for the query"
                        }
                    },
                    "required": ["query"]
                }
            ),
            types.Tool(
                name="explain_neo4j_cypher",
                description="Explain a Cypher query execution plan",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The Cypher query to explain"
                        }
                    },
                    "required": ["query"]
                }
            ),
            
            # Database statistics tools
            types.Tool(
                name="get_database_statistics",
                description="Get statistics about the Neo4j database, including node and relationship counts",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            types.Tool(
                name="get_node_counts_by_label",
                description="Get the number of nodes for each label in the database",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            types.Tool(
                name="get_relationship_counts_by_type",
                description="Get the number of relationships for each type in the database",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            
            # Database management tools
            types.Tool(
                name="get_indexes",
                description="Get all indexes in the database",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            types.Tool(
                name="get_constraints",
                description="Get all constraints in the database",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            types.Tool(
                name="create_index",
                description="Create a new index in the database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "label": {
                            "type": "string",
                            "description": "The node label to create the index on"
                        },
                        "properties": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "The properties to include in the index"
                        },
                        "name": {
                            "type": "string",
                            "description": "The name of the index (optional)"
                        },
                        "type": {
                            "type": "string",
                            "description": "The type of index (e.g., 'BTREE', 'FULLTEXT', 'LOOKUP')",
                            "enum": ["BTREE", "FULLTEXT", "LOOKUP"]
                        }
                    },
                    "required": ["label", "properties"]
                }
            ),
            types.Tool(
                name="create_constraint",
                description="Create a new constraint in the database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "label": {
                            "type": "string",
                            "description": "The node label to create the constraint on"
                        },
                        "property": {
                            "type": "string",
                            "description": "The property to create the constraint on"
                        },
                        "name": {
                            "type": "string",
                            "description": "The name of the constraint (optional)"
                        },
                        "type": {
                            "type": "string",
                            "description": "The type of constraint (e.g., 'UNIQUE', 'EXISTS', 'NODE_KEY')",
                            "enum": ["UNIQUE", "EXISTS", "NODE_KEY"]
                        }
                    },
                    "required": ["label", "property", "type"]
                }
            ),
            types.Tool(
                name="drop_index",
                description="Drop an index from the database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the index to drop"
                        }
                    },
                    "required": ["name"]
                }
            ),
            types.Tool(
                name="drop_constraint",
                description="Drop a constraint from the database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the constraint to drop"
                        }
                    },
                    "required": ["name"]
                }
            ),
            
            # Data exploration tools
            types.Tool(
                name="get_sample_data",
                description="Get sample data for each node label in the database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of nodes per label",
                            "default": 10
                        },
                        "labels": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Specific labels to get sample data for (optional)"
                        }
                    }
                }
            ),
            types.Tool(
                name="find_nodes",
                description="Find nodes in the database based on label and property conditions",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "label": {
                            "type": "string",
                            "description": "The node label to search for"
                        },
                        "properties": {
                            "type": "object",
                            "description": "Property conditions for the search"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of nodes to return",
                            "default": 10
                        }
                    },
                    "required": ["label"]
                }
            ),
            types.Tool(
                name="find_relationships",
                description="Find relationships in the database based on type and property conditions",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": "The relationship type to search for"
                        },
                        "source_label": {
                            "type": "string",
                            "description": "The label of the source node (optional)"
                        },
                        "target_label": {
                            "type": "string",
                            "description": "The label of the target node (optional)"
                        },
                        "properties": {
                            "type": "object",
                            "description": "Property conditions for the relationship (optional)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of relationships to return",
                            "default": 10
                        }
                    },
                    "required": ["type"]
                }
            ),
            types.Tool(
                name="find_paths",
                description="Find paths between nodes in the database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "start_label": {
                            "type": "string",
                            "description": "The label of the start node"
                        },
                        "start_properties": {
                            "type": "object",
                            "description": "Property conditions for the start node"
                        },
                        "end_label": {
                            "type": "string",
                            "description": "The label of the end node"
                        },
                        "end_properties": {
                            "type": "object",
                            "description": "Property conditions for the end node"
                        },
                        "max_depth": {
                            "type": "integer",
                            "description": "Maximum path depth",
                            "default": 3
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of paths to return",
                            "default": 5
                        }
                    },
                    "required": ["start_label", "start_properties", "end_label", "end_properties"]
                }
            ),
            
            # Graph algorithms
            types.Tool(
                name="find_shortest_path",
                description="Find the shortest path between two nodes",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "start_label": {
                            "type": "string",
                            "description": "The label of the start node"
                        },
                        "start_properties": {
                            "type": "object",
                            "description": "Property conditions for the start node"
                        },
                        "end_label": {
                            "type": "string",
                            "description": "The label of the end node"
                        },
                        "end_properties": {
                            "type": "object",
                            "description": "Property conditions for the end node"
                        },
                        "relationship_types": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Specific relationship types to consider (optional)"
                        },
                        "max_depth": {
                            "type": "integer",
                            "description": "Maximum path depth",
                            "default": 5
                        }
                    },
                    "required": ["start_label", "start_properties", "end_label", "end_properties"]
                }
            ),
            types.Tool(
                name="find_all_paths",
                description="Find all paths between two nodes",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "start_label": {
                            "type": "string",
                            "description": "The label of the start node"
                        },
                        "start_properties": {
                            "type": "object",
                            "description": "Property conditions for the start node"
                        },
                        "end_label": {
                            "type": "string",
                            "description": "The label of the end node"
                        },
                        "end_properties": {
                            "type": "object",
                            "description": "Property conditions for the end node"
                        },
                        "relationship_types": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Specific relationship types to consider (optional)"
                        },
                        "max_depth": {
                            "type": "integer",
                            "description": "Maximum path depth",
                            "default": 3
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of paths to return",
                            "default": 5
                        }
                    },
                    "required": ["start_label", "start_properties", "end_label", "end_properties"]
                }
            )
        ]
        
    # Tool handler implementations
    
    async def get_schema(self, arguments: Dict[str, Any]) -> List[types.Content]:
        """
        Get the database schema.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Schema information as text content
        """
        detailed = arguments.get("detailed", False)
        
        if detailed:
            # Get detailed schema with APOC if available
            schema = self.db.get_schema()
        else:
            # Get basic schema
            schema = self.db.get_basic_schema()
            
        return [types.TextContent(type="text", text=json.dumps(schema, indent=2))]
        
    async def get_database_info(self, arguments: Dict[str, Any]) -> List[types.Content]:
        """
        Get information about the Neo4j database.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Database information as text content
        """
        info = self.db.get_database_info()
        return [types.TextContent(type="text", text=json.dumps(info, indent=2))]
        
    async def execute_read_query(self, arguments: Dict[str, Any]) -> List[types.Content]:
        """
        Execute a read Cypher query.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Query results as text content
        """
        query = arguments.get("query")
        params = arguments.get("params", {})
        
        if not query:
            return [types.TextContent(type="text", text="No query provided")]
            
        results = self.db.run_query(query, params)
        return [types.TextContent(type="text", text=json.dumps(results, indent=2))]
        
    async def execute_write_query(self, arguments: Dict[str, Any]) -> List[types.Content]:
        """
        Execute a write Cypher query.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Query results as text content
        """
        query = arguments.get("query")
        params = arguments.get("params", {})
        
        if not query:
            return [types.TextContent(type="text", text="No query provided")]
            
        results = self.db.run_write_query(query, params)
        return [types.TextContent(type="text", text=json.dumps(results, indent=2))]
        
    async def explain_query(self, arguments: Dict[str, Any]) -> List[types.Content]:
        """
        Explain a Cypher query execution plan.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Query explanation as text content
        """
        query = arguments.get("query")
        
        if not query:
            return [types.TextContent(type="text", text="No query provided")]
            
        explain_query = f"EXPLAIN {query}"
        
        try:
            with self.db.get_session() as session:
                result = session.run(explain_query)
                plan = result.consume().plan
                
                plan_dict = {
                    "operatorType": plan.operator_type,
                    "identifiers": plan.identifiers,
                    "arguments": plan.arguments,
                    "children": []
                }
                
                # Recursively add children
                def add_children(plan_node, dict_node):
                    for child in plan_node.children:
                        child_dict = {
                            "operatorType": child.operator_type,
                            "identifiers": child.identifiers,
                            "arguments": child.arguments,
                            "children": []
                        }
                        dict_node["children"].append(child_dict)
                        add_children(child, child_dict)
                        
                add_children(plan, plan_dict)
                
                return [types.TextContent(type="text", text=json.dumps(plan_dict, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error explaining query: {str(e)}")]
            
    async def get_database_statistics(self, arguments: Dict[str, Any]) -> List[types.Content]:
        """
        Get statistics about the Neo4j database.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Database statistics as text content
        """
        node_count = self.db.get_node_count()
        relationship_count = self.db.get_relationship_count()
        
        stats = {
            "node_count": node_count,
            "relationship_count": relationship_count,
            "database_info": self.db.get_database_info()
        }
        
        return [types.TextContent(type="text", text=json.dumps(stats, indent=2))]
        
    async def get_node_counts_by_label(self, arguments: Dict[str, Any]) -> List[types.Content]:
        """
        Get the number of nodes for each label in the database.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Node counts as text content
        """
        labels = self.db.get_node_labels()
        counts = {}
        
        for label in labels:
            query = f"MATCH (n:{label}) RETURN count(n) as count"
            with self.db.get_session() as session:
                result = session.run(query)
                record = result.single()
                counts[label] = record["count"] if record else 0
                
        return [types.TextContent(type="text", text=json.dumps(counts, indent=2))]
        
    async def get_relationship_counts_by_type(self, arguments: Dict[str, Any]) -> List[types.Content]:
        """
        Get the number of relationships for each type in the database.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Relationship counts as text content
        """
        types_list = self.db.get_relationship_types()
        counts = {}
        
        for rel_type in types_list:
            query = f"MATCH ()-[r:{rel_type}]->() RETURN count(r) as count"
            with self.db.get_session() as session:
                result = session.run(query)
                record = result.single()
                counts[rel_type] = record["count"] if record else 0
                
        return [types.TextContent(type="text", text=json.dumps(counts, indent=2))]
        
    async def get_indexes(self, arguments: Dict[str, Any]) -> List[types.Content]:
        """
        Get all indexes in the database.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Indexes as text content
        """
        indexes = self.db.get_indexes()
        return [types.TextContent(type="text", text=json.dumps(indexes, indent=2))]
        
    async def get_constraints(self, arguments: Dict[str, Any]) -> List[types.Content]:
        """
        Get all constraints in the database.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Constraints as text content
        """
        constraints = self.db.get_constraints()
        return [types.TextContent(type="text", text=json.dumps(constraints, indent=2))]
        
    async def create_index(self, arguments: Dict[str, Any]) -> List[types.Content]:
        """
        Create a new index in the database.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Result as text content
        """
        label = arguments.get("label")
        properties = arguments.get("properties", [])
        name = arguments.get("name")
        index_type = arguments.get("type", "BTREE")
        
        if not label or not properties:
            return [types.TextContent(type="text", text="Label and properties are required")]
            
        # Format properties for the query
        props_str = ", ".join([f"n.{prop}" for prop in properties])
        
        # Create the query
        if name:
            query = f"CREATE {index_type} INDEX {name} FOR (n:{label}) ON ({props_str})"
        else:
            query = f"CREATE {index_type} INDEX FOR (n:{label}) ON ({props_str})"
            
        try:
            self.db.run_write_query(query)
            return [types.TextContent(type="text", text=f"Index created successfully on :{label}({props_str})")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error creating index: {str(e)}")]
            
    async def create_constraint(self, arguments: Dict[str, Any]) -> List[types.Content]:
        """
        Create a new constraint in the database.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Result as text content
        """
        label = arguments.get("label")
        property_name = arguments.get("property")
        name = arguments.get("name")
        constraint_type = arguments.get("type", "UNIQUE")
        
        if not label or not property_name or not constraint_type:
            return [types.TextContent(type="text", text="Label, property, and type are required")]
            
        # Create the query
        if name:
            if constraint_type == "UNIQUE":
                query = f"CREATE CONSTRAINT {name} FOR (n:{label}) REQUIRE n.{property_name} IS UNIQUE"
            elif constraint_type == "EXISTS":
                query = f"CREATE CONSTRAINT {name} FOR (n:{label}) REQUIRE n.{property_name} IS NOT NULL"
            elif constraint_type == "NODE_KEY":
                query = f"CREATE CONSTRAINT {name} FOR (n:{label}) REQUIRE n.{property_name} IS NODE KEY"
            else:
                return [types.TextContent(type="text", text=f"Unknown constraint type: {constraint_type}")]
        else:
            if constraint_type == "UNIQUE":
                query = f"CREATE CONSTRAINT FOR (n:{label}) REQUIRE n.{property_name} IS UNIQUE"
            elif constraint_type == "EXISTS":
                query = f"CREATE CONSTRAINT FOR (n:{label}) REQUIRE n.{property_name} IS NOT NULL"
            elif constraint_type == "NODE_KEY":
                query = f"CREATE CONSTRAINT FOR (n:{label}) REQUIRE n.{property_name} IS NODE KEY"
            else:
                return [types.TextContent(type="text", text=f"Unknown constraint type: {constraint_type}")]
                
        try:
            self.db.run_write_query(query)
            return [types.TextContent(type="text", text=f"Constraint created successfully on :{label}.{property_name}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error creating constraint: {str(e)}")]
            
    async def drop_index(self, arguments: Dict[str, Any]) -> List[types.Content]:
        """
        Drop an index from the database.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Result as text content
        """
        name = arguments.get("name")
        
        if not name:
            return [types.TextContent(type="text", text="Index name is required")]
            
        query = f"DROP INDEX {name}"
        
        try:
            self.db.run_write_query(query)
            return [types.TextContent(type="text", text=f"Index {name} dropped successfully")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error dropping index: {str(e)}")]
            
    async def drop_constraint(self, arguments: Dict[str, Any]) -> List[types.Content]:
        """
        Drop a constraint from the database.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Result as text content
        """
        name = arguments.get("name")
        
        if not name:
            return [types.TextContent(type="text", text="Constraint name is required")]
            
        query = f"DROP CONSTRAINT {name}"
        
        try:
            self.db.run_write_query(query)
            return [types.TextContent(type="text", text=f"Constraint {name} dropped successfully")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error dropping constraint: {str(e)}")]
            
    async def get_sample_data(self, arguments: Dict[str, Any]) -> List[types.Content]:
        """
        Get sample data for each node label in the database.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Sample data as text content
        """
        limit = arguments.get("limit", 10)
        specific_labels = arguments.get("labels", [])
        
        if specific_labels:
            sample_data = {}
            for label in specific_labels:
                query = f"""
                MATCH (n:{label})
                RETURN n
                LIMIT {limit}
                """
                
                with self.db.get_session() as session:
                    result = session.run(query)
                    sample_data[label] = [record["n"] for record in result]
        else:
            sample_data = self.db.get_sample_data(limit)
            
        return [types.TextContent(type="text", text=json.dumps(sample_data, indent=2))]
        
    async def find_nodes(self, arguments: Dict[str, Any]) -> List[types.Content]:
        """
        Find nodes in the database based on label and property conditions.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Nodes as text content
        """
        label = arguments.get("label")
        properties = arguments.get("properties", {})
        limit = arguments.get("limit", 10)
        
        if not label:
            return [types.TextContent(type="text", text="Node label is required")]
            
        # Build the query
        query = f"MATCH (n:{label})"
        
        # Add property conditions if provided
        if properties:
            conditions = []
            for key, value in properties.items():
                if isinstance(value, str):
                    conditions.append(f"n.{key} = '{value}'")
                else:
                    conditions.append(f"n.{key} = {value}")
                    
            if conditions:
                query += f" WHERE {' AND '.join(conditions)}"
                
        query += f" RETURN n LIMIT {limit}"
        
        try:
            results = self.db.run_query(query)
            return [types.TextContent(type="text", text=json.dumps(results, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error finding nodes: {str(e)}")]
            
    async def find_relationships(self, arguments: Dict[str, Any]) -> List[types.Content]:
        """
        Find relationships in the database based on type and property conditions.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Relationships as text content
        """
        rel_type = arguments.get("type")
        source_label = arguments.get("source_label")
        target_label = arguments.get("target_label")
        properties = arguments.get("properties", {})
        limit = arguments.get("limit", 10)
        
        if not rel_type:
            return [types.TextContent(type="text", text="Relationship type is required")]
            
        # Build the query
        source_pattern = f"(source{':' + source_label if source_label else ''})"
        target_pattern = f"(target{':' + target_label if target_label else ''})"
        rel_pattern = f"[r:{rel_type}]"
        
        query = f"MATCH {source_pattern}-{rel_pattern}->{target_pattern}"
        
        # Add property conditions if provided
        if properties:
            conditions = []
            for key, value in properties.items():
                if isinstance(value, str):
                    conditions.append(f"r.{key} = '{value}'")
                else:
                    conditions.append(f"r.{key} = {value}")
                    
            if conditions:
                query += f" WHERE {' AND '.join(conditions)}"
                
        query += f" RETURN source, r, target LIMIT {limit}"
        
        try:
            results = self.db.run_query(query)
            return [types.TextContent(type="text", text=json.dumps(results, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error finding relationships: {str(e)}")]
            
    async def find_paths(self, arguments: Dict[str, Any]) -> List[types.Content]:
        """
        Find paths between nodes in the database.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Paths as text content
        """
        start_label = arguments.get("start_label")
        start_properties = arguments.get("start_properties", {})
        end_label = arguments.get("end_label")
        end_properties = arguments.get("end_properties", {})
        max_depth = arguments.get("max_depth", 3)
        limit = arguments.get("limit", 5)
        
        if not start_label or not end_label:
            return [types.TextContent(type="text", text="Start and end labels are required")]
            
        # Build start node conditions
        start_conditions = []
        for key, value in start_properties.items():
            if isinstance(value, str):
                start_conditions.append(f"start.{key} = '{value}'")
            else:
                start_conditions.append(f"start.{key} = {value}")
                
        # Build end node conditions
        end_conditions = []
        for key, value in end_properties.items():
            if isinstance(value, str):
                end_conditions.append(f"end.{key} = '{value}'")
            else:
                end_conditions.append(f"end.{key} = {value}")
                
        # Build the query
        query = f"""
        MATCH (start:{start_label}), (end:{end_label})
        WHERE {' AND '.join(start_conditions) if start_conditions else 'true'}
        AND {' AND '.join(end_conditions) if end_conditions else 'true'}
        MATCH path = (start)-[*1..{max_depth}]->(end)
        RETURN path
        LIMIT {limit}
        """
        
        try:
            with self.db.get_session() as session:
                result = session.run(query)
                
                paths = []
                for record in result:
                    path = record["path"]
                    path_data = {
                        "nodes": [dict(node.items()) for node in path.nodes],
                        "relationships": [dict(rel.items()) for rel in path.relationships],
                        "length": len(path.relationships)
                    }
                    paths.append(path_data)
                    
                return [types.TextContent(type="text", text=json.dumps(paths, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error finding paths: {str(e)}")]
            
    async def find_shortest_path(self, arguments: Dict[str, Any]) -> List[types.Content]:
        """
        Find the shortest path between two nodes.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Shortest path as text content
        """
        start_label = arguments.get("start_label")
        start_properties = arguments.get("start_properties", {})
        end_label = arguments.get("end_label")
        end_properties = arguments.get("end_properties", {})
        relationship_types = arguments.get("relationship_types", [])
        max_depth = arguments.get("max_depth", 5)
        
        if not start_label or not end_label:
            return [types.TextContent(type="text", text="Start and end labels are required")]
            
        # Build start node conditions
        start_conditions = []
        for key, value in start_properties.items():
            if isinstance(value, str):
                start_conditions.append(f"start.{key} = '{value}'")
            else:
                start_conditions.append(f"start.{key} = {value}")
                
        # Build end node conditions
        end_conditions = []
        for key, value in end_properties.items():
            if isinstance(value, str):
                end_conditions.append(f"end.{key} = '{value}'")
            else:
                end_conditions.append(f"end.{key} = {value}")
                
        # Build relationship pattern
        if relationship_types:
            rel_pattern = f"[*1..{max_depth}]"
        else:
            rel_types_str = "|".join(relationship_types)
            rel_pattern = f"[*1..{max_depth} r WHERE type(r) IN ['{rel_types_str}']]"
            
        # Build the query
        query = f"""
        MATCH (start:{start_label}), (end:{end_label})
        WHERE {' AND '.join(start_conditions) if start_conditions else 'true'}
        AND {' AND '.join(end_conditions) if end_conditions else 'true'}
        MATCH path = shortestPath((start)-{rel_pattern}->(end))
        RETURN path
        """
        
        try:
            with self.db.get_session() as session:
                result = session.run(query)
                record = result.single()
                
                if record:
                    path = record["path"]
                    path_data = {
                        "nodes": [dict(node.items()) for node in path.nodes],
                        "relationships": [dict(rel.items()) for rel in path.relationships],
                        "length": len(path.relationships)
                    }
                    return [types.TextContent(type="text", text=json.dumps(path_data, indent=2))]
                else:
                    return [types.TextContent(type="text", text="No path found")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error finding shortest path: {str(e)}")]
            
    async def find_all_paths(self, arguments: Dict[str, Any]) -> List[types.Content]:
        """
        Find all paths between two nodes.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            All paths as text content
        """
        start_label = arguments.get("start_label")
        start_properties = arguments.get("start_properties", {})
        end_label = arguments.get("end_label")
        end_properties = arguments.get("end_properties", {})
        relationship_types = arguments.get("relationship_types", [])
        max_depth = arguments.get("max_depth", 3)
        limit = arguments.get("limit", 5)
        
        if not start_label or not end_label:
            return [types.TextContent(type="text", text="Start and end labels are required")]
            
        # Build start node conditions
        start_conditions = []
        for key, value in start_properties.items():
            if isinstance(value, str):
                start_conditions.append(f"start.{key} = '{value}'")
            else:
                start_conditions.append(f"start.{key} = {value}")
                
        # Build end node conditions
        end_conditions = []
        for key, value in end_properties.items():
            if isinstance(value, str):
                end_conditions.append(f"end.{key} = '{value}'")
            else:
                end_conditions.append(f"end.{key} = {value}")
                
        # Build relationship pattern
        if relationship_types:
            rel_pattern = f"[*1..{max_depth}]"
        else:
            rel_types_str = "|".join(relationship_types)
            rel_pattern = f"[*1..{max_depth} r WHERE type(r) IN ['{rel_types_str}']]"
            
        # Build the query
        query = f"""
        MATCH (start:{start_label}), (end:{end_label})
        WHERE {' AND '.join(start_conditions) if start_conditions else 'true'}
        AND {' AND '.join(end_conditions) if end_conditions else 'true'}
        MATCH path = allShortestPaths((start)-{rel_pattern}->(end))
        RETURN path
        LIMIT {limit}
        """
        
        try:
            with self.db.get_session() as session:
                result = session.run(query)
                
                paths = []
                for record in result:
                    path = record["path"]
                    path_data = {
                        "nodes": [dict(node.items()) for node in path.nodes],
                        "relationships": [dict(rel.items()) for rel in path.relationships],
                        "length": len(path.relationships)
                    }
                    paths.append(path_data)
                    
                return [types.TextContent(type="text", text=json.dumps(paths, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error finding all paths: {str(e)}")]
            
    async def run(self):
        """
        Run the MCP server.
        """
        async with stdio_server() as (read_stream, write_stream):
            logger.info(f"Neo4j MCP server running on stdio")
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=self.server_name,
                    server_version=self.server_version,
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )
