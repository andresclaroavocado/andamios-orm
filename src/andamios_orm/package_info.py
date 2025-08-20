"""
Package information and structure validation for Andamios ORM
"""

from typing import List, Dict, Any
import importlib
import sys
from pathlib import Path

# Package structure definition
PACKAGE_STRUCTURE = {
    "andamios_orm": {
        "description": "Main package with all public API exports",
        "exports": [
            # Engine API
            "create_engine", "create_memory_engine", "create_file_engine", 
            "get_engine", "create_optimized_engine",
            # Session API  
            "sessionmaker", "AsyncSession", "get_session", "init_db",
            "session_scope", "transaction_scope", "SessionManager",
            # Database API
            "DatabaseInitializer", "initialize_database", "create_tables", 
            "drop_tables", "verify_database_schema",
            # Models API
            "Model", "Base", "Project", "Conversation", "Document", "Repository",
            # Exception API
            "AndamiosORMException", "ValidationError", "NotFoundError", 
            "DatabaseConnectionError", "DatabaseOperationError", "ConfigurationError",
            # Logging API
            "setup_logging", "get_logger",
            # SQLAlchemy convenience exports
            "Column", "Integer", "String", "Text", "DateTime", "Boolean", "JSON",
        ]
    },
    "andamios_orm.core": {
        "description": "Core ORM functionality - engine, session, database management",
        "modules": {
            "engine": "Database engine creation and management",
            "session": "Session management and async wrappers", 
            "database": "Database initialization and schema management"
        }
    },
    "andamios_orm.models": {
        "description": "Model definitions and base classes",
        "modules": {
            "base": "Base model class with Active Record pattern",
            "project": "Project model definition",
            "conversation": "Conversation model definition", 
            "document": "Document model definition",
            "repository": "Repository model definition"
        }
    },
    "andamios_orm.exceptions": {
        "description": "Exception classes for error handling"
    },
    "andamios_orm.logging": {
        "description": "Logging configuration and utilities"
    }
}

def get_package_info() -> Dict[str, Any]:
    """Get comprehensive package information."""
    try:
        from . import (
            __version__, __author__, __email__, __description__, 
            __url__, __license__, __all__
        )
        
        return {
            "name": "andamios-orm",
            "version": __version__,
            "author": __author__,
            "email": __email__, 
            "description": __description__,
            "url": __url__,
            "license": __license__,
            "exports": __all__,
            "structure": PACKAGE_STRUCTURE
        }
    except ImportError as e:
        return {"error": f"Failed to import package metadata: {e}"}

def validate_package_structure() -> Dict[str, Any]:
    """Validate that package structure matches expectations."""
    results = {
        "valid": True,
        "missing_modules": [],
        "missing_exports": [],
        "errors": []
    }
    
    # Check main package exports
    try:
        import andamios_orm
        expected_exports = PACKAGE_STRUCTURE["andamios_orm"]["exports"]
        actual_exports = dir(andamios_orm)
        
        missing = [exp for exp in expected_exports if exp not in actual_exports]
        if missing:
            results["missing_exports"].extend(missing)
            results["valid"] = False
            
    except ImportError as e:
        results["errors"].append(f"Cannot import main package: {e}")
        results["valid"] = False
    
    return results

def generate_api_documentation() -> str:
    """Generate API documentation string."""
    doc = "# Andamios ORM API Reference\n\n"
    
    info = get_package_info()
    if "error" in info:
        return f"Error generating documentation: {info['error']}"
    
    doc += f"Version: {info['version']}\n"
    doc += f"Description: {info['description']}\n\n"
    
    doc += "## API Structure\n\n"
    
    # Engine API
    doc += "### Engine API\n"
    doc += "Database engine creation and configuration:\n"
    engine_exports = [
        "create_engine", "create_memory_engine", "create_file_engine", 
        "get_engine", "create_optimized_engine"
    ]
    for export in engine_exports:
        doc += f"- `{export}`\n"
    doc += "\n"
    
    # Session API
    doc += "### Session API\n"
    doc += "Session management and transaction handling:\n"
    session_exports = [
        "sessionmaker", "AsyncSession", "get_session", "init_db",
        "session_scope", "transaction_scope", "SessionManager"
    ]
    for export in session_exports:
        doc += f"- `{export}`\n"
    doc += "\n"
    
    # Database API
    doc += "### Database API\n"
    doc += "Schema management and initialization:\n"
    db_exports = [
        "DatabaseInitializer", "initialize_database", "create_tables", 
        "drop_tables", "verify_database_schema"
    ]
    for export in db_exports:
        doc += f"- `{export}`\n"
    doc += "\n"
    
    # Models API
    doc += "### Models API\n"
    doc += "Active Record pattern and model definitions:\n"
    model_exports = ["Model", "Base", "Project", "Conversation", "Document", "Repository"]
    for export in model_exports:
        doc += f"- `{export}`\n"
    doc += "\n"
    
    return doc

if __name__ == "__main__":
    print("Andamios ORM Package Information")
    print("=" * 40)
    
    info = get_package_info()
    if "error" in info:
        print(f"Error: {info['error']}")
        sys.exit(1)
    
    print(f"Name: {info['name']}")
    print(f"Version: {info['version']}")
    print(f"Description: {info['description']}")
    print(f"Exports: {len(info['exports'])} items")
    
    print("\nValidating package structure...")
    validation = validate_package_structure()
    
    if validation["valid"]:
        print("✓ Package structure is valid")
    else:
        print("✗ Package structure issues found:")
        if validation["missing_exports"]:
            print(f"  Missing exports: {validation['missing_exports']}")
        if validation["errors"]:
            for error in validation["errors"]:
                print(f"  Error: {error}")