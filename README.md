# Jinja2 HTML Language Server for Zed IDE

A comprehensive Language Server Protocol (LSP) implementation for Jinja2 HTML templates in Zed IDE, providing intelligent auto-completion, syntax highlighting, diagnostics, and advanced Emmet snippet support.

## Features

### 🚀 Core Features
- **Intelligent Auto-completion**: Context-aware completions for HTML, Jinja2, and mixed content
- **Advanced Emmet Support**: Full Emmet abbreviation expansion with Jinja2 integration
- **Syntax Highlighting**: Rich syntax highlighting for Jinja2 templates with HTML
- **Real-time Diagnostics**: Validation and error detection for templates
- **Hover Information**: Detailed documentation on hover for Jinja2 filters, functions, and HTML elements

### 🎯 Jinja2 Features
- **Template Variables**: Auto-completion for context variables extracted from templates
- **Filters**: Complete set of built-in Jinja2 filters with documentation and argument hints
- **Functions**: Global functions like `range()`, `lipsum()`, `dict()`, etc.
- **Tests**: Built-in test functions for conditional logic
- **Control Structures**: `if/elif/else`, `for` loops, `block` definitions, template inheritance
- **Macros & Includes**: Support for template composition and reusability

### 🌐 HTML Features
- **HTML5 Elements**: Complete HTML5 tag library with smart snippets
- **Attributes**: Context-aware attribute suggestions based on current HTML element
- **CSS Classes & IDs**: Auto-completion for existing classes and IDs in your project
- **Form Elements**: Enhanced support for form controls with proper attributes

### ⚡ Emmet Integration
- **Standard Emmet**: Full support for Emmet abbreviations (`div.class#id`, `ul>li*5`, etc.)
- **Jinja2 Enhanced**: Special Jinja2-aware Emmet patterns (`j:form`, `j:table`, etc.)
- **Smart Snippets**: Context-aware snippet expansion based on current template state

## Installation

### Prerequisites
- **Zed IDE**: Latest version of Zed editor
- **Python 3.8+**: Required for the language server
- **pip**: Python package manager

### Step 1: Install Python Dependencies

Navigate to the server directory and install dependencies:

```bash
cd server/
pip install -r requirements.txt
```

Or install the package directly:

```bash
cd server/
pip install -e .
```

### Step 2: Install Zed Extension

1. **Manual Installation** (Development):
   ```bash
   # Copy the extension to Zed's extensions directory
   mkdir -p ~/.config/zed/extensions/
   cp -r zed-jinja2-html ~/.config/zed/extensions/
   ```

2. **From Extensions Registry** (When available):
   - Open Zed IDE
   - Go to Extensions panel (`Cmd/Ctrl + Shift + X`)
   - Search for "Jinja2 HTML"
   - Install the extension

### Step 3: Configuration

Add the following to your Zed `settings.json`:

```json
{
  "languages": {
    "Jinja2 HTML": {
      "language_servers": ["jinja2-html-lsp"],
      "format_on_save": "on",
      "tab_size": 2,
      "hard_tabs": false
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
          "auto_close_tags": true
        }
      }
    }
  }
}
```

## Usage

### File Extensions

The extension automatically activates for files with these extensions:
- `.j2`
- `.jinja`
- `.jinja2`
- `.html.j2`
- `.htm.j2`
- `.html.jinja`
- `.htm.jinja`
- `.html.jinja2`
- `.htm.jinja2`

### Basic Completion

#### Jinja2 Variables
```jinja2
{{ user.name }}     <!-- Variable completion -->
{{ users|length }}  <!-- Filter completion -->
{{ range(10) }}     <!-- Function completion -->
```

#### Control Structures
```jinja2
{% for item in items %}
    {{ item.name }}
{% endfor %}

{% if condition %}
    <!-- Content -->
{% endif %}
```

#### Template Inheritance
```jinja2
{% extends "base.html" %}
{% block content %}
    <!-- Block content -->
{% endblock %}
```

### Emmet Snippets

#### Standard HTML Emmet
```
div.container>div.row>div.col*3
```
Expands to:
```html
<div class="container">
    <div class="row">
        <div class="col"></div>
        <div class="col"></div>
        <div class="col"></div>
    </div>
</div>
```

#### Jinja2 Enhanced Emmet
```
j:form
```
Expands to:
```html
<form method="post">
    {{ csrf_token() }}
    
    <input type="submit" value="">
</form>
```

```
j:table
```
Expands to:
```html
{% for item in  %}
<tr>
    <td>{{ item. }}</td>
</tr>
{% endfor %}
```

### Available Snippets

#### Jinja2 Snippets
- `for` → `{% for item in items %}...{% endfor %}`
- `if` → `{% if condition %}...{% endif %}`
- `block` → `{% block name %}...{% endblock %}`
- `macro` → `{% macro name(args) %}...{% endmacro %}`
- `extend` → `{% extends "template.html" %}`
- `include` → `{% include "template.html" %}`
- `set` → `{% set var = value %}`
- `comment` → `{# comment #}`
- `var` → `{{ variable }}`
- `filter` → `{{ variable|filter }}`

#### HTML5 Snippets
- `html:5` → Complete HTML5 boilerplate
- `form` → Form with method and action
- `table` → Table with header and data rows
- `ul` → Unordered list with list items
- `nav` → Navigation structure

## Advanced Features

### Context-Aware Completions

The language server provides intelligent completions based on context:

1. **Inside Jinja2 expressions** (`{{ }}`): Variables, filters, functions
2. **Inside Jinja2 statements** (`{% %}`): Keywords, control structures, variables
3. **HTML context**: Tags, attributes, values
4. **CSS context**: Classes, IDs, style properties

### Variable Extraction

The server automatically extracts variables from your templates:
- Variables from `{{ variable }}` expressions
- Loop variables from `{% for var in items %}`
- Set variables from `{% set var = value %}`

### Error Detection

Real-time validation for:
- Unclosed Jinja2 blocks
- Invalid syntax
- Missing template inheritance
- Unclosed HTML tags

### Hover Documentation

Hover over Jinja2 elements to see:
- Filter descriptions and arguments
- Function signatures
- Keyword documentation
- HTML element information

## Development

### Project Structure
```
zed-jinja2-html/
├── extension.toml              # Zed extension manifest
├── languages/
│   └── jinja2-html.toml       # Language configuration
├── grammars/
│   └── jinja2-html/
│       └── grammar.json       # TextMate grammar
├── server/
│   ├── __init__.py
│   ├── main.py               # Main LSP server
│   ├── completion_provider.py # Completion logic
│   ├── emmet_support.py      # Emmet integration
│   ├── requirements.txt      # Python dependencies
│   └── setup.py             # Package setup
└── README.md
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Testing

Run the language server in development mode:

```bash
cd server/
python -m pytest tests/  # Run tests (when available)
python main.py          # Start server directly
```

### Debugging

Enable debug logging by setting environment variables:

```bash
export JINJA2_LSP_LOG_LEVEL=DEBUG
export JINJA2_LSP_LOG_FILE=/tmp/jinja2-lsp.log
```

## Configuration Options

### Extension Settings

```json
{
  "jinja2": {
    "enable_emmet": true,           // Enable Emmet expansion
    "enable_jinja_snippets": true,  // Enable Jinja2 snippets
    "auto_close_tags": true,        // Auto-close HTML tags
    "validate_on_type": true,       // Real-time validation
    "completion_trigger_chars": ["<", "{", "%", "#", "."],
    "hover_documentation": true,    // Show hover docs
    "format_on_save": true         // Format templates on save
  }
}
```

### Custom Templates

Add custom template directories to search path:

```json
{
  "jinja2": {
    "template_directories": [
      "./templates",
      "./views",
      "../shared/templates"
    ]
  }
}
```

## Debugging & Validation

### Extension Validation

The extension includes validation tools to help debug configuration issues:

#### TOML Validator
```bash
python3 validate_toml.py
```

This script validates your `extension.toml` file and checks:
- TOML syntax validity
- Required fields presence
- Language server configuration
- Grammar repository settings
- Directory structure

#### Extension Test Suite
```bash
python3 test_extension.py
```

Comprehensive test suite that validates:
- Extension directory structure
- Configuration file validity
- Python dependencies
- Language server import/startup
- Sample template processing

### Error Detection

To find specific TOML validation errors:

1. **Python TOML validation**:
   ```bash
   python3 -c "import tomllib; print(tomllib.load(open('extension.toml', 'rb')))"
   ```

2. **Check extension structure**:
   ```bash
   # Verify required directories exist
   ls -la languages/jinja2_html/config.toml
   ls -la server/main.py
   ```

3. **Test language server manually**:
   ```bash
   cd server/
   python3 -m main
   ```

## Troubleshooting

### Common Issues

1. **"Invalid extension.toml file" error**
   - Run `python3 validate_toml.py` to see specific validation errors
   - Ensure all required fields are present: `id`, `name`, `version`, `schema_version`, `authors`, `description`
   - Check grammar configuration uses `repository` and `rev` fields, not local `path`
   - Verify language configuration is in `languages/jinja2_html/config.toml`, not directly in `extension.toml`

2. **Language server not starting**
   - Check Python installation: `python --version`
   - Verify dependencies: `pip list | grep pygls`
   - Test server import: `cd server && python3 -c "import main"`
   - Check Zed logs: View → Developer → Open Logs

3. **Completions not working**
   - Ensure file has correct extension (`.j2`, `.jinja2`, etc.)
   - Check LSP connection in Zed status bar
   - Verify language server binary path in extension config
   - Restart Zed IDE

4. **Syntax highlighting missing**
   - Verify grammar repository and revision are correct
   - Check file association in Zed settings
   - Ensure grammar name matches in both `extension.toml` and `languages/jinja2_html/config.toml`
   - Clear Zed cache and restart

### Performance Tips

- Large templates may have slower completions
- Consider splitting very large templates
- Use template inheritance for better organization

## License

MIT License - see LICENSE file for details.

## Changelog

### v0.1.0
- Initial release
- Basic Jinja2 and HTML completion
- Emmet snippet support
- Syntax highlighting
- Real-time diagnostics
- Hover documentation

## Roadmap

- [ ] Template debugging support
- [ ] Advanced refactoring tools
- [ ] Integration with popular frameworks (Flask, Django)
- [ ] Custom filter/function definitions
- [ ] Template performance analysis
- [ ] Multi-file template analysis
- [ ] Auto-formatting improvements
- [ ] Snippet customization interface