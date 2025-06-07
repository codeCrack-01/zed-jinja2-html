# Jinja2 HTML Language Server Package
__version__ = "0.1.0"
__author__ = "Jinja2 HTML LSP Contributors"

try:
    from .main import main
except ImportError:
    # Handle case when imported as a module directly
    from main import main

__all__ = ["main"]