#!/bin/bash

# Jinja2 HTML Language Server for Zed IDE - Installation Script
# This script automates the installation process for the extension

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Get OS type
get_os() {
    case "$(uname -s)" in
        Darwin*) echo "macos" ;;
        Linux*) echo "linux" ;;
        CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
        *) echo "unknown" ;;
    esac
}

# Get Zed extensions directory
get_zed_extensions_dir() {
    local os=$(get_os)
    case $os in
        macos)
            echo "$HOME/.config/zed/extensions"
            ;;
        linux)
            echo "$HOME/.config/zed/extensions"
            ;;
        windows)
            echo "$APPDATA/Zed/extensions"
            ;;
        *)
            echo "$HOME/.config/zed/extensions"
            ;;
    esac
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check Python
    if ! command_exists python3 && ! command_exists python; then
        print_error "Python 3.8+ is required but not found. Please install Python first."
        print_info "Visit: https://www.python.org/downloads/"
        exit 1
    fi
    
    # Check Python version
    if command_exists python3; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        print_error "Python 3.8+ is required. Found version: $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION found"
    
    # Check pip
    if ! command_exists pip3 && ! command_exists pip; then
        print_error "pip is required but not found. Please install pip first."
        exit 1
    fi
    
    if command_exists pip3; then
        PIP_CMD="pip3"
    else
        PIP_CMD="pip"
    fi
    
    print_success "pip found"
    
    # Check if Zed is installed
    if ! command_exists zed; then
        print_warning "Zed IDE command not found in PATH."
        print_info "Please make sure Zed IDE is installed and accessible."
        print_info "Visit: https://zed.dev/"
    else
        print_success "Zed IDE found"
    fi
}

# Install Python dependencies
install_python_deps() {
    print_info "Installing Python dependencies..."
    
    cd server/
    
    # Install in virtual environment if available
    if [ -d "venv" ] || [ -d ".venv" ]; then
        print_info "Virtual environment detected, activating..."
        if [ -d "venv" ]; then
            source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
        else
            source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null
        fi
    fi
    
    # Upgrade pip first
    $PIP_CMD install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        $PIP_CMD install -r requirements.txt
        print_success "Dependencies installed from requirements.txt"
    else
        # Install core dependencies manually
        $PIP_CMD install pygls>=1.0.0 lsprotocol>=2023.0.0 jinja2>=3.1.0 markupsafe>=2.1.0
        print_success "Core dependencies installed"
    fi
    
    # Install package in development mode
    $PIP_CMD install -e .
    print_success "Language server package installed"
    
    cd ..
}

# Install Zed extension
install_zed_extension() {
    print_info "Installing Zed extension..."
    
    ZED_EXTENSIONS_DIR=$(get_zed_extensions_dir)
    EXTENSION_DIR="$ZED_EXTENSIONS_DIR/jinja2-html"
    
    # Create extensions directory if it doesn't exist
    mkdir -p "$ZED_EXTENSIONS_DIR"
    
    # Remove existing extension if present
    if [ -d "$EXTENSION_DIR" ]; then
        print_info "Removing existing extension..."
        rm -rf "$EXTENSION_DIR"
    fi
    
    # Copy extension files
    print_info "Copying extension files..."
    cp -r . "$EXTENSION_DIR"
    
    # Remove unnecessary files from extension directory
    cd "$EXTENSION_DIR"
    rm -f install.sh README.md example.html.j2
    rm -rf .git .gitignore
    
    print_success "Extension installed to: $EXTENSION_DIR"
}

# Create virtual environment
create_virtualenv() {
    if [ "$1" = "--venv" ]; then
        print_info "Creating virtual environment..."
        cd server/
        
        if command_exists python3; then
            python3 -m venv venv
        else
            python -m venv venv
        fi
        
        # Activate virtual environment
        source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
        
        print_success "Virtual environment created and activated"
        cd ..
        return 0
    fi
    return 1
}

# Test installation
test_installation() {
    print_info "Testing language server..."
    
    cd server/
    
    # Test if the server can start
    timeout 5s $PYTHON_CMD -c "
import sys
sys.path.insert(0, '.')
try:
    from main import main
    print('Language server can be imported successfully')
except ImportError as e:
    print(f'Import error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'Other error: {e}')
    sys.exit(1)
" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        print_success "Language server test passed"
    else
        print_warning "Language server test failed, but installation may still work"
    fi
    
    cd ..
}

# Generate Zed configuration
generate_zed_config() {
    print_info "Generating Zed configuration..."
    
    CONFIG_FILE="zed-settings.json"
    
    cat > "$CONFIG_FILE" << 'EOF'
{
  "languages": {
    "Jinja2 HTML": {
      "language_servers": ["jinja2-html-lsp"],
      "format_on_save": "on",
      "tab_size": 2,
      "hard_tabs": false,
      "preferred_line_length": 120
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
          "enable_emmet": true,
          "enable_jinja_snippets": true,
          "auto_close_tags": true,
          "validate_on_type": true,
          "completion_trigger_chars": ["<", "{", "%", "#", "."],
          "hover_documentation": true,
          "format_on_save": true
        }
      }
    }
  }
}
EOF
    
    print_success "Configuration saved to: $CONFIG_FILE"
    print_info "Copy the contents to your Zed settings.json file"
}

# Print usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help        Show this help message"
    echo "  --venv        Create and use virtual environment"
    echo "  --no-test     Skip testing the installation"
    echo "  --config-only Only generate Zed configuration"
    echo "  --uninstall   Uninstall the extension"
    echo ""
    echo "Examples:"
    echo "  $0                    # Standard installation"
    echo "  $0 --venv            # Install with virtual environment"
    echo "  $0 --config-only     # Generate configuration only"
    echo "  $0 --uninstall       # Remove the extension"
}

# Uninstall function
uninstall() {
    print_info "Uninstalling Jinja2 HTML Language Server..."
    
    ZED_EXTENSIONS_DIR=$(get_zed_extensions_dir)
    EXTENSION_DIR="$ZED_EXTENSIONS_DIR/jinja2-html"
    
    if [ -d "$EXTENSION_DIR" ]; then
        rm -rf "$EXTENSION_DIR"
        print_success "Extension removed from: $EXTENSION_DIR"
    else
        print_info "Extension not found in: $EXTENSION_DIR"
    fi
    
    print_info "Note: Python dependencies are not automatically removed."
    print_info "To remove them manually, run: pip uninstall pygls lsprotocol jinja2"
}

# Main installation function
main() {
    echo "=========================================="
    echo "  Jinja2 HTML Language Server for Zed"
    echo "=========================================="
    echo ""
    
    # Parse command line arguments
    SKIP_TEST=false
    CONFIG_ONLY=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help)
                usage
                exit 0
                ;;
            --venv)
                create_virtualenv "$1"
                shift
                ;;
            --no-test)
                SKIP_TEST=true
                shift
                ;;
            --config-only)
                CONFIG_ONLY=true
                shift
                ;;
            --uninstall)
                uninstall
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    if [ "$CONFIG_ONLY" = true ]; then
        generate_zed_config
        exit 0
    fi
    
    # Check if we're in the right directory
    if [ ! -f "extension.toml" ]; then
        print_error "This script must be run from the extension root directory"
        print_info "Make sure extension.toml is present in the current directory"
        exit 1
    fi
    
    # Run installation steps
    check_prerequisites
    install_python_deps
    install_zed_extension
    
    if [ "$SKIP_TEST" = false ]; then
        test_installation
    fi
    
    generate_zed_config
    
    echo ""
    print_success "Installation completed successfully!"
    echo ""
    print_info "Next steps:"
    echo "1. Copy the configuration from 'zed-settings.json' to your Zed settings"
    echo "2. Restart Zed IDE"
    echo "3. Open a .j2 or .jinja2 file to test the extension"
    echo ""
    print_info "For troubleshooting, check the README.md file"
    echo "Report issues at: https://github.com/yourusername/zed-jinja2-html/issues"
}

# Run main function
main "$@"