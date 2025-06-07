#!/usr/bin/env python3
"""
Comprehensive Completion Provider for Jinja2 HTML Language Server
Provides intelligent auto-completion for HTML, Jinja2, and integrated features.
"""

import re
from typing import List, Dict, Optional, Set, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json

from lsprotocol.types import (
    CompletionItem,
    CompletionItemKind,
    InsertTextFormat,
    Position,
    Range,
    TextEdit
)

try:
    from .emmet_support import emmet_integration
except ImportError:
    from emmet_support import emmet_integration


class CompletionContext(Enum):
    """Context types for completion."""
    HTML = "html"
    JINJA_EXPRESSION = "jinja_expression"
    JINJA_STATEMENT = "jinja_statement"
    JINJA_COMMENT = "jinja_comment"
    CSS_CLASS = "css_class"
    CSS_ID = "css_id"
    ATTRIBUTE_NAME = "attribute_name"
    ATTRIBUTE_VALUE = "attribute_value"
    UNKNOWN = "unknown"


@dataclass
class CompletionRequest:
    """Represents a completion request with context."""
    position: Position
    line: str
    word: str
    prefix: str
    context: CompletionContext
    trigger_character: Optional[str] = None
    inside_quotes: bool = False
    tag_name: Optional[str] = None


class Jinja2HTMLCompletionProvider:
    """Comprehensive completion provider for Jinja2 HTML templates."""
    
    def __init__(self):
        self.html_tags = self._load_html_tags()
        self.html_attributes = self._load_html_attributes()
        self.jinja2_filters = self._load_jinja2_filters()
        self.jinja2_functions = self._load_jinja2_functions()
        self.jinja2_tests = self._load_jinja2_tests()
        self.jinja2_keywords = self._load_jinja2_keywords()
        self.css_properties = self._load_css_properties()
        self.common_values = self._load_common_attribute_values()
        
        # Cache for extracted variables and context
        self._variable_cache = {}
        self._context_cache = {}
    
    def _load_html_tags(self) -> Dict[str, Dict[str, Any]]:
        """Load HTML tags with metadata."""
        return {
            'div': {
                'description': 'Generic container element',
                'attributes': ['class', 'id', 'style', 'data-*'],
                'snippet': '<div$1>$2</div>$0'
            },
            'span': {
                'description': 'Inline generic container',
                'attributes': ['class', 'id', 'style'],
                'snippet': '<span$1>$2</span>$0'
            },
            'p': {
                'description': 'Paragraph element',
                'attributes': ['class', 'id', 'style'],
                'snippet': '<p$1>$2</p>$0'
            },
            'a': {
                'description': 'Anchor/link element',
                'attributes': ['href', 'target', 'rel', 'class', 'id'],
                'snippet': '<a href="$1"$2>$3</a>$0'
            },
            'img': {
                'description': 'Image element',
                'attributes': ['src', 'alt', 'width', 'height', 'class', 'id'],
                'snippet': '<img src="$1" alt="$2"$3>$0',
                'void': True
            },
            'input': {
                'description': 'Input element',
                'attributes': ['type', 'name', 'value', 'placeholder', 'required', 'class', 'id'],
                'snippet': '<input type="$1" name="$2"$3>$0',
                'void': True
            },
            'form': {
                'description': 'Form element',
                'attributes': ['action', 'method', 'enctype', 'class', 'id'],
                'snippet': '<form action="$1" method="$2"$3>\n    $4\n</form>$0'
            },
            'button': {
                'description': 'Button element',
                'attributes': ['type', 'name', 'value', 'class', 'id', 'onclick'],
                'snippet': '<button type="$1"$2>$3</button>$0'
            },
            'table': {
                'description': 'Table element',
                'attributes': ['class', 'id', 'border', 'cellpadding', 'cellspacing'],
                'snippet': '<table$1>\n    <tr>\n        <td>$2</td>\n    </tr>\n</table>$0'
            },
            'ul': {
                'description': 'Unordered list',
                'attributes': ['class', 'id', 'style'],
                'snippet': '<ul$1>\n    <li>$2</li>\n</ul>$0'
            },
            'ol': {
                'description': 'Ordered list',
                'attributes': ['class', 'id', 'style', 'type', 'start'],
                'snippet': '<ol$1>\n    <li>$2</li>\n</ol>$0'
            },
            'li': {
                'description': 'List item',
                'attributes': ['class', 'id', 'style'],
                'snippet': '<li$1>$2</li>$0'
            },
            'h1': {'description': 'Heading 1', 'snippet': '<h1$1>$2</h1>$0'},
            'h2': {'description': 'Heading 2', 'snippet': '<h2$1>$2</h2>$0'},
            'h3': {'description': 'Heading 3', 'snippet': '<h3$1>$2</h3>$0'},
            'h4': {'description': 'Heading 4', 'snippet': '<h4$1>$2</h4>$0'},
            'h5': {'description': 'Heading 5', 'snippet': '<h5$1>$2</h5>$0'},
            'h6': {'description': 'Heading 6', 'snippet': '<h6$1>$2</h6>$0'},
            'header': {
                'description': 'Header section',
                'snippet': '<header$1>\n    $2\n</header>$0'
            },
            'footer': {
                'description': 'Footer section',
                'snippet': '<footer$1>\n    $2\n</footer>$0'
            },
            'nav': {
                'description': 'Navigation section',
                'snippet': '<nav$1>\n    $2\n</nav>$0'
            },
            'main': {
                'description': 'Main content section',
                'snippet': '<main$1>\n    $2\n</main>$0'
            },
            'section': {
                'description': 'Section element',
                'snippet': '<section$1>\n    $2\n</section>$0'
            },
            'article': {
                'description': 'Article element',
                'snippet': '<article$1>\n    $2\n</article>$0'
            },
            'aside': {
                'description': 'Aside element',
                'snippet': '<aside$1>\n    $2\n</aside>$0'
            }
        }
    
    def _load_html_attributes(self) -> Dict[str, Dict[str, Any]]:
        """Load HTML attributes with metadata."""
        return {
            'class': {
                'description': 'Space-separated list of CSS classes',
                'values': [],
                'global': True
            },
            'id': {
                'description': 'Unique identifier',
                'global': True
            },
            'style': {
                'description': 'Inline CSS styles',
                'global': True
            },
            'title': {
                'description': 'Advisory information about the element',
                'global': True
            },
            'data-*': {
                'description': 'Custom data attributes',
                'global': True
            },
            'href': {
                'description': 'URL reference',
                'tags': ['a', 'link'],
                'values': ['#', 'mailto:', 'tel:', 'javascript:']
            },
            'src': {
                'description': 'Source URL',
                'tags': ['img', 'script', 'iframe', 'audio', 'video', 'source'],
            },
            'alt': {
                'description': 'Alternative text',
                'tags': ['img', 'area', 'input']
            },
            'type': {
                'description': 'Type specification',
                'tags': ['input', 'button', 'script', 'style', 'link'],
                'values': {
                    'input': ['text', 'password', 'email', 'number', 'tel', 'url', 'search', 'submit', 'reset', 'button', 'checkbox', 'radio', 'file', 'hidden', 'date', 'datetime-local', 'month', 'week', 'time', 'color', 'range'],
                    'button': ['submit', 'reset', 'button'],
                    'script': ['text/javascript', 'module'],
                    'style': ['text/css'],
                    'link': ['stylesheet', 'icon', 'preload', 'prefetch']
                }
            },
            'name': {
                'description': 'Name of the element',
                'tags': ['input', 'select', 'textarea', 'button', 'form', 'fieldset', 'output']
            },
            'value': {
                'description': 'Value of the element',
                'tags': ['input', 'button', 'option', 'li', 'meter', 'progress']
            },
            'placeholder': {
                'description': 'Placeholder text',
                'tags': ['input', 'textarea']
            },
            'required': {
                'description': 'Required field',
                'tags': ['input', 'select', 'textarea'],
                'boolean': True
            },
            'disabled': {
                'description': 'Disabled element',
                'boolean': True
            },
            'readonly': {
                'description': 'Read-only element',
                'tags': ['input', 'textarea'],
                'boolean': True
            },
            'checked': {
                'description': 'Checked state',
                'tags': ['input'],
                'boolean': True
            },
            'selected': {
                'description': 'Selected state',
                'tags': ['option'],
                'boolean': True
            },
            'method': {
                'description': 'HTTP method',
                'tags': ['form'],
                'values': ['get', 'post', 'put', 'delete', 'patch']
            },
            'action': {
                'description': 'Form action URL',
                'tags': ['form']
            },
            'target': {
                'description': 'Target window or frame',
                'tags': ['a', 'form'],
                'values': ['_blank', '_self', '_parent', '_top']
            },
            'rel': {
                'description': 'Relationship between documents',
                'tags': ['a', 'link'],
                'values': ['stylesheet', 'icon', 'canonical', 'nofollow', 'noopener', 'noreferrer']
            }
        }
    
    def _load_jinja2_filters(self) -> Dict[str, Dict[str, Any]]:
        """Load Jinja2 filters with metadata."""
        return {
            'abs': {'description': 'Return absolute value of a number'},
            'attr': {'description': 'Get attribute of an object', 'args': ['name']},
            'batch': {'description': 'Batch items into sublists', 'args': ['linecount', 'fill_with']},
            'capitalize': {'description': 'Capitalize the first character'},
            'center': {'description': 'Center string in given width', 'args': ['width']},
            'default': {'description': 'Use default value if variable is undefined', 'args': ['default_value', 'boolean']},
            'd': {'description': 'Alias for default filter', 'args': ['default_value', 'boolean']},
            'dictsort': {'description': 'Sort dictionary by key or value', 'args': ['case_sensitive', 'by']},
            'escape': {'description': 'Escape HTML characters'},
            'e': {'description': 'Alias for escape filter'},
            'filesizeformat': {'description': 'Format bytes as human readable file size'},
            'first': {'description': 'Return first item of sequence'},
            'float': {'description': 'Convert to floating point number', 'args': ['default']},
            'forceescape': {'description': 'Force HTML escaping'},
            'format': {'description': 'Format string using Python formatting'},
            'groupby': {'description': 'Group items by attribute', 'args': ['attribute']},
            'indent': {'description': 'Indent lines of text', 'args': ['width', 'first']},
            'int': {'description': 'Convert to integer', 'args': ['default', 'base']},
            'join': {'description': 'Join items with separator', 'args': ['separator', 'attribute']},
            'last': {'description': 'Return last item of sequence'},
            'length': {'description': 'Return length of sequence'},
            'count': {'description': 'Alias for length filter'},
            'list': {'description': 'Convert to list'},
            'lower': {'description': 'Convert to lowercase'},
            'map': {'description': 'Apply filter to each item', 'args': ['filter']},
            'max': {'description': 'Return maximum value', 'args': ['attribute']},
            'min': {'description': 'Return minimum value', 'args': ['attribute']},
            'pprint': {'description': 'Pretty print variable'},
            'random': {'description': 'Return random item from sequence'},
            'reject': {'description': 'Filter items that match test', 'args': ['test']},
            'rejectattr': {'description': 'Filter items by attribute test', 'args': ['attribute', 'test']},
            'replace': {'description': 'Replace substring', 'args': ['old', 'new', 'count']},
            'reverse': {'description': 'Reverse sequence'},
            'round': {'description': 'Round number', 'args': ['precision', 'method']},
            'safe': {'description': 'Mark string as safe for HTML output'},
            's': {'description': 'Alias for safe filter'},
            'select': {'description': 'Filter items that match test', 'args': ['test']},
            'selectattr': {'description': 'Filter items by attribute test', 'args': ['attribute', 'test']},
            'slice': {'description': 'Slice sequence', 'args': ['slices', 'fill_with']},
            'sort': {'description': 'Sort sequence', 'args': ['reverse', 'case_sensitive', 'attribute']},
            'string': {'description': 'Convert to string'},
            'striptags': {'description': 'Remove HTML tags'},
            'sum': {'description': 'Sum numeric values', 'args': ['attribute', 'start']},
            'title': {'description': 'Convert to title case'},
            'trim': {'description': 'Remove leading/trailing whitespace', 'args': ['chars']},
            'truncate': {'description': 'Truncate string', 'args': ['length', 'killwords', 'end', 'leeway']},
            'unique': {'description': 'Remove duplicate items', 'args': ['case_sensitive', 'attribute']},
            'upper': {'description': 'Convert to uppercase'},
            'urlencode': {'description': 'URL encode string'},
            'urlize': {'description': 'Convert URLs to clickable links', 'args': ['trim_url_limit', 'nofollow', 'target', 'rel']},
            'wordcount': {'description': 'Count words in string'},
            'wordwrap': {'description': 'Wrap text to specified width', 'args': ['width', 'break_long_words', 'wrapstring']},
            'xmlattr': {'description': 'Create XML/HTML attributes from dict'},
            'tojson': {'description': 'Convert to JSON string', 'args': ['indent']},
            'tojsonfilter': {'description': 'Alias for tojson filter'}
        }
    
    def _load_jinja2_functions(self) -> Dict[str, Dict[str, Any]]:
        """Load Jinja2 global functions."""
        return {
            'range': {'description': 'Generate range of numbers', 'args': ['start', 'stop', 'step']},
            'lipsum': {'description': 'Generate lorem ipsum text', 'args': ['n', 'html', 'min', 'max']},
            'dict': {'description': 'Create dictionary from keyword arguments'},
            'cycler': {'description': 'Create cycler object', 'args': ['*items']},
            'joiner': {'description': 'Create joiner object', 'args': ['sep']},
            'namespace': {'description': 'Create namespace object for variable assignment'}
        }
    
    def _load_jinja2_tests(self) -> Dict[str, Dict[str, Any]]:
        """Load Jinja2 test functions."""
        return {
            'callable': {'description': 'Test if object is callable'},
            'defined': {'description': 'Test if variable is defined'},
            'divisibleby': {'description': 'Test if number is divisible by another', 'args': ['num']},
            'escaped': {'description': 'Test if string is escaped'},
            'even': {'description': 'Test if number is even'},
            'iterable': {'description': 'Test if object is iterable'},
            'lower': {'description': 'Test if string is lowercase'},
            'mapping': {'description': 'Test if object is mapping (dict-like)'},
            'none': {'description': 'Test if value is None'},
            'number': {'description': 'Test if value is a number'},
            'odd': {'description': 'Test if number is odd'},
            'sameas': {'description': 'Test if objects are the same', 'args': ['other']},
            'sequence': {'description': 'Test if object is a sequence'},
            'string': {'description': 'Test if value is a string'},
            'undefined': {'description': 'Test if variable is undefined'},
            'upper': {'description': 'Test if string is uppercase'}
        }
    
    def _load_jinja2_keywords(self) -> Dict[str, Dict[str, Any]]:
        """Load Jinja2 keywords and statements."""
        return {
            # Control structures
            'if': {'description': 'Conditional statement', 'snippet': 'if $1:\n    $2\n{% endif %}$0'},
            'elif': {'description': 'Else if condition'},
            'else': {'description': 'Else clause'},
            'endif': {'description': 'End if statement'},
            'for': {'description': 'For loop', 'snippet': 'for $1 in $2:\n    $3\n{% endfor %}$0'},
            'endfor': {'description': 'End for loop'},
            'while': {'description': 'While loop (if supported)'},
            'endwhile': {'description': 'End while loop'},
            'break': {'description': 'Break from loop'},
            'continue': {'description': 'Continue to next iteration'},
            
            # Template inheritance
            'extends': {'description': 'Extend base template', 'snippet': 'extends "$1"'},
            'block': {'description': 'Define block', 'snippet': 'block $1:\n    $2\n{% endblock %}$0'},
            'endblock': {'description': 'End block definition'},
            'super': {'description': 'Call parent block content'},
            
            # Include and import
            'include': {'description': 'Include another template', 'snippet': 'include "$1"'},
            'import': {'description': 'Import template', 'snippet': 'import "$1" as $2'},
            'from': {'description': 'Import from template', 'snippet': 'from "$1" import $2'},
            
            # Variables and macros
            'set': {'description': 'Set variable', 'snippet': 'set $1 = $2'},
            'macro': {'description': 'Define macro', 'snippet': 'macro $1($2):\n    $3\n{% endmacro %}$0'},
            'endmacro': {'description': 'End macro definition'},
            'call': {'description': 'Call macro with content', 'snippet': 'call $1($2):\n    $3\n{% endcall %}$0'},
            'endcall': {'description': 'End call block'},
            
            # Context and scoping
            'with': {'description': 'Create local scope', 'snippet': 'with $1 = $2:\n    $3\n{% endwith %}$0'},
            'endwith': {'description': 'End with block'},
            'without': {'description': 'Without context modifier'},
            'context': {'description': 'With context modifier'},
            'ignore': {'description': 'Ignore missing'},
            'missing': {'description': 'Missing template handling'},
            
            # Filters and processing
            'filter': {'description': 'Apply filter to block', 'snippet': 'filter $1:\n    $2\n{% endfilter %}$0'},
            'endfilter': {'description': 'End filter block'},
            'raw': {'description': 'Raw content block', 'snippet': 'raw:\n    $1\n{% endraw %}$0'},
            'endraw': {'description': 'End raw block'},
            
            # Auto-escaping
            'autoescape': {'description': 'Auto-escape block', 'snippet': 'autoescape $1:\n    $2\n{% endautoescape %}$0'},
            'endautoescape': {'description': 'End auto-escape block'},
            
            # Operators and logic
            'and': {'description': 'Logical AND operator'},
            'or': {'description': 'Logical OR operator'},
            'not': {'description': 'Logical NOT operator'},
            'is': {'description': 'Test operator'},
            'in': {'description': 'Membership test operator'},
            'as': {'description': 'Alias operator'},
            
            # Internationalization (if enabled)
            'trans': {'description': 'Translation block', 'snippet': 'trans:\n    $1\n{% endtrans %}$0'},
            'endtrans': {'description': 'End translation block'},
            'pluralize': {'description': 'Pluralization in trans block'},
            
            # Miscellaneous
            'do': {'description': 'Execute expression without output', 'snippet': 'do $1'}
        }
    
    def _load_css_properties(self) -> List[str]:
        """Load common CSS properties for style attribute completion."""
        return [
            'color', 'background-color', 'font-size', 'font-family', 'font-weight',
            'margin', 'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
            'padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
            'border', 'border-top', 'border-right', 'border-bottom', 'border-left',
            'border-color', 'border-width', 'border-style', 'border-radius',
            'width', 'height', 'max-width', 'max-height', 'min-width', 'min-height',
            'display', 'position', 'top', 'right', 'bottom', 'left', 'z-index',
            'float', 'clear', 'overflow', 'visibility', 'opacity',
            'text-align', 'text-decoration', 'text-transform', 'line-height',
            'vertical-align', 'white-space', 'word-wrap', 'word-break',
            'flex', 'flex-direction', 'justify-content', 'align-items', 'align-content',
            'grid', 'grid-template-columns', 'grid-template-rows', 'grid-gap',
            'box-shadow', 'text-shadow', 'transform', 'transition', 'animation'
        ]
    
    def _load_common_attribute_values(self) -> Dict[str, List[str]]:
        """Load common values for HTML attributes."""
        return {
            'display': ['block', 'inline', 'inline-block', 'flex', 'grid', 'none', 'table', 'table-cell'],
            'position': ['static', 'relative', 'absolute', 'fixed', 'sticky'],
            'text-align': ['left', 'center', 'right', 'justify'],
            'font-weight': ['normal', 'bold', '100', '200', '300', '400', '500', '600', '700', '800', '900'],
            'font-style': ['normal', 'italic', 'oblique'],
            'text-decoration': ['none', 'underline', 'overline', 'line-through'],
            'text-transform': ['none', 'uppercase', 'lowercase', 'capitalize'],
            'overflow': ['visible', 'hidden', 'scroll', 'auto'],
            'float': ['none', 'left', 'right'],
            'clear': ['none', 'left', 'right', 'both'],
            'visibility': ['visible', 'hidden'],
            'cursor': ['pointer', 'default', 'text', 'wait', 'help', 'move', 'not-allowed']
        }
    
    def analyze_completion_context(self, line: str, position: int) -> CompletionRequest:
        """Analyze the context for completion."""
        word_start = position
        word_end = position
        
        # Find word boundaries
        while word_start > 0 and (line[word_start - 1].isalnum() or line[word_start - 1] in '_-.:'):
            word_start -= 1
        while word_end < len(line) and (line[word_end].isalnum() or line[word_end] in '_-.:'):
            word_end += 1
        
        word = line[word_start:word_end]
        prefix = line[:position]
        
        # Determine context
        context = self._determine_context(line, position)
        
        # Check if inside quotes
        inside_quotes = self._is_inside_quotes(line, position)
        
        # Get current tag name if applicable
        tag_name = self._get_current_tag(line, position)
        
        return CompletionRequest(
            position=Position(line=0, character=position),
            line=line,
            word=word,
            prefix=prefix,
            context=context,
            inside_quotes=inside_quotes,
            tag_name=tag_name
        )
    
    def _determine_context(self, line: str, position: int) -> CompletionContext:
        """Determine the completion context."""
        # Check for Jinja2 contexts first
        before_cursor = line[:position]
        
        # Jinja2 expression {{ }}
        expr_start = before_cursor.rfind('{{')
        expr_end = before_cursor.rfind('}}')
        if expr_start > expr_end:
            return CompletionContext.JINJA_EXPRESSION
        
        # Jinja2 statement {% %}
        stmt_start = before_cursor.rfind('{%')
        stmt_end = before_cursor.rfind('%}')
        if stmt_start > stmt_end:
            return CompletionContext.JINJA_STATEMENT
        
        # Jinja2 comment {# #}
        comment_start = before_cursor.rfind('{#')
        comment_end = before_cursor.rfind('#}')
        if comment_start > comment_end:
            return CompletionContext.JINJA_COMMENT
        
        # HTML attribute value
        if self._is_in_attribute_value(line, position):
            return CompletionContext.ATTRIBUTE_VALUE
        
        # HTML attribute name
        if self._is_in_attribute_name(line, position):
            return CompletionContext.ATTRIBUTE_NAME
        
        # CSS class (class="...")
        if self._is_in_css_class(line, position):
            return CompletionContext.CSS_CLASS
        
        # CSS ID (id="...")
        if self._is_in_css_id(line, position):
            return CompletionContext.CSS_ID
        
        return CompletionContext.HTML
    
    def _is_inside_quotes(self, line: str, position: int) -> bool:
        """Check if position is inside quotes."""
        before_cursor = line[:position]
        double_quotes = before_cursor.count('"') - before_cursor.count('\\"')
        single_quotes = before_cursor.count("'") - before_cursor.count("\\'")
        return (double_quotes % 2 == 1) or (single_quotes % 2 == 1)
    
    def _get_current_tag(self, line: str, position: int) -> Optional[str]:
        """Get the current HTML tag name."""
        before_cursor = line[:position]
        tag_match = re.search(r'<(\w+)[^>]*$', before_cursor)
        return tag_match.group(1) if tag_match else None
    
    def _is_in_attribute_value(self, line: str, position: int) -> bool:
        """Check if position is in an attribute value."""
        before_cursor = line[:position]
        # Look for pattern: attr="value_here or attr='value_here
        return bool(re.search(r'\w+\s*=\s*["\'][^"\']*$', before_cursor))
    
    def _is_in_attribute_name(self, line: str, position: int) -> bool:
        """Check if position is in an attribute name."""
        before_cursor = line[:position]
        # After < and tag name, but not in quotes
        if self._is_inside_quotes(line, position):
            return False
        return bool(re.search(r'<\w+[^>]*\s+[\w-]*$', before_cursor))
    
    def _is_in_css_class(self, line: str, position: int) -> bool:
        """Check if position is in CSS class attribute."""
        before_cursor = line[:position]
        return bool(re.search(r'class\s*=\s*["\'][^"\']*$', before_cursor))
    
    def _is_in_css_id(self, line: str, position: int) -> bool:
        """Check if position is in CSS ID attribute."""
        before_cursor = line[:position]
        return bool(re.search(r'id\s*=\s*["\'][^"\']*$', before_cursor))
    
    def provide_completions(self, request: CompletionRequest, document_content: str = "") -> List[CompletionItem]:
        """Provide completions based on context."""
        completions = []
        
        if request.context == CompletionContext.HTML:
            completions.extend(self._get_html_completions(request))
            completions.extend(self._get_emmet_completions(request))
        
        elif request.context == CompletionContext.JINJA_EXPRESSION:
            completions.extend(self._get_jinja_expression_completions(request, document_content))
        
        elif request.context == CompletionContext.JINJA_STATEMENT:
            completions.extend(self._get_jinja_statement_completions(request, document_content))
        
        elif request.context == CompletionContext.ATTRIBUTE_NAME:
            completions.extend(self._get_attribute_name_completions(request))
        
        elif request.context == CompletionContext.ATTRIBUTE_VALUE:
            completions.extend(self._get_attribute_value_completions(request))
        
        elif request.context == CompletionContext.CSS_CLASS:
            completions.extend(self._get_css_class_completions(request, document_content))
        
        elif request.context == CompletionContext.CSS_ID:
            completions.extend(self._get_css_id_completions(request, document_content))
        
        # Filter completions by prefix
        if request.word:
            completions = [c for c in completions if c.label.lower().startswith(request.word.lower())]
        
        return completions
    
    def _get_html_completions(self, request: CompletionRequest) -> List[CompletionItem]:
        """Get HTML tag completions."""
        completions = []
        
        for tag, info in self.html_tags.items():
            if not request.word or tag.startswith(request.word.lower()):
                snippet = info.get('snippet', f'<{tag}>$1</{tag}>$0')
                if info.get('void', False):
                    snippet = f'<{tag}$1>$0'
                
                completions.append(CompletionItem(
                    label=tag,
                    kind=CompletionItemKind.Keyword,
                    detail=f"HTML <{tag}> element",
                    documentation=info.get('description', f'HTML {tag} element'),
                    insert_text=snippet,
                    insert_text_format=InsertTextFormat.Snippet
                ))
        
        return completions
    
    def _get_emmet_completions(self, request: CompletionRequest) -> List[CompletionItem]:
        """Get Emmet snippet completions."""
        return [
            CompletionItem(
                label=item['label'],
                kind=CompletionItemKind.Snippet,
                detail=item['detail'],
                documentation=item['documentation'],
                insert_text=item['insert_text'],
                insert_text_format=InsertTextFormat.Snippet
            )
            for item in emmet_integration.get_jinja_completions(request.word)
        ]
    
    def _get_jinja_expression_completions(self, request: CompletionRequest, document_content: str) -> List[CompletionItem]:
        """Get completions for Jinja2 expressions {{ }}."""
        completions = []
        
        # Variables from document
        variables = self._extract_variables(document_content)
        for var in variables:
            if not request.word or var.startswith(request.word):
                completions.append(CompletionItem(
                    label=var,
                    kind=CompletionItemKind.Variable,
                    detail="Template variable",
                    documentation=f"Variable: {var}"
                ))
        
        # Filters
        for filter_name, info in self.jinja2_filters.items():
            if not request.word or filter_name.startswith(request.word):
                args = info.get('args', [])
                snippet = f"{filter_name}" + (f"({', '.join(f'${i+1}' for i in range(len(args)))})" if args else "")
                
                completions.append(CompletionItem(
                    label=filter_name,
                    kind=CompletionItemKind.Function,
                    detail="Jinja2 filter",
                    documentation=info['description'],
                    insert_text=snippet,
                    insert_text_format=InsertTextFormat.Snippet if args else InsertTextFormat.PlainText
                ))
        
        # Functions
        for func_name, info in self.jinja2_functions.items():
            if not request.word or func_name.startswith(request.word):
                args = info.get('args', [])
                snippet = f"{func_name}({', '.join(f'${i+1}' for i in range(len(args)))})"
                
                completions.append(CompletionItem(
                    label=func_name,
                    kind=CompletionItemKind.Function,
                    detail="Jinja2 function",
                    documentation=info['description'],
                    insert_text=snippet,
                    insert_text_format=InsertTextFormat.Snippet
                ))
        
        return completions
    
    def _get_jinja_statement_completions(self, request: CompletionRequest, document_content: str) -> List[CompletionItem]:
        """Get completions for Jinja2 statements {% %}."""
        completions = []
        
        # Keywords
        for keyword, info in self.jinja2_keywords.items():
            if not request.word or keyword.startswith(request.word):
                snippet = info.get('snippet', keyword)
                
                completions.append(CompletionItem(
                    label=keyword,
                    kind=CompletionItemKind.Keyword,
                    detail="Jinja2 keyword",
                    documentation=info['description'],
                    insert_text=snippet,
                    insert_text_format=InsertTextFormat.Snippet if '$' in snippet else InsertTextFormat.PlainText
                ))
        
        # Tests (for use with 'is' operator)
        for test_name, info in self.jinja2_tests.items():
            if not request.word or test_name.startswith(request.word):
                completions.append(CompletionItem(
                    label=test_name,
                    kind=CompletionItemKind.Function,
                    detail="Jinja2 test",
                    documentation=info['description'],
                    insert_text=test_name
                ))
        
        # Variables
        variables = self._extract_variables(document_content)
        for var in variables:
            if not request.word or var.startswith(request.word):
                completions.append(CompletionItem(
                    label=var,
                    kind=CompletionItemKind.Variable,
                    detail="Template variable",
                    documentation=f"Variable: {var}"
                ))
        
        return completions
    
    def _get_attribute_name_completions(self, request: CompletionRequest) -> List[CompletionItem]:
        """Get HTML attribute name completions."""
        completions = []
        
        for attr_name, info in self.html_attributes.items():
            # Check if attribute is applicable to current tag
            if request.tag_name:
                applicable_tags = info.get('tags', [])
                if applicable_tags and request.tag_name not in applicable_tags and not info.get('global', False):
                    continue
            
            if not request.word or attr_name.startswith(request.word):
                snippet = f'{attr_name}="$1"$0' if not info.get('boolean', False) else attr_name
                
                completions.append(CompletionItem(
                    label=attr_name,
                    kind=CompletionItemKind.Property,
                    detail="HTML attribute",
                    documentation=info.get('description', f'HTML {attr_name} attribute'),
                    insert_text=snippet,
                    insert_text_format=InsertTextFormat.Snippet if '"' in snippet else InsertTextFormat.PlainText
                ))
        
        return completions
    
    def _get_attribute_value_completions(self, request: CompletionRequest) -> List[CompletionItem]:
        """Get HTML attribute value completions."""
        completions = []
        
        # Extract attribute name from context
        attr_match = re.search(r'(\w+)\s*=\s*["\'][^"\']*$', request.prefix)
        if not attr_match:
            return completions
        
        attr_name = attr_match.group(1)
        attr_info = self.html_attributes.get(attr_name, {})
        
        # Get values for this attribute
        values = attr_info.get('values', [])
        if isinstance(values, dict) and request.tag_name:
            values = values.get(request.tag_name, [])
        
        for value in values:
            if not request.word or value.startswith(request.word):
                completions.append(CompletionItem(
                    label=value,
                    kind=CompletionItemKind.Value,
                    detail=f"{attr_name} value",
                    insert_text=value
                ))
        
        # Add CSS property completions for style attribute
        if attr_name == 'style':
            for prop in self.css_properties:
                if not request.word or prop.startswith(request.word):
                    values = self.common_values.get(prop, [])
                    snippet = f"{prop}: $1;" if not values else f"{prop}: ${{1|{','.join(values)}|}};"
                    
                    completions.append(CompletionItem(
                        label=prop,
                        kind=CompletionItemKind.Property,
                        detail="CSS property",
                        insert_text=snippet,
                        insert_text_format=InsertTextFormat.Snippet
                    ))
        
        return completions
    
    def _get_css_class_completions(self, request: CompletionRequest, document_content: str) -> List[CompletionItem]:
        """Get CSS class completions."""
        completions = []
        
        # Extract existing classes from document
        classes = self._extract_css_classes(document_content)
        
        for class_name in classes:
            if not request.word or class_name.startswith(request.word):
                completions.append(CompletionItem(
                    label=class_name,
                    kind=CompletionItemKind.Value,
                    detail="CSS class",
                    insert_text=class_name
                ))
        
        # Add common CSS framework classes
        common_classes = [
            'container', 'row', 'col', 'col-md-6', 'col-lg-4',
            'btn', 'btn-primary', 'btn-secondary', 'btn-success', 'btn-danger',
            'form-control', 'form-group', 'form-label',
            'nav', 'navbar', 'nav-link', 'nav-item',
            'card', 'card-body', 'card-header', 'card-footer',
            'table', 'table-striped', 'table-bordered',
            'text-center', 'text-left', 'text-right',
            'd-flex', 'd-block', 'd-none', 'd-inline',
            'mb-3', 'mt-3', 'p-3', 'm-3'
        ]
        
        for class_name in common_classes:
            if not request.word or class_name.startswith(request.word):
                completions.append(CompletionItem(
                    label=class_name,
                    kind=CompletionItemKind.Value,
                    detail="CSS class",
                    insert_text=class_name
                ))
        
        return completions
    
    def _get_css_id_completions(self, request: CompletionRequest, document_content: str) -> List[CompletionItem]:
        """Get CSS ID completions."""
        completions = []
        
        # Extract existing IDs from document
        ids = self._extract_css_ids(document_content)
        
        for id_name in ids:
            if not request.word or id_name.startswith(request.word):
                completions.append(CompletionItem(
                    label=id_name,
                    kind=CompletionItemKind.Value,
                    detail="CSS ID",
                    insert_text=id_name
                ))
        
        return completions
    
    def _extract_variables(self, content: str) -> Set[str]:
        """Extract Jinja2 variables from template content."""
        variables = set()
        
        # Variables in expressions {{ var }}
        expr_pattern = r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)'
        matches = re.findall(expr_pattern, content)
        for match in matches:
            variables.add(match.split('.')[0])
        
        # Variables in statements {% for var in ... %}
        for_pattern = r'\{%\s*for\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.findall(for_pattern, content)
        variables.update(matches)
        
        # Variables in set statements {% set var = ... %}
        set_pattern = r'\{%\s*set\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.findall(set_pattern, content)
        variables.update(matches)
        
        return variables
    
    def _extract_css_classes(self, content: str) -> Set[str]:
        """Extract CSS classes from template content."""
        classes = set()
        
        # Find class attributes
        class_pattern = r'class\s*=\s*["\']([^"\']+)["\']'
        matches = re.findall(class_pattern, content)
        
        for match in matches:
            # Split by whitespace to get individual classes
            classes.update(match.split())
        
        return classes
    
    def _extract_css_ids(self, content: str) -> Set[str]:
        """Extract CSS IDs from template content."""
        ids = set()
        
        # Find id attributes
        id_pattern = r'id\s*=\s*["\']([^"\']+)["\']'
        matches = re.findall(id_pattern, content)
        ids.update(matches)
        
        return ids