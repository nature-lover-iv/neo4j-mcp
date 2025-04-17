#!/usr/bin/env python3
"""
Run all tests for the Neo4j MCP server.
"""
import os
import sys
import unittest
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_unit_tests():
    """
    Run the unit tests.
    """
    print("\n=== Running Unit Tests ===\n")
    
    # Discover and run all unit tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern="test_*.py", top_level_dir=start_dir)
    
    # Filter out integration tests
    filtered_suite = unittest.TestSuite()
    for test_suite in suite:
        # Check if this is the integration test module
        if not str(test_suite).startswith('test_integration'):
            filtered_suite.addTest(test_suite)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(filtered_suite)
    
    return result.wasSuccessful()


def run_integration_tests():
    """
    Run the integration tests.
    """
    print("\n=== Running Integration Tests ===\n")
    
    # Import the integration tests
    from tests.test_integration import TestNeo4jMCPServerIntegration
    
    # Run the tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestNeo4jMCPServerIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_mcp_tool_tests():
    """
    Run tests using the MCP tools directly.
    """
    print("\n=== Running MCP Tool Tests ===\n")
    
    # Import the necessary modules
    import json
    import asyncio
    from custom_neo4j_mcp.core.server import Neo4jMCPServer
    
    # Create the server
    server = Neo4jMCPServer(
        uri=os.environ.get("NEO4J_URL", "bolt://localhost:7687"),
        username=os.environ.get("NEO4J_USERNAME", "neo4j"),
        password=os.environ.get("NEO4J_PASSWORD", "ihorek12345")
    )
    
    # Define the test cases
    async def test_get_schema():
        print("Testing get_neo4j_schema tool...")
        result = await server.get_schema({"detailed": False})
        print(f"Result: {result[0].text}\n")
        return True
        
    async def test_read_query():
        print("Testing read_neo4j_cypher tool...")
        result = await server.execute_read_query({
            "query": "MATCH (n) RETURN count(n) as count"
        })
        print(f"Result: {result[0].text}\n")
        return True
        
    async def test_write_query():
        print("Testing write_neo4j_cypher tool...")
        # Create a test node
        result = await server.execute_write_query({
            "query": "CREATE (n:TestNode {name: 'Test', created: timestamp()})"
        })
        print(f"Result: {result[0].text}")
        
        # Verify the node was created
        result = await server.execute_read_query({
            "query": "MATCH (n:TestNode) RETURN n.name"
        })
        print(f"Verification: {result[0].text}")
        
        # Clean up
        result = await server.execute_write_query({
            "query": "MATCH (n:TestNode) DELETE n"
        })
        print(f"Cleanup: {result[0].text}\n")
        return True
        
    async def test_find_nodes():
        print("Testing find_nodes tool...")
        # Create some test nodes
        await server.execute_write_query({
            "query": """
            CREATE (alice:Person {name: 'Alice', age: 30})
            CREATE (bob:Person {name: 'Bob', age: 40})
            """
        })
        
        # Find the nodes
        result = await server.find_nodes({
            "label": "Person",
            "properties": {"name": "Alice"},
            "limit": 10
        })
        print(f"Result: {result[0].text}")
        
        # Clean up
        await server.execute_write_query({
            "query": "MATCH (n:Person) DELETE n"
        })
        print("Cleanup complete\n")
        return True
        
    async def test_database_statistics():
        print("Testing get_database_statistics tool...")
        result = await server.get_database_statistics({})
        print(f"Result: {result[0].text}\n")
        return True
        
    # Run the tests
    async def run_tests():
        tests = [
            test_get_schema,
            test_read_query,
            test_write_query,
            test_find_nodes,
            test_database_statistics
        ]
        
        results = []
        for test in tests:
            try:
                result = await test()
                results.append(result)
            except Exception as e:
                print(f"Error: {e}")
                results.append(False)
                
        return all(results)
        
    # Run the tests asynchronously
    result = asyncio.run(run_tests())
    
    return result


def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description="Run tests for the Neo4j MCP server")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--mcp", action="store_true", help="Run MCP tool tests only")
    args = parser.parse_args()
    
    # Determine which tests to run
    run_unit = args.unit or not (args.integration or args.mcp)
    run_integration = args.integration or not (args.unit or args.mcp)
    run_mcp = args.mcp or not (args.unit or args.integration)
    
    # Run the tests
    results = []
    
    if run_unit:
        results.append(run_unit_tests())
        
    if run_integration:
        results.append(run_integration_tests())
        
    if run_mcp:
        results.append(run_mcp_tool_tests())
        
    # Print the summary
    print("\n=== Test Summary ===\n")
    print(f"Unit Tests: {'Passed' if run_unit and results[0] else 'Failed' if run_unit else 'Not Run'}")
    print(f"Integration Tests: {'Passed' if run_integration and results[1 if run_unit else 0] else 'Failed' if run_integration else 'Not Run'}")
    print(f"MCP Tool Tests: {'Passed' if run_mcp and results[-1] else 'Failed' if run_mcp else 'Not Run'}")
    
    # Return the overall result
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
