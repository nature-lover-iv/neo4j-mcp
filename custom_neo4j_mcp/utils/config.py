"""
Configuration utilities for Neo4j MCP server.
"""
import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

DEFAULT_CONFIG = {
    "neo4j": {
        "uri": "bolt://localhost:7687",
        "username": "neo4j",
        "password": "",
        "database": None
    },
    "server": {
        "name": "neo4j-mcp-server",
        "version": "0.1.0"
    },
    "logging": {
        "level": "INFO",
        "file": None
    }
}

def get_config_path() -> str:
    """
    Get the path to the configuration file.
    
    Returns:
        Path to the configuration file
    """
    # Check for config file in the current directory
    if os.path.exists("config.json"):
        return "config.json"
        
    # Check for config file in the user's home directory
    home_config = os.path.join(os.path.expanduser("~"), ".neo4j-mcp", "config.json")
    if os.path.exists(home_config):
        return home_config
        
    # Check for config file in the system directory
    system_config = "/etc/neo4j-mcp/config.json"
    if os.path.exists(system_config):
        return system_config
        
    # Return the default config path in the user's home directory
    return home_config
    
def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.
    
    Args:
        config_path: Path to the configuration file (default: None, uses get_config_path())
        
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = get_config_path()
        
    # If the config file doesn't exist, create it with default values
    if not os.path.exists(config_path):
        # Create directory if it doesn't exist
        config_dir = os.path.dirname(config_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir)
            
        # Write default config to file
        with open(config_path, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
            
        return DEFAULT_CONFIG
        
    # Load config from file
    with open(config_path, "r") as f:
        config = json.load(f)
        
    # Merge with default config to ensure all keys are present
    merged_config = DEFAULT_CONFIG.copy()
    
    # Update neo4j config
    if "neo4j" in config:
        merged_config["neo4j"].update(config["neo4j"])
        
    # Update server config
    if "server" in config:
        merged_config["server"].update(config["server"])
        
    # Update logging config
    if "logging" in config:
        merged_config["logging"].update(config["logging"])
        
    return merged_config
    
def save_config(config: Dict[str, Any], config_path: Optional[str] = None) -> None:
    """
    Save configuration to a JSON file.
    
    Args:
        config: Configuration dictionary
        config_path: Path to the configuration file (default: None, uses get_config_path())
    """
    if config_path is None:
        config_path = get_config_path()
        
    # Create directory if it doesn't exist
    config_dir = os.path.dirname(config_path)
    if config_dir and not os.path.exists(config_dir):
        os.makedirs(config_dir)
        
    # Write config to file
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
