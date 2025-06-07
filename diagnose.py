#!/usr/bin/env python3
"""
Diagnostic script for Jinja2 HTML Language Server Extension
This script verifies that all components are properly installed and configured.
"""

import sys
import os
import subprocess
import json
import importlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# ANSI color codes
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color

def print_header(text: str):
    """Print a colored header."""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.WHITE}{text.center(60)}{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓{Colors.NC} {text}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}✗{Colors.NC} {text}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠{Colors.NC} {text}")

def print_info(text: str):
    """Print info message."""
    print(f"{Colors.CYAN}ℹ{Colors.NC} {text}")

def print_step(text: str):
    """Print step message."""
    print(f"{Colors.PURPLE}→{Colors.NC} {text}")

def check_python_version() -> Tuple[bool, str]:
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        return True, f"{version.major}.{version.minor}.{version.micro}"
    return False, f"{version.major}.{version.minor}.{version.micro}"

def check_required_packages() -> Dict[str, bool]:
    """Check if required Python packages are installed."""
    required_packages = [
        'pygls',
        'lsprotocol',
        'jinja2',
        'markupsafe',
        'bs4',  # beautifulsoup4 imports as bs4
        'html5lib',
        'regex'
    ]

    results = {}
    for package in required_packages:
        try:
            importlib.import_module(package)
            results[package] = True
        except ImportError:
            results[package] = False

    return results

def check_extension_files() -> Dict[str, bool]:
    """Check if all required extension files exist."""
    base_path = Path(__file__).parent
    required_files = {
        'extension.toml': base_path / 'extension.toml',
        'language config': base_path / 'languages' / 'jinja2_html' / 'config.toml',
        'grammar file': base_path / 'grammars' / 'jinja2_html' / 'grammar.json',
        'main server': base_path / 'server' / 'main.py',
        'completion provider': base_path / 'server' / 'completion_provider.py',
        'emmet support': base_path / 'server' / 'emmet_support.py',
        'requirements.txt': base_path / 'server' / 'requirements.txt',
        'setup.py': base_path / 'server' / 'setup.py'
    }

    results = {}
    for name, path in required_files.items():
        results[name] = path.exists()

    return results

def validate_extension_manifest() -> Tuple[bool, List[str]]:
    """Validate the extension manifest file."""
    base_path = Path(__file__).parent
    manifest_path = base_path / 'extension.toml'

    if not manifest_path.exists():
        return False, ["extension.toml not found"]

    try:
        # Basic validation - check if file can be read
        with open(manifest_path, 'r') as f:
            content = f.read()

        issues = []
        required_keys = ['id', 'name', 'description', 'version', 'schema_version']

        for key in required_keys:
            if f'{key} = ' not in content:
                issues.append(f"Missing required field: {key}")

        if 'language_servers.jinja2_html_lsp' not in content:
            issues.append("Missing language server configuration")

        # Language configuration is in a separate file for this project structure
        # So we'll skip this check as it's not in the extension.toml

        return len(issues) == 0, issues

    except Exception as e:
        return False, [f"Error reading manifest: {str(e)}"]

def validate_grammar_file() -> Tuple[bool, List[str]]:
    """Validate the TextMate grammar file."""
    base_path = Path(__file__).parent
    grammar_path = base_path / 'grammars' / 'jinja2_html' / 'grammar.json'

    if not grammar_path.exists():
        return False, ["grammar.json not found"]

    try:
        with open(grammar_path, 'r') as f:
            grammar = json.load(f)

        issues = []
        required_keys = ['name', 'scopeName', 'fileTypes', 'patterns', 'repository']

        for key in required_keys:
            if key not in grammar:
                issues.append(f"Missing required field: {key}")

        if 'jinja-expression' not in grammar.get('repository', {}):
            issues.append("Missing Jinja2 expression patterns")

        if 'jinja-statement' not in grammar.get('repository', {}):
            issues.append("Missing Jinja2 statement patterns")

        return len(issues) == 0, issues

    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {str(e)}"]
    except Exception as e:
        return False, [f"Error reading grammar: {str(e)}"]

def test_language_server() -> Tuple[bool, List[str]]:
    """Test if the language server can be imported and initialized."""
    base_path = Path(__file__).parent
    server_path = base_path / 'server'

    # Add server directory to Python path
    sys.path.insert(0, str(server_path))

    try:
        # Test imports
        from main import Jinja2HTMLLanguageServer
        from completion_provider import Jinja2HTMLCompletionProvider
        from emmet_support import EmmetExpander, JinjaEmmetIntegration

        # Test basic initialization
        server = Jinja2HTMLLanguageServer()
        provider = Jinja2HTMLCompletionProvider()
        emmet = EmmetExpander()

        # Test basic functionality
        test_line = '<div class="test">'
        request = provider.analyze_completion_context(test_line, len(test_line))

        # Test Emmet expansion
        emmet_result = emmet.expand('div.test')

        issues = []

        if not hasattr(server, 'completion_provider'):
            issues.append("Server missing completion provider")

        if not hasattr(provider, 'html_tags'):
            issues.append("Completion provider missing HTML tags")

        if not emmet_result:
            issues.append("Emmet expansion failed")

        return len(issues) == 0, issues

    except ImportError as e:
        return False, [f"Import error: {str(e)}"]
    except Exception as e:
        return False, [f"Runtime error: {str(e)}"]
    finally:
        # Remove server path from Python path
        if str(server_path) in sys.path:
            sys.path.remove(str(server_path))

def check_zed_installation() -> Tuple[bool, str]:
    """Check if Zed IDE is installed."""
    try:
        result = subprocess.run(['zed', '--version'],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, "Zed command failed"
    except subprocess.TimeoutExpired:
        return False, "Zed command timed out"
    except FileNotFoundError:
        return False, "Zed command not found"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_zed_extensions_dir() -> Optional[Path]:
    """Get the Zed extensions directory path."""
    if sys.platform == "darwin":  # macOS
        return Path.home() / ".config" / "zed" / "extensions"
    elif sys.platform.startswith("linux"):  # Linux
        return Path.home() / ".config" / "zed" / "extensions"
    elif sys.platform.startswith("win"):  # Windows
        return Path(os.environ.get('APPDATA', '')) / "Zed" / "extensions"
    else:
        return Path.home() / ".config" / "zed" / "extensions"

def check_extension_installation() -> Tuple[bool, str]:
    """Check if the extension is installed in Zed."""
    extensions_dir = get_zed_extensions_dir()
    if not extensions_dir:
        return False, "Could not determine Zed extensions directory"

    extension_dir = extensions_dir / "jinja2-html"

    if not extension_dir.exists():
        return False, f"Extension not installed in {extension_dir}"

    # Check if essential files exist in the installed extension
    required_files = ['extension.toml', 'server/main.py']
    missing_files = []

    for file_name in required_files:
        if not (extension_dir / file_name).exists():
            missing_files.append(file_name)

    if missing_files:
        return False, f"Missing files in installation: {', '.join(missing_files)}"

    return True, str(extension_dir)

def generate_sample_config() -> str:
    """Generate a sample Zed configuration."""
    config = {
        "languages": {
            "Jinja2 HTML": {
                "language_servers": ["jinja2-html-lsp"],
                "format_on_save": "on",
                "tab_size": 2,
                "hard_tabs": False
            }
        },
        "lsp": {
            "jinja2-html-lsp": {
                "binary": {
                    "path": "python",
                    "arguments": ["-m", "server.main"]
                },
                "settings": {
                    "jinja2": {
                        "enable_emmet": True,
                        "enable_jinja_snippets": True,
                        "auto_close_tags": True
                    }
                }
            }
        }
    }

    return json.dumps(config, indent=2)

def run_comprehensive_test() -> Tuple[bool, List[str]]:
    """Run a comprehensive functionality test."""
    base_path = Path(__file__).parent
    server_path = base_path / 'server'
    sys.path.insert(0, str(server_path))

    try:
        from completion_provider import Jinja2HTMLCompletionProvider
        from emmet_support import emmet_integration

        provider = Jinja2HTMLCompletionProvider()
        issues = []

        # Test HTML completion
        html_request = provider.analyze_completion_context('<div', 4)
        html_completions = provider.provide_completions(html_request)

        if not html_completions:
            issues.append("No HTML completions found")

        # Test Jinja2 completion
        jinja_request = provider.analyze_completion_context('{{ user.', 7)
        jinja_completions = provider.provide_completions(jinja_request, "{{ user.name }}")

        # Test Emmet expansion
        emmet_result = emmet_integration.expand_with_jinja_context('div.container>div.row')

        if not emmet_result:
            issues.append("Emmet expansion failed")

        # Test variable extraction
        test_template = """
        {% for user in users %}
            <div>{{ user.name|title }}</div>
        {% endfor %}
        """

        variables = provider._extract_variables(test_template)
        if 'user' not in variables or 'users' not in variables:
            issues.append("Variable extraction failed")

        return len(issues) == 0, issues

    except Exception as e:
        return False, [f"Test error: {str(e)}"]
    finally:
        if str(server_path) in sys.path:
            sys.path.remove(str(server_path))

def main():
    """Run all diagnostic checks."""
    print_header("Jinja2 HTML Language Server Diagnostics")

    # Python version check
    print_step("Checking Python version...")
    py_ok, py_version = check_python_version()
    if py_ok:
        print_success(f"Python {py_version} (compatible)")
    else:
        print_error(f"Python {py_version} (requires 3.8+)")

    # Package dependencies
    print_step("Checking Python packages...")
    packages = check_required_packages()
    missing_packages = [pkg for pkg, installed in packages.items() if not installed]

    if not missing_packages:
        print_success("All required packages installed")
    else:
        print_error(f"Missing packages: {', '.join(missing_packages)}")
        print_info("Install with: pip install " + " ".join(missing_packages))

    # Extension files
    print_step("Checking extension files...")
    files = check_extension_files()
    missing_files = [name for name, exists in files.items() if not exists]

    if not missing_files:
        print_success("All extension files present")
    else:
        print_error(f"Missing files: {', '.join(missing_files)}")

    # Extension manifest validation
    print_step("Validating extension manifest...")
    manifest_ok, manifest_issues = validate_extension_manifest()
    if manifest_ok:
        print_success("Extension manifest is valid")
    else:
        print_error("Extension manifest issues:")
        for issue in manifest_issues:
            print(f"  - {issue}")

    # Grammar file validation
    print_step("Validating grammar file...")
    grammar_ok, grammar_issues = validate_grammar_file()
    if grammar_ok:
        print_success("Grammar file is valid")
    else:
        print_error("Grammar file issues:")
        for issue in grammar_issues:
            print(f"  - {issue}")

    # Language server test
    print_step("Testing language server...")
    if not missing_packages:  # Only test if packages are available
        server_ok, server_issues = test_language_server()
        if server_ok:
            print_success("Language server components working")
        else:
            print_error("Language server issues:")
            for issue in server_issues:
                print(f"  - {issue}")
    else:
        print_warning("Skipping language server test (missing packages)")
        server_ok = False

    # Zed installation check
    print_step("Checking Zed IDE installation...")
    zed_ok, zed_info = check_zed_installation()
    if zed_ok:
        print_success(f"Zed IDE found: {zed_info}")
    else:
        print_warning(f"Zed IDE: {zed_info}")

    # Extension installation check
    print_step("Checking extension installation...")
    ext_ok, ext_info = check_extension_installation()
    if ext_ok:
        print_success(f"Extension installed: {ext_info}")
    else:
        print_warning(f"Extension: {ext_info}")

    # Comprehensive functionality test
    if not missing_packages and manifest_ok and grammar_ok:
        print_step("Running comprehensive functionality test...")
        test_ok, test_issues = run_comprehensive_test()
        if test_ok:
            print_success("All functionality tests passed")
        else:
            print_error("Functionality test issues:")
            for issue in test_issues:
                print(f"  - {issue}")
    else:
        print_warning("Skipping functionality test (prerequisites not met)")
        test_ok = False

    # Summary
    print_header("Diagnostic Summary")

    all_checks = [
        ("Python Version", py_ok),
        ("Required Packages", not missing_packages),
        ("Extension Files", not missing_files),
        ("Extension Manifest", manifest_ok),
        ("Grammar File", grammar_ok),
        ("Language Server", server_ok if not missing_packages else None),
        ("Zed IDE", zed_ok),
        ("Extension Installation", ext_ok),
        ("Functionality Test", test_ok if not missing_packages else None)
    ]

    for check_name, status in all_checks:
        if status is True:
            print_success(check_name)
        elif status is False:
            print_error(check_name)
        else:
            print_warning(f"{check_name} (skipped)")

    # Recommendations
    print_header("Recommendations")

    if not py_ok:
        print_info("1. Upgrade to Python 3.8 or later")

    if missing_packages:
        print_info("2. Install missing packages:")
        print(f"   pip install {' '.join(missing_packages)}")

    if missing_files:
        print_info("3. Ensure all extension files are present")

    if not ext_ok:
        print_info("4. Install the extension:")
        print("   Run: ./install.sh")

    if not zed_ok:
        print_info("5. Install Zed IDE from https://zed.dev/")

    # Generate sample config
    print_header("Sample Zed Configuration")
    print("Add this to your Zed settings.json:")
    print()
    print(generate_sample_config())

    # Final status
    all_critical_ok = py_ok and not missing_packages and not missing_files and manifest_ok and grammar_ok

    print()
    if all_critical_ok:
        print_success("✓ Extension is ready for use!")
        if not ext_ok:
            print_info("Run './install.sh' to install in Zed")
    else:
        print_error("✗ Extension has issues that need to be resolved")
        print_info("Fix the issues above and run diagnostics again")

    return 0 if all_critical_ok else 1

if __name__ == "__main__":
    sys.exit(main())
