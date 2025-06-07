#!/usr/bin/env python3
"""
TOML Validation Script for Zed Extensions

This script validates the extension.toml file and provides detailed error reporting
to help debug issues with Zed extension configuration.
"""

import sys
import tomllib
from pathlib import Path

def validate_extension_toml(toml_path="extension.toml"):
    """Validate the extension.toml file and report any issues."""
    
    toml_file = Path(toml_path)
    
    if not toml_file.exists():
        print(f"❌ Error: {toml_path} not found!")
        return False
    
    try:
        with open(toml_file, 'rb') as f:
            data = tomllib.load(f)
        
        print(f"✅ {toml_path} is syntactically valid TOML")
        
        # Check required fields for Zed extensions
        required_fields = ['id', 'name', 'version', 'schema_version', 'authors', 'description']
        missing_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"⚠️  Warning: Missing required fields: {', '.join(missing_fields)}")
        else:
            print("✅ All required fields present")
        
        # Validate specific sections
        if 'language_servers' in data:
            print(f"✅ Found {len(data['language_servers'])} language server(s)")
            for name, config in data['language_servers'].items():
                print(f"   - {name}: {config.get('name', 'No name')}")
        
        if 'grammars' in data:
            print(f"✅ Found {len(data['grammars'])} grammar(s)")
            for name, config in data['grammars'].items():
                if 'repository' in config and 'rev' in config:
                    print(f"   - {name}: {config['repository']} @ {config['rev']}")
                elif 'path' in config:
                    print(f"   - {name}: local path {config['path']}")
                else:
                    print(f"   - {name}: ⚠️  Missing repository/rev or path")
        
        # Check for languages directory
        languages_dir = Path("languages")
        if languages_dir.exists():
            language_dirs = [d for d in languages_dir.iterdir() if d.is_dir()]
            print(f"✅ Found {len(language_dirs)} language(s) in languages/ directory")
            for lang_dir in language_dirs:
                config_file = lang_dir / "config.toml"
                if config_file.exists():
                    print(f"   - {lang_dir.name}: config.toml found")
                    try:
                        with open(config_file, 'rb') as f:
                            lang_config = tomllib.load(f)
                        print(f"     Name: {lang_config.get('name', 'Unknown')}")
                        print(f"     Grammar: {lang_config.get('grammar', 'None')}")
                        print(f"     Extensions: {lang_config.get('path_suffixes', [])}")
                    except Exception as e:
                        print(f"     ❌ Error reading config.toml: {e}")
                else:
                    print(f"   - {lang_dir.name}: ❌ Missing config.toml")
        else:
            print("ℹ️  No languages/ directory found")
        
        print("\n📋 Full parsed structure:")
        print_dict(data, indent=0)
        
        return True
        
    except tomllib.TOMLDecodeError as e:
        print(f"❌ TOML Syntax Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def print_dict(d, indent=0):
    """Pretty print a dictionary with indentation."""
    for key, value in d.items():
        if isinstance(value, dict):
            print("  " * indent + f"{key}:")
            print_dict(value, indent + 1)
        elif isinstance(value, list):
            print("  " * indent + f"{key}: {value}")
        else:
            print("  " * indent + f"{key}: {value}")

if __name__ == "__main__":
    toml_file = sys.argv[1] if len(sys.argv) > 1 else "extension.toml"
    
    print("🔍 Zed Extension TOML Validator")
    print("=" * 40)
    
    success = validate_extension_toml(toml_file)
    
    if success:
        print("\n✅ Validation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Validation failed!")
        sys.exit(1)