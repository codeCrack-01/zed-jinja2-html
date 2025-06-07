# Jinja2 HTML Language Server - Architecture Overview

## Project Summary

This project provides a comprehensive Language Server Protocol (LSP) implementation for Jinja2 HTML templates in Zed IDE. It offers intelligent auto-completion, syntax highlighting, error detection, and advanced Emmet snippet support with Jinja2 template integration.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Zed IDE                                 │
├─────────────────────────────────────────────────────────────┤
│  Extension System  │  Language Client  │  Grammar Engine   │
└─────────────────────────────────────────────────────────────┘
                                │
                                │ LSP Protocol
                                │
┌─────────────────────────────────────────────────────────────┐
│              Jinja2 HTML Language Server                   │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│ │  Main Server    │ │ Completion      │ │ Emmet Support   │ │
│ │  (main.py)      │ │ Provider        │ │ (emmet_support) │ │
│ │                 │ │ (completion_    │ │                 │ │
│ │ - LSP Protocol  │ │  provider.py)   │ │ - Abbreviation  │ │
│ │ - Document Mgmt │ │                 │ │   Parsing       │ │
│ │ - Diagnostics   │ │ - Context       │ │ - HTML/Jinja2   │ │
│ │ - Hover Info    │ │   Analysis      │ │   Integration   │ │
│ └─────────────────┘ │ - HTML Tags     │ │ - Snippet       │ │
│                     │ - Jinja2 Items  │ │   Expansion     │ │
│                     │ - CSS Classes   │ └─────────────────┘ │
│                     │ - Attributes    │                     │
│                     └─────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

## 📂 Project Structure

```
zed-jinja2-html/
├── 📋 Extension Configuration
│   ├── extension.toml              # Main extension manifest
│   ├── languages/jinja2-html.toml  # Language definition
│   └── grammars/jinja2-html/       # TextMate grammar
│       └── grammar.json
│
├── 🐍 Language Server (Python)
│   ├── server/
│   │   ├── __init__.py             # Package initialization
│   │   ├── main.py                 # Main LSP server
│   │   ├── completion_provider.py  # Completion logic
│   │   ├── emmet_support.py        # Emmet integration
│   │   ├── requirements.txt        # Python dependencies
│   │   ├── setup.py               # Package setup
│   │   └── test_lsp.py            # Test suite
│   │
├── 🛠️ Installation & Testing
│   ├── install.sh                  # Automated installer
│   ├── diagnose.py                # Diagnostic tool
│   └── QUICKSTART.md              # Quick start guide
│
├── 📖 Documentation
│   ├── README.md                   # Main documentation
│   ├── ARCHITECTURE.md            # This file
│   └── example.html.j2            # Example template
│
└── 📄 Project Files
    ├── LICENSE                     # MIT License
    └── MANIFEST.in                # Distribution manifest
```

## 🔧 Core Components

### 1. Main Language Server (`main.py`)

**Responsibilities:**
- LSP protocol implementation using `pygls`
- Document lifecycle management
- Feature registration (completion, hover, diagnostics)
- Message routing and response handling

**Key Classes:**
- `Jinja2HTMLLanguageServer`: Main server class inheriting from `LanguageServer`

**LSP Features Implemented:**
- `textDocument/completion` - Auto-completion
- `textDocument/hover` - Hover documentation
- `textDocument/didOpen` - Document open events
- `textDocument/didChange` - Document change events
- `textDocument/publishDiagnostics` - Error reporting

### 2. Completion Provider (`completion_provider.py`)

**Responsibilities:**
- Context-aware completion analysis
- HTML tag and attribute completion
- Jinja2 syntax completion (filters, functions, keywords)
- CSS class and ID extraction
- Variable extraction from templates

**Key Classes:**
- `Jinja2HTMLCompletionProvider`: Main completion logic
- `CompletionRequest`: Context data structure
- `CompletionContext`: Enum for different contexts

**Completion Contexts:**
- HTML: Tags, attributes, values
- Jinja2 Expression: Variables, filters, functions
- Jinja2 Statement: Keywords, control structures
- CSS: Classes, IDs, properties
- Attribute: Names and values

### 3. Emmet Support (`emmet_support.py`)

**Responsibilities:**
- Emmet abbreviation parsing
- HTML generation from abbreviations
- Jinja2-aware snippet expansion
- Custom template patterns

**Key Classes:**
- `EmmetParser`: Parse Emmet abbreviations into AST
- `EmmetExpander`: Generate HTML from parsed nodes
- `JinjaEmmetIntegration`: Jinja2-specific enhancements
- `EmmetNode`: AST node representation

**Emmet Features:**
- Standard HTML abbreviations (`div.class#id`)
- Multiplication (`li*5`)
- Nesting (`ul>li`)
- Attributes (`input[type=text]`)
- Jinja2 patterns (`j:form`, `j:table`)

### 4. Grammar Definition (`grammar.json`)

**Responsibilities:**
- Syntax highlighting rules
- Token classification
- Scope definitions for themes

**TextMate Grammar Patterns:**
- Jinja2 expressions: `{{ }}`
- Jinja2 statements: `{% %}`
- Jinja2 comments: `{# #}`
- HTML integration
- Nested pattern matching

## 🔄 Data Flow

### Completion Request Flow

```
1. User types in editor
2. Zed sends completion request via LSP
3. Server receives completion params
4. Completion provider analyzes context:
   - Parse current line
   - Determine context (HTML/Jinja2/CSS)
   - Extract word prefix
   - Identify trigger characters
5. Generate completions based on context:
   - HTML: Tags, attributes, Emmet
   - Jinja2: Variables, filters, keywords
   - CSS: Classes, IDs, properties
6. Filter results by prefix
7. Return completion list to Zed
8. Zed displays completions to user
```

### Document Validation Flow

```
1. Document opened/changed in editor
2. Server receives document update
3. Validation engine processes document:
   - Parse Jinja2 syntax
   - Check for unclosed blocks
   - Validate HTML structure
   - Extract semantic information
4. Generate diagnostics list
5. Publish diagnostics to Zed
6. Zed displays errors/warnings
```

## 🧩 Extension Integration

### Zed Extension System

The extension integrates with Zed through:

1. **Extension Manifest** (`extension.toml`):
   - Defines extension metadata
   - Registers language server
   - Associates file extensions
   - Configures language settings

2. **Language Configuration** (`languages/jinja2-html.toml`):
   - File type associations
   - Comment definitions
   - Bracket matching
   - Auto-indentation rules

3. **Grammar Definition** (`grammars/jinja2-html/grammar.json`):
   - Syntax highlighting patterns
   - Token classification
   - Scope definitions

### LSP Communication

The server communicates with Zed using the Language Server Protocol:

- **JSON-RPC** over stdin/stdout
- **Request/Response** pattern for features
- **Notification** pattern for events
- **Capabilities** negotiation during initialization

## 🔍 Context Analysis

The completion provider uses sophisticated context analysis:

### Context Detection Strategy

1. **Character-based Analysis**:
   - Look for Jinja2 delimiters (`{{`, `{%`, `{#`)
   - Identify HTML tag boundaries (`<`, `>`)
   - Detect attribute contexts (`=`, quotes)

2. **Position-aware Parsing**:
   - Calculate cursor position relative to syntax elements
   - Track nesting levels
   - Handle incomplete syntax

3. **Semantic Understanding**:
   - Extract variables from document
   - Build context-sensitive suggestion lists
   - Provide relevant completions only

### Variable Extraction

The system extracts template variables through regex patterns:

- **Expression Variables**: `{{ variable.property }}`
- **Loop Variables**: `{% for item in items %}`
- **Assignment Variables**: `{% set var = value %}`
- **Macro Parameters**: `{% macro name(param) %}`

## ⚡ Performance Considerations

### Optimization Strategies

1. **Lazy Loading**:
   - Load completion data on demand
   - Cache frequently used patterns
   - Minimize startup time

2. **Incremental Parsing**:
   - Only reparse changed document sections
   - Cache analysis results
   - Efficient diff algorithms

3. **Memory Management**:
   - Limit cache sizes
   - Clean up unused documents
   - Efficient data structures

### Scalability Features

- **Document Size Limits**: Handle large templates efficiently
- **Completion Filtering**: Fast prefix matching
- **Background Processing**: Non-blocking operations
- **Resource Cleanup**: Proper memory management

## 🔧 Extension Points

### Adding New Completions

1. **HTML Elements**: Add to `html_tags` dictionary in completion provider
2. **Jinja2 Filters**: Extend `jinja2_filters` with metadata
3. **Emmet Patterns**: Add to `emmet_snippets` or `jinja_snippets`
4. **Custom Contexts**: Implement new `CompletionContext` types

### Extending Emmet Support

1. **New Abbreviations**: Add patterns to `EmmetParser`
2. **Custom Snippets**: Extend snippet dictionaries
3. **Jinja2 Integration**: Add patterns to `JinjaEmmetIntegration`
4. **Template Patterns**: Create domain-specific expansions

### Grammar Enhancements

1. **New Syntax Patterns**: Add to TextMate grammar
2. **Scope Definitions**: Extend for better theming
3. **Nested Languages**: Support embedded languages
4. **Custom Tokens**: Define application-specific patterns

## 🧪 Testing Strategy

### Test Coverage

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Cross-component functionality
3. **Performance Tests**: Large document handling
4. **Protocol Tests**: LSP compliance verification

### Test Categories

- **Parser Tests**: Emmet abbreviation parsing
- **Completion Tests**: Context-aware suggestions
- **Validation Tests**: Error detection accuracy
- **Protocol Tests**: LSP message handling

## 🔮 Future Enhancements

### Planned Features

1. **Template Debugging**: Breakpoint support, variable inspection
2. **Refactoring Tools**: Rename variables, extract blocks
3. **Framework Integration**: Flask, Django, FastAPI support
4. **Performance Analysis**: Template optimization suggestions
5. **Multi-file Analysis**: Cross-template variable tracking
6. **Custom Filters**: User-defined filter completion
7. **Template Inheritance**: Visual inheritance tree
8. **Snippet Customization**: User-defined patterns

### Technical Improvements

1. **AST-based Parsing**: More accurate syntax analysis
2. **Incremental Updates**: Faster document processing
3. **Language Server Protocol 3.17**: Latest LSP features
4. **WebAssembly Integration**: Client-side processing
5. **Tree-sitter Grammar**: Alternative parsing backend

## 📊 Metrics & Monitoring

### Performance Metrics

- Completion response time: < 100ms target
- Memory usage: < 50MB per workspace
- Startup time: < 2 seconds
- Document parsing: < 50ms for typical files

### Quality Metrics

- Completion accuracy: Context-appropriate suggestions
- Error detection: Catch common template mistakes
- User satisfaction: Productivity improvements
- Extension reliability: Minimal crashes/errors

This architecture provides a solid foundation for a comprehensive Jinja2 HTML development experience in Zed IDE, with room for future enhancements and customizations.