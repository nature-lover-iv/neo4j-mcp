#!/usr/bin/env python3
"""
Main entry point for the Neo4j MCP server.
"""
import os
import sys
import asyncio
import argparse
import logging

from custom_neo4j_mcp.core.server import Neo4jMCPServer
from custom_neo4j_mcp.utils.config import load_config
from custom_neo4j_mcp.utils.logging import setup_logging

def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Neo4j MCP Server")
    
    # Neo4j connection options
    parser.add_argument("--uri", help="Neo4j connection URI (e.g., bolt://localhost:7687)")
    parser.add_argument("--username", help="Neo4j username")
    parser.add_argument("--password", help="Neo4j password")
    parser.add_argument("--database", help="Neo4j database name")
    
    # Server options
    parser.add_argument("--server-name", help="MCP server name")
    parser.add_argument("--server-version", help="MCP server version")
    
    # Config options
    parser.add_argument("--config", help="Path to configuration file")
    
    # Logging options
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], 
                       help="Logging level")
    parser.add_argument("--log-file", help="Path to log file")
    
    return parser.parse_args()

async def run_server(config):
    """
    Run the Neo4j MCP server.
    
    Args:
        config: Configuration dictionary
    """
    # Create Neo4j MCP server
    server = Neo4jMCPServer(
        uri=config["neo4j"]["uri"],
        username=config["neo4j"]["username"],
        password=config["neo4j"]["password"],
        database=config["neo4j"]["database"],
        server_name=config["server"]["name"],
        server_version=config["server"]["version"]
    )
    
    # Run the server
    await server.run()

def main():
    """
    Main entry point.
    """
    # Parse command line arguments
    args = parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line arguments
    if args.uri:
        config["neo4j"]["uri"] = args.uri
    if args.username:
        config["neo4j"]["username"] = args.username
    if args.password:
        config["neo4j"]["password"] = args.password
    if args.database:
        config["neo4j"]["database"] = args.database
    if args.server_name:
        config["server"]["name"] = args.server_name
    if args.server_version:
        config["server"]["version"] = args.server_version
    if args.log_level:
        config["logging"]["level"] = args.log_level
    if args.log_file:
        config["logging"]["file"] = args.log_file
        
    # Set up logging
    log_level = getattr(logging, config["logging"]["level"])
    logger = setup_logging(level=log_level, log_file=config["logging"]["file"])
    
    # Log configuration
    logger.info(f"Starting Neo4j MCP server with configuration:")
    logger.info(f"  Neo4j URI: {config['neo4j']['uri']}")
    logger.info(f"  Neo4j username: {config['neo4j']['username']}")
    logger.info(f"  Neo4j database: {config['neo4j']['database'] or 'default'}")
    logger.info(f"  Server name: {config['server']['name']}")
    logger.info(f"  Server version: {config['server']['version']}")
    
    # Run the server
    try:
        asyncio.run(run_server(config))
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
