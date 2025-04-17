"""
Neo4j database connection and management module.
"""
import os
import logging
from typing import Dict, List, Any, Optional, Union
from neo4j import GraphDatabase, Driver, Session, Result, Record

logger = logging.getLogger(__name__)

class Neo4jDatabase:
    """
    Neo4j database connection and management class.
    Handles connections, queries, and transactions with Neo4j.
    """
    def __init__(
        self,
        uri: str = None,
        username: str = None,
        password: str = None,
        database: str = None
    ):
        """
        Initialize Neo4j database connection.
        
        Args:
            uri: Neo4j connection URI (e.g., bolt://localhost:7687)
            username: Neo4j username
            password: Neo4j password
            database: Neo4j database name (default: None, uses the default database)
        """
        self.uri = uri or os.environ.get("NEO4J_URL", "bolt://localhost:7687")
        self.username = username or os.environ.get("NEO4J_USERNAME", "neo4j")
        self.password = password or os.environ.get("NEO4J_PASSWORD", "")
        self.database = database or os.environ.get("NEO4J_DATABASE", None)
        
        self._driver = None
        self.connect()
        
    def connect(self) -> None:
        """
        Connect to Neo4j database.
        """
        try:
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password) if self.password else None
            )
            self.verify_connectivity()
            logger.info(f"Connected to Neo4j at {self.uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
            
    def verify_connectivity(self) -> None:
        """
        Verify connection to Neo4j database.
        """
        if self._driver:
            self._driver.verify_connectivity()
        
    def close(self) -> None:
        """
        Close Neo4j database connection.
        """
        if self._driver:
            self._driver.close()
            self._driver = None
            logger.info("Closed Neo4j connection")
            
    def get_session(self) -> Session:
        """
        Get a Neo4j session.
        
        Returns:
            Neo4j session
        """
        if not self._driver:
            self.connect()
            
        return self._driver.session(database=self.database)
        
    def run_query(
        self,
        query: str,
        params: Dict[str, Any] = None,
        database: str = None
    ) -> List[Dict[str, Any]]:
        """
        Run a Cypher query and return the results.
        
        Args:
            query: Cypher query
            params: Query parameters
            database: Database name (overrides the default)
            
        Returns:
            List of records as dictionaries
        """
        db = database or self.database
        with self._driver.session(database=db) as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]
            
    def run_write_query(
        self,
        query: str,
        params: Dict[str, Any] = None,
        database: str = None
    ) -> Dict[str, int]:
        """
        Run a write Cypher query and return the counters.
        
        Args:
            query: Cypher query
            params: Query parameters
            database: Database name (overrides the default)
            
        Returns:
            Dictionary with counters (nodes_created, relationships_created, etc.)
        """
        db = database or self.database
        with self._driver.session(database=db) as session:
            result = session.run(query, params or {})
            summary = result.consume()
            counters = summary.counters
            
            return {
                "nodes_created": counters.nodes_created,
                "nodes_deleted": counters.nodes_deleted,
                "relationships_created": counters.relationships_created,
                "relationships_deleted": counters.relationships_deleted,
                "properties_set": counters.properties_set,
                "labels_added": counters.labels_added,
                "labels_removed": counters.labels_removed,
                "indexes_added": counters.indexes_added,
                "indexes_removed": counters.indexes_removed,
                "constraints_added": counters.constraints_added,
                "constraints_removed": counters.constraints_removed
            }
            
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the database schema.
        
        Returns:
            Dictionary with schema information
        """
        try:
            # Try to use APOC if available
            query = """
            CALL apoc.meta.schema() YIELD value
            RETURN value
            """
            
            with self.get_session() as session:
                try:
                    result = session.run(query)
                    record = result.single()
                    if record:
                        return record["value"]
                    return {}
                except Exception as e:
                    # APOC procedure not found or other error
                    logger.info(f"APOC not available, using basic schema: {e}")
                    return self.get_basic_schema()
                
        except Exception as e:
            # Fall back to basic schema information
            logger.info(f"Error getting schema, using basic schema: {e}")
            return self.get_basic_schema()
            
    def get_basic_schema(self) -> Dict[str, Any]:
        """
        Get basic schema information without APOC.
        
        Returns:
            Dictionary with basic schema information
        """
        schema = {
            "nodes": {},
            "relationships": []
        }
        
        # Get node labels and properties
        node_query = """
        CALL db.labels() YIELD label
        RETURN label
        """
        
        with self.get_session() as session:
            # Get node labels
            labels = session.run(node_query)
            
            for label_record in labels:
                label = label_record["label"]
                schema["nodes"][label] = {"properties": {}}
                
                # Get properties for this label
                prop_query = f"""
                MATCH (n:{label})
                UNWIND keys(n) AS property
                RETURN DISTINCT property
                """
                
                properties = session.run(prop_query)
                for prop_record in properties:
                    prop = prop_record["property"]
                    schema["nodes"][label]["properties"][prop] = {"type": "unknown"}
            
            # Get relationship types
            rel_query = """
            CALL db.relationshipTypes() YIELD relationshipType
            RETURN relationshipType
            """
            
            rel_types = session.run(rel_query)
            
            for rel_record in rel_types:
                rel_type = rel_record["relationshipType"]
                
                # Get source and target node labels for this relationship type
                rel_details_query = f"""
                MATCH (source)-[r:{rel_type}]->(target)
                RETURN DISTINCT labels(source) AS source_labels, labels(target) AS target_labels
                LIMIT 5
                """
                
                rel_details = session.run(rel_details_query)
                
                for detail_record in rel_details:
                    source_labels = detail_record["source_labels"]
                    target_labels = detail_record["target_labels"]
                    
                    for source_label in source_labels:
                        for target_label in target_labels:
                            schema["relationships"].append({
                                "type": rel_type,
                                "source": source_label,
                                "target": target_label
                            })
        
        return schema
        
    def get_database_info(self) -> Dict[str, Any]:
        """
        Get information about the Neo4j database.
        
        Returns:
            Dictionary with database information
        """
        info = {
            "version": None,
            "edition": None,
            "database_name": self.database,
            "address": self.uri
        }
        
        try:
            query = "CALL dbms.components() YIELD name, versions, edition RETURN name, versions, edition"
            with self.get_session() as session:
                result = session.run(query)
                record = result.single()
                if record:
                    info["version"] = record["versions"][0]
                    info["edition"] = record["edition"]
        except Exception as e:
            logger.warning(f"Could not get database version: {e}")
            
        return info
        
    def get_node_count(self) -> int:
        """
        Get the total number of nodes in the database.
        
        Returns:
            Number of nodes
        """
        query = "MATCH (n) RETURN count(n) as count"
        with self.get_session() as session:
            result = session.run(query)
            record = result.single()
            return record["count"] if record else 0
            
    def get_relationship_count(self) -> int:
        """
        Get the total number of relationships in the database.
        
        Returns:
            Number of relationships
        """
        query = "MATCH ()-[r]->() RETURN count(r) as count"
        with self.get_session() as session:
            result = session.run(query)
            record = result.single()
            return record["count"] if record else 0
            
    def get_node_labels(self) -> List[str]:
        """
        Get all node labels in the database.
        
        Returns:
            List of node labels
        """
        query = "CALL db.labels() YIELD label RETURN label"
        with self.get_session() as session:
            result = session.run(query)
            return [record["label"] for record in result]
            
    def get_relationship_types(self) -> List[str]:
        """
        Get all relationship types in the database.
        
        Returns:
            List of relationship types
        """
        query = "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType"
        with self.get_session() as session:
            result = session.run(query)
            return [record["relationshipType"] for record in result]
            
    def get_property_keys(self) -> List[str]:
        """
        Get all property keys in the database.
        
        Returns:
            List of property keys
        """
        query = "CALL db.propertyKeys() YIELD propertyKey RETURN propertyKey"
        with self.get_session() as session:
            result = session.run(query)
            return [record["propertyKey"] for record in result]
            
    def get_indexes(self) -> List[Dict[str, Any]]:
        """
        Get all indexes in the database.
        
        Returns:
            List of indexes
        """
        try:
            # Neo4j 4.x+
            query = """
            SHOW INDEXES YIELD name, labelsOrTypes, properties, type, uniqueness
            RETURN name, labelsOrTypes, properties, type, uniqueness
            """
            with self.get_session() as session:
                result = session.run(query)
                return [record.data() for record in result]
        except Exception:
            # Fallback for older versions
            try:
                query = "CALL db.indexes() YIELD description, label, properties RETURN description, label, properties"
                with self.get_session() as session:
                    result = session.run(query)
                    return [record.data() for record in result]
            except Exception as e:
                logger.warning(f"Could not get indexes: {e}")
                return []
                
    def get_constraints(self) -> List[Dict[str, Any]]:
        """
        Get all constraints in the database.
        
        Returns:
            List of constraints
        """
        try:
            # Neo4j 4.x+
            query = """
            SHOW CONSTRAINTS YIELD name, labelsOrTypes, properties, type
            RETURN name, labelsOrTypes, properties, type
            """
            with self.get_session() as session:
                result = session.run(query)
                return [record.data() for record in result]
        except Exception:
            # Fallback for older versions
            try:
                query = "CALL db.constraints() YIELD description RETURN description"
                with self.get_session() as session:
                    result = session.run(query)
                    return [record.data() for record in result]
            except Exception as e:
                logger.warning(f"Could not get constraints: {e}")
                return []
                
    def get_sample_data(self, limit: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get sample data for each node label.
        
        Args:
            limit: Maximum number of nodes per label
            
        Returns:
            Dictionary with node labels as keys and lists of nodes as values
        """
        sample_data = {}
        
        labels = self.get_node_labels()
        
        for label in labels:
            query = f"""
            MATCH (n:{label})
            RETURN n
            LIMIT {limit}
            """
            
            with self.get_session() as session:
                result = session.run(query)
                sample_data[label] = [record["n"] for record in result]
                
        return sample_data
