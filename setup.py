from setuptools import setup, find_packages

setup(
    name="neo4j-mcp",
    version="0.1.0",
    description="Neo4j MCP Server - A comprehensive MCP server for Neo4j",
    author="Natuke Is King",
    url="https://github.com/nature-lover-iv/neo4j-mcp",
    packages=find_packages(),
    install_requires=[
        "neo4j>=5.0.0",
        "pydantic>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "neo4j-mcp=custom_neo4j_mcp.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires=">=3.9",
    license="MIT",
)
