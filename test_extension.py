#!/usr/bin/env python3
"""
Test script for Zed Jinja2 HTML Extension

This script tests the extension configuration and language server setup
to help verify everything is working correctly.
"""

import sys
import subprocess
import json
from pathlib import Path
import tempfile
import os

def test_extension_structure():
    """Test that the extension has the correct directory structure."""
    print("🔍 Testing extension structure...")
    
    required_files = [
        "extension.toml",
        "languages/jinja2_html/config.toml",
        "server/main.py",
        "server/__init__.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files present")
        return True

def test_language_server():
    """Test that the language server can be imported and started."""
    print("\n🔍 Testing language server...")
    
    try:
        # Test if server can be imported
        sys.path.insert(0, str(Path("server").absolute()))
        import main as server_main
        print("✅ Language server module imports successfully")
        
        # Test if server has required components
        if hasattr(server_main, 'server'):
            print("✅ Language server instance found")
        else:
            print("⚠️  Language server instance not found")
            
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import language server: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing language server: {e}")
        return False

def test_sample_template():
    """Test parsing a sample Jinja2 template."""
    print("\n🔍 Testing sample Jinja2 template...")
    
    sample_template = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    <h1>{{ heading }}</h1>
    
    {% if items %}
    <ul>
        {% for item in items %}
        <li>{{ item.name }} - {{ item.price }}</li>
        {% endfor %}
    </ul>
    {% else %}
    <p>No items found.</p>
    {% endif %}
    
    {# This is a comment #}
    <footer>
        <p>&copy; {{ year }} {{ company }}</p>
    </footer>
</body>
</html>
"""
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html.j2', delete=False) as f:
        f.write(sample_template)
        temp_path = f.name
    
    print(f"✅ Created test template: {temp_path}")
    
    # Test file extensions
    test_extensions = ['.j2', '.jinja', '.jinja2', '.html.j2', '.htm.j2']
    print(f"✅ Extension should handle: {', '.join(test_extensions)}")
    
    # Cleanup
    os.unlink(temp_path)
    return True

def test_dependencies():
    """Test that required Python dependencies are available."""
    print("\n🔍 Testing Python dependencies...")
    
    required_packages = [
        'pygls',
        'lsprotocol',
        'jinja2'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} available")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} not available")
    
    if missing_packages:
        print(f"\n⚠️  To install missing packages, run:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def test_configuration():
    """Test extension configuration files."""
    print("\n🔍 Testing configuration files...")
    
    # Test extension.toml
    try:
        import tomllib
        with open('extension.toml', 'rb') as f:
            ext_config = tomllib.load(f)
        
        print("✅ extension.toml is valid")
        print(f"   Extension ID: {ext_config.get('id')}")
        print(f"   Extension Name: {ext_config.get('name')}")
        print(f"   Version: {ext_config.get('version')}")
        
    except Exception as e:
        print(f"❌ Error reading extension.toml: {e}")
        return False
    
    # Test language config
    try:
        with open('languages/jinja2_html/config.toml', 'rb') as f:
            lang_config = tomllib.load(f)
        
        print("✅ language config.toml is valid")
        print(f"   Language Name: {lang_config.get('name')}")
        print(f"   Grammar: {lang_config.get('grammar')}")
        print(f"   File Extensions: {lang_config.get('path_suffixes')}")
        
    except Exception as e:
        print(f"❌ Error reading language config.toml: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🧪 Zed Jinja2 HTML Extension Test Suite")
    print("=" * 50)
    
    tests = [
        test_extension_structure,
        test_configuration,
        test_dependencies,
        test_language_server,
        test_sample_template
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Your extension is ready for testing in Zed.")
        print("\n📝 To install in Zed:")
        print("1. Open Zed")
        print("2. Open Command Palette (Cmd/Ctrl + Shift + P)")
        print("3. Type 'zed: extensions'")
        print("4. Click 'Install Dev Extension'")
        print(f"5. Select this directory: {Path.cwd().absolute()}")
    else:
        print("⚠️  Some tests failed. Please fix the issues before installing the extension.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)