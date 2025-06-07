# Quick Start Guide - Jinja2 HTML Language Server for Zed

Get up and running with the Jinja2 HTML Language Server in under 5 minutes!

## 🚀 One-Command Installation

```bash
./install.sh
```

That's it! The installation script will:
- Check prerequisites
- Install Python dependencies
- Copy extension files to Zed
- Generate configuration
- Test the installation

## 📋 Prerequisites

- **Python 3.8+** (check with `python --version`)
- **Zed IDE** (download from [zed.dev](https://zed.dev))
- **pip** (Python package manager)

## 🛠️ Manual Installation (if needed)

### 1. Install Python Dependencies
```bash
cd server/
pip install -r requirements.txt
```

### 2. Install Extension
```bash
# Copy to Zed extensions directory
mkdir -p ~/.config/zed/extensions/
cp -r . ~/.config/zed/extensions/jinja2-html/
```

### 3. Configure Zed
Add to your Zed `settings.json`:

```json
{
  "languages": {
    "Jinja2 HTML": {
      "language_servers": ["jinja2-html-lsp"]
    }
  },
  "lsp": {
    "jinja2-html-lsp": {
      "binary": {
        "path": "python",
        "arguments": ["-m", "server.main"]
      }
    }
  }
}
```

## ✅ Verify Installation

Run the diagnostic script:
```bash
python diagnose.py
```

## 🎯 First Steps

### 1. Create a Template File
Create a file with one of these extensions:
- `.j2`
- `.jinja2`
- `.html.j2`
- `.html.jinja2`

### 2. Try Basic Completions

**HTML Tags:**
```html
<div|  <!-- Type 'div' and get completion -->
```

**Jinja2 Variables:**
```jinja2
{{ user.|  <!-- Get variable completions -->
```

**Jinja2 Statements:**
```jinja2
{% for|  <!-- Get keyword completions -->
```

### 3. Use Emmet Shortcuts

**HTML Structure:**
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

**Jinja2 Patterns:**
```
j:form  <!-- Jinja2-aware form -->
j:table <!-- Jinja2 table iteration -->
```

## 🔧 Common Issues & Solutions

### Extension Not Working?
1. **Check Zed logs:** View → Developer → Open Logs
2. **Restart Zed:** Sometimes needed after installation
3. **Verify file extension:** Must be `.j2`, `.jinja2`, etc.
4. **Run diagnostics:** `python diagnose.py`

### No Completions?
1. **Check LSP status:** Look for language server icon in status bar
2. **Verify Python path:** Ensure `python` command works
3. **Check dependencies:** Run `pip list | grep pygls`

### Syntax Highlighting Missing?
1. **Clear Zed cache:** Close Zed, delete cache, restart
2. **Check file association:** File should show as "Jinja2 HTML"
3. **Verify grammar:** Check grammar file exists in extension

## 📖 Key Features to Try

### Auto-Completion
- HTML tags and attributes
- Jinja2 filters and functions
- Template variables
- CSS classes and IDs

### Emmet Expansion
- Standard HTML: `ul>li*5`
- Jinja2 enhanced: `j:form`, `j:table`
- Custom snippets: `html:5`, `nav`, `form`

### Error Detection
- Unclosed Jinja2 blocks
- Invalid syntax
- Missing template tags
- HTML validation

### Hover Documentation
- Jinja2 filter descriptions
- Function signatures
- HTML element info
- Keyword explanations

## 🎨 Example Template

Try this example in a `.html.j2` file:

```jinja2
<!DOCTYPE html>
<html lang="en">
<head>
    <title>{{ page_title|default("My Site") }}</title>
</head>
<body>
    <header class="navbar">
        <h1>{{ site_name }}</h1>
    </header>
    
    <main>
        {% if users %}
        <section class="users">
            {% for user in users %}
            <div class="user-card">
                <h3>{{ user.name|title }}</h3>
                <p>{{ user.email|lower }}</p>
                {% if user.is_active %}
                <span class="badge active">Active</span>
                {% endif %}
            </div>
            {% endfor %}
        </section>
        {% else %}
        <p>No users found.</p>
        {% endif %}
    </main>
    
    {% block content %}{% endblock %}
</body>
</html>
```

## 🔍 Testing Completions

Place your cursor in these positions and press `Ctrl+Space`:

1. **After `<`** → HTML tag completions
2. **After `{{`** → Variable and filter completions  
3. **After `{%`** → Jinja2 keyword completions
4. **After `class="`** → CSS class completions
5. **After `|`** → Jinja2 filter completions

## 🆘 Need Help?

- **Documentation:** See `README.md` for detailed info
- **Diagnostics:** Run `python diagnose.py`
- **Issues:** Check GitHub issues or create a new one
- **Configuration:** See sample configs in `zed-settings.json`

## 🎉 You're Ready!

The extension is now installed and configured. Start creating Jinja2 templates and enjoy:
- ⚡ Lightning-fast completions
- 🎯 Context-aware suggestions  
- 🛠️ Powerful Emmet integration
- 🔍 Real-time error detection
- 📚 Comprehensive documentation

Happy templating! 🚀