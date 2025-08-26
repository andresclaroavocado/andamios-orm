"""
Package information and structure for Andamios ORM

This module provides metadata about the package structure, exports, and documentation.
"""

from typing import Dict, List, Any, Optional
import importlib
import inspect
import sys
from pathlib import Path

# Package structure metadata
PACKAGE_STRUCTURE = {
    "andamios_orm": {
        "description": "A modern, async-first Python ORM library built for DuckDB",
        "exports": [
            "create_engine", "create_memory_engine", "create_file_engine", "get_engine", "create_optimized_engine",
            "sessionmaker", "AsyncSession", "get_session", "init_db", "session_scope", "transaction_scope", "SessionManager",
            "DatabaseInitializer", "initialize_database", "create_tables", "drop_tables", "verify_database_schema",
            "Model", "Base", "Project", "Conversation", "Document", "Repository",
            "AndamiosORMException", "ValidationError", "NotFoundError", "DatabaseConnectionError", 
            "DatabaseOperationError", "ConfigurationError", "TransactionError", "MigrationError", "QueryError",
            "setup_logging", "get_logger", "log_async_performance", "log_sync_performance", "log_context",
            "LoggingConfig", "DEVELOPMENT_CONFIG", "PRODUCTION_CONFIG", "TESTING_CONFIG",
            "Column", "Integer", "String", "Text", "DateTime", "Boolean", "JSON"
        ]
    },
    "andamios_orm.core": {
        "description": "Core ORM functionality",
        "modules": [
            "engine", "session", "database"
        ],
        "exports": [
            "create_engine", "create_memory_engine", "create_file_engine", "get_engine", "create_optimized_engine",
            "sessionmaker", "AsyncSession", "get_session", "init_db", "session_scope", "transaction_scope", "SessionManager",
            "DatabaseInitializer", "initialize_database", "create_tables", "drop_tables", "verify_database_schema"
        ],
        "module_exports": {
            "engine": ["create_engine", "create_memory_engine", "create_file_engine", "get_engine", "create_optimized_engine"],
            "session": ["sessionmaker", "AsyncSession", "get_session", "init_db", "session_scope", "transaction_scope", "SessionManager"],
            "database": ["DatabaseInitializer", "initialize_database", "create_tables", "drop_tables", "verify_database_schema"]
        }
    },
    "andamios_orm.models": {
        "description": "Model definitions and base classes",
        "modules": [
            "base", "project", "conversation", "document", "repository"
        ],
        "exports": [
            "Model", "Base", "Project", "Conversation", "Document", "Repository"
        ],
        "module_exports": {
            "base": ["Model", "Base"],
            "project": ["Project"],
            "conversation": ["Conversation"],
            "document": ["Document"],
            "repository": ["Repository"]
        }
    },
    "andamios_orm.exceptions": {
        "description": "Exception classes and error handling",
        "exports": [
            "AndamiosORMException", "ValidationError", "NotFoundError", "DatabaseConnectionError",
            "DatabaseOperationError", "ConfigurationError", "TransactionError", "MigrationError", "QueryError",
            "handle_database_error", "handle_validation_error", "handle_not_found_error"
        ]
    },
    "andamios_orm.logging": {
        "description": "Logging configuration and utilities",
        "exports": [
            "setup_logging", "get_logger", "log_async_performance", "log_sync_performance", "log_context",
            "LoggingConfig", "DEVELOPMENT_CONFIG", "PRODUCTION_CONFIG", "TESTING_CONFIG",
            "StructuredFormatter", "PerformanceLoggerAdapter", "AsyncLogHandler"
        ]
    }
}


def get_package_info(package_name: str = "andamios_orm") -> Dict[str, Any]:
    """
    Get comprehensive package information.
    
    Args:
        package_name: Name of the package to analyze
        
    Returns:
        Dictionary containing package information
    """
    try:
        # Import the package
        package = importlib.import_module(package_name)
        
        # Get basic info
        info = {
            "name": package_name,
            "version": getattr(package, "__version__", "unknown"),
            "description": getattr(package, "__description__", ""),
            "author": getattr(package, "__author__", ""),
            "email": getattr(package, "__email__", ""),
            "url": getattr(package, "__url__", ""),
            "license": getattr(package, "__license__", ""),
            "path": str(Path(package.__file__).parent) if hasattr(package, "__file__") else "",
        }
        
        # Get exports from __all__ if available
        if hasattr(package, "__all__"):
            info["exports"] = package.__all__
        else:
            # Fallback to public attributes
            info["exports"] = [name for name in dir(package) if not name.startswith("_")]
        
        # Get structure information
        if package_name in PACKAGE_STRUCTURE:
            info["structure"] = PACKAGE_STRUCTURE[package_name]
        
        # Get submodules
        if package_name in PACKAGE_STRUCTURE and "modules" in PACKAGE_STRUCTURE[package_name]:
            info["submodules"] = PACKAGE_STRUCTURE[package_name]["modules"]
        
        return info
        
    except ImportError as e:
        return {
            "name": package_name,
            "error": f"Failed to import package: {e}",
            "available": False
        }
    except Exception as e:
        return {
            "name": package_name,
            "error": f"Failed to get package info: {e}",
            "available": False
        }


def validate_package_structure(package_name: str = "andamios_orm") -> Dict[str, Any]:
    """
    Validate that the actual package structure matches the expected structure.
    
    Args:
        package_name: Name of the package to validate
        
    Returns:
        Dictionary containing validation results
    """
    results = {
        "valid": True,
        "missing_modules": [],
        "missing_exports": [],
        "unexpected_exports": [],
        "errors": []
    }
    
    try:
        if package_name not in PACKAGE_STRUCTURE:
            results["valid"] = False
            results["errors"].append(f"No structure definition found for {package_name}")
            return results
        
        expected = PACKAGE_STRUCTURE[package_name]
        
        # Check main package exports
        if "exports" in expected:
            try:
                package = importlib.import_module(package_name)
                actual_exports = set(getattr(package, "__all__", []))
                expected_exports = set(expected["exports"])
                
                results["missing_exports"] = list(expected_exports - actual_exports)
                results["unexpected_exports"] = list(actual_exports - expected_exports)
                
                if results["missing_exports"] or results["unexpected_exports"]:
                    results["valid"] = False
                    
            except ImportError as e:
                results["valid"] = False
                results["errors"].append(f"Failed to import {package_name}: {e}")
        
        # Check submodules
        if "modules" in expected:
            for module_name in expected["modules"]:
                full_module_name = f"{package_name}.{module_name}"
                try:
                    importlib.import_module(full_module_name)
                except ImportError:
                    results["valid"] = False
                    results["missing_modules"].append(module_name)
        
        return results
        
    except Exception as e:
        results["valid"] = False
        results["errors"].append(f"Validation failed: {e}")
        return results


def generate_api_documentation(package_name: str = "andamios_orm") -> str:
    """
    Generate API documentation for the package.
    
    Args:
        package_name: Name of the package to document
        
    Returns:
        String containing formatted documentation
    """
    try:
        package_info = get_package_info(package_name)
        
        if "error" in package_info:
            return f"Error generating documentation: {package_info['error']}"
        
        doc_lines = []
        doc_lines.append(f"# {package_info.get('name', package_name)} API Documentation")
        doc_lines.append("")
        
        if package_info.get("description"):
            doc_lines.append(f"**Description:** {package_info['description']}")
            doc_lines.append("")
        
        if package_info.get("version"):
            doc_lines.append(f"**Version:** {package_info['version']}")
        
        if package_info.get("author"):
            doc_lines.append(f"**Author:** {package_info['author']}")
        
        if package_info.get("license"):
            doc_lines.append(f"**License:** {package_info['license']}")
        
        doc_lines.append("")
        
        # Add exports section
        exports = package_info.get("exports", [])
        if exports:
            doc_lines.append("## Exports")
            doc_lines.append("")
            for export in sorted(exports):
                doc_lines.append(f"- `{export}`")
            doc_lines.append("")
        
        # Add structure section
        structure = package_info.get("structure", {})
        if structure and "modules" in structure:
            doc_lines.append("## Modules")
            doc_lines.append("")
            for module in structure["modules"]:
                doc_lines.append(f"### {module}")
                module_exports = structure.get("module_exports", {}).get(module, [])
                if module_exports:
                    for export in sorted(module_exports):
                        doc_lines.append(f"- `{export}`")
                doc_lines.append("")
        
        return "\n".join(doc_lines)
        
    except Exception as e:
        return f"Error generating documentation: {e}"


def get_module_info(module_name: str) -> Dict[str, Any]:
    """
    Get information about a specific module.
    
    Args:
        module_name: Full name of the module
        
    Returns:
        Dictionary containing module information
    """
    try:
        module = importlib.import_module(module_name)
        
        info = {
            "name": module_name,
            "file": getattr(module, "__file__", ""),
            "doc": getattr(module, "__doc__", ""),
            "functions": [],
            "classes": [],
            "constants": []
        }
        
        # Get all public attributes
        for name in dir(module):
            if name.startswith("_"):
                continue
                
            attr = getattr(module, name)
            
            if inspect.isfunction(attr):
                info["functions"].append({
                    "name": name,
                    "doc": getattr(attr, "__doc__", ""),
                    "signature": str(inspect.signature(attr)) if hasattr(inspect, "signature") else ""
                })
            elif inspect.isclass(attr):
                info["classes"].append({
                    "name": name,
                    "doc": getattr(attr, "__doc__", ""),
                    "methods": [method for method in dir(attr) if not method.startswith("_")]
                })
            elif not inspect.ismodule(attr):
                info["constants"].append({
                    "name": name,
                    "type": type(attr).__name__,
                    "value": str(attr) if len(str(attr)) < 100 else f"{str(attr)[:100]}..."
                })
        
        return info
        
    except ImportError as e:
        return {
            "name": module_name,
            "error": f"Failed to import module: {e}",
            "available": False
        }
    except Exception as e:
        return {
            "name": module_name,
            "error": f"Failed to get module info: {e}",
            "available": False
        }