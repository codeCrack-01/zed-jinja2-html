#!/usr/bin/env python3
"""
Advanced Emmet Support for Jinja2 HTML Language Server
Provides comprehensive Emmet abbreviation expansion with Jinja2 template integration.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class EmmetNode:
    """Represents a node in the Emmet AST."""
    tag: str
    attributes: Dict[str, str]
    classes: List[str]
    id: Optional[str]
    content: Optional[str]
    children: List['EmmetNode']
    repeat: int = 1
    climb_up: int = 0


class EmmetParser:
    """Parse Emmet abbreviations into structured nodes."""
    
    def __init__(self):
        self.html5_tags = {
            'a', 'abbr', 'address', 'area', 'article', 'aside', 'audio', 'b',
            'base', 'bdi', 'bdo', 'blockquote', 'body', 'br', 'button', 'canvas',
            'caption', 'cite', 'code', 'col', 'colgroup', 'data', 'datalist',
            'dd', 'del', 'details', 'dfn', 'dialog', 'div', 'dl', 'dt', 'em',
            'embed', 'fieldset', 'figcaption', 'figure', 'footer', 'form', 'h1',
            'h2', 'h3', 'h4', 'h5', 'h6', 'head', 'header', 'hgroup', 'hr',
            'html', 'i', 'iframe', 'img', 'input', 'ins', 'kbd', 'label',
            'legend', 'li', 'link', 'main', 'map', 'mark', 'meta', 'meter',
            'nav', 'noscript', 'object', 'ol', 'optgroup', 'option', 'output',
            'p', 'param', 'picture', 'pre', 'progress', 'q', 'rp', 'rt', 'ruby',
            's', 'samp', 'script', 'section', 'select', 'small', 'source', 'span',
            'strong', 'style', 'sub', 'summary', 'sup', 'table', 'tbody', 'td',
            'template', 'textarea', 'tfoot', 'th', 'thead', 'time', 'title', 'tr',
            'track', 'u', 'ul', 'var', 'video', 'wbr'
        }
        
        self.void_elements = {
            'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'
        }
        
        self.snippets = {
            '!': '<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>$1</title>\n</head>\n<body>\n    $0\n</body>\n</html>',
            'html:5': '<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>$1</title>\n</head>\n<body>\n    $0\n</body>\n</html>',
            'cc:ie': '<!--[if IE]>\n    $0\n<![endif]-->',
            'cc:noie': '<!--[if !IE]><!-->\n    $0\n<!--<![endif]-->',
        }

    def parse(self, abbreviation: str) -> List[EmmetNode]:
        """Parse an Emmet abbreviation into nodes."""
        if abbreviation in self.snippets:
            return [EmmetNode(
                tag='snippet',
                attributes={},
                classes=[],
                id=None,
                content=self.snippets[abbreviation],
                children=[]
            )]
        
        # Split by comma for multiple siblings
        parts = self._split_by_comma(abbreviation)
        nodes = []
        
        for part in parts:
            node = self._parse_single_expression(part.strip())
            if node:
                nodes.append(node)
        
        return nodes

    def _split_by_comma(self, text: str) -> List[str]:
        """Split text by comma, respecting parentheses and brackets."""
        parts = []
        current = ""
        depth = 0
        
        for char in text:
            if char in '([{':
                depth += 1
            elif char in ')]}':
                depth -= 1
            elif char == ',' and depth == 0:
                parts.append(current)
                current = ""
                continue
            current += char
        
        if current:
            parts.append(current)
        
        return parts

    def _parse_single_expression(self, expr: str) -> Optional[EmmetNode]:
        """Parse a single Emmet expression."""
        # Handle multiplication
        multiply_match = re.search(r'\*(\d+)$', expr)
        repeat = 1
        if multiply_match:
            repeat = int(multiply_match.group(1))
            expr = expr[:multiply_match.start()]
        
        # Handle climb-up
        climb_up = 0
        while expr.endswith('^'):
            climb_up += 1
            expr = expr[:-1]
        
        # Handle grouping
        if '(' in expr and ')' in expr:
            return self._parse_grouped_expression(expr, repeat, climb_up)
        
        # Handle child operator
        if '>' in expr:
            return self._parse_child_expression(expr, repeat, climb_up)
        
        # Handle sibling operator
        if '+' in expr:
            return self._parse_sibling_expression(expr, repeat, climb_up)
        
        # Parse single element
        return self._parse_element(expr, repeat, climb_up)

    def _parse_element(self, expr: str, repeat: int = 1, climb_up: int = 0) -> Optional[EmmetNode]:
        """Parse a single element."""
        # Extract tag name
        tag_match = re.match(r'^([a-zA-Z0-9-]+)', expr)
        tag = tag_match.group(1) if tag_match else 'div'
        
        # Extract ID
        id_match = re.search(r'#([a-zA-Z0-9-_]+)', expr)
        element_id = id_match.group(1) if id_match else None
        
        # Extract classes
        class_matches = re.findall(r'\.([a-zA-Z0-9-_]+)', expr)
        classes = class_matches
        
        # Extract attributes
        attributes = {}
        attr_matches = re.findall(r'\[([^\]]+)\]', expr)
        for attr_str in attr_matches:
            if '=' in attr_str:
                key, value = attr_str.split('=', 1)
                # Remove quotes if present
                value = value.strip('"\'')
                attributes[key.strip()] = value
            else:
                attributes[attr_str.strip()] = ""
        
        # Extract content
        content_match = re.search(r'\{([^}]*)\}', expr)
        content = content_match.group(1) if content_match else None
        
        return EmmetNode(
            tag=tag,
            attributes=attributes,
            classes=classes,
            id=element_id,
            content=content,
            children=[],
            repeat=repeat,
            climb_up=climb_up
        )

    def _parse_child_expression(self, expr: str, repeat: int = 1, climb_up: int = 0) -> Optional[EmmetNode]:
        """Parse expression with child operator (>)."""
        parts = expr.split('>', 1)
        if len(parts) != 2:
            return None
        
        parent = self._parse_element(parts[0].strip())
        if not parent:
            return None
        
        child = self._parse_single_expression(parts[1].strip())
        if child:
            parent.children.append(child)
        
        parent.repeat = repeat
        parent.climb_up = climb_up
        return parent

    def _parse_sibling_expression(self, expr: str, repeat: int = 1, climb_up: int = 0) -> Optional[EmmetNode]:
        """Parse expression with sibling operator (+)."""
        parts = expr.split('+', 1)
        if len(parts) != 2:
            return None
        
        # For simplicity, return the first element
        # In a full implementation, you'd want to handle siblings properly
        return self._parse_element(parts[0].strip(), repeat, climb_up)

    def _parse_grouped_expression(self, expr: str, repeat: int = 1, climb_up: int = 0) -> Optional[EmmetNode]:
        """Parse grouped expression with parentheses."""
        # This is a simplified implementation
        # A full parser would handle nested groups properly
        group_match = re.search(r'\(([^)]+)\)', expr)
        if not group_match:
            return None
        
        group_content = group_match.group(1)
        return self._parse_single_expression(group_content)


class EmmetExpander:
    """Expand Emmet nodes into HTML with Jinja2 template support."""
    
    def __init__(self):
        self.parser = EmmetParser()
        self.tab_stops = []
        self.current_tab_stop = 1

    def expand(self, abbreviation: str, with_jinja: bool = False) -> str:
        """Expand an Emmet abbreviation to HTML."""
        nodes = self.parser.parse(abbreviation)
        if not nodes:
            return ""
        
        self.tab_stops = []
        self.current_tab_stop = 1
        
        result = ""
        for node in nodes:
            result += self._expand_node(node, with_jinja)
        
        # Add final tab stop
        if '$0' not in result:
            result += '$0'
        
        return result

    def _expand_node(self, node: EmmetNode, with_jinja: bool = False, indent: int = 0) -> str:
        """Expand a single node to HTML."""
        if node.tag == 'snippet':
            return node.content
        
        result = ""
        indent_str = "    " * indent
        
        for i in range(node.repeat):
            # Handle numbered placeholders in repeated elements
            multiplier_suffix = f"{i + 1}" if node.repeat > 1 else ""
            
            # Start tag
            tag_str = self._build_start_tag(node, multiplier_suffix, with_jinja)
            
            if node.tag in self.parser.void_elements:
                result += f"{indent_str}{tag_str}\n"
            else:
                result += f"{indent_str}{tag_str}"
                
                # Content or tab stop
                if node.content:
                    content = node.content
                    if multiplier_suffix:
                        content = content.replace('$', f'${multiplier_suffix}')
                    result += content
                elif not node.children:
                    result += f"${self.current_tab_stop}"
                    self.current_tab_stop += 1
                
                # Children
                if node.children:
                    result += "\n"
                    for child in node.children:
                        result += self._expand_node(child, with_jinja, indent + 1)
                    result += indent_str
                
                # End tag
                result += f"</{node.tag}>"
                
                if i < node.repeat - 1 or indent > 0:
                    result += "\n"
        
        return result

    def _build_start_tag(self, node: EmmetNode, multiplier_suffix: str = "", with_jinja: bool = False) -> str:
        """Build the opening tag with attributes."""
        tag = f"<{node.tag}"
        
        # ID attribute
        if node.id:
            id_value = node.id
            if multiplier_suffix:
                id_value += multiplier_suffix
            tag += f' id="{id_value}"'
        
        # Class attribute
        if node.classes:
            classes_str = " ".join(node.classes)
            tag += f' class="{classes_str}"'
        
        # Other attributes
        for key, value in node.attributes.items():
            if value:
                attr_value = value
                if multiplier_suffix and '$' in value:
                    attr_value = value.replace('$', multiplier_suffix)
                tag += f' {key}="{attr_value}"'
            else:
                tag += f' {key}'
        
        # Add common Jinja2 attributes if requested
        if with_jinja and node.tag in ['input', 'select', 'textarea', 'form']:
            if node.tag == 'form' and 'method' not in node.attributes:
                tag += ' method="post"'
        
        tag += ">"
        return tag

    def get_completions(self, prefix: str) -> List[Dict[str, str]]:
        """Get Emmet completion suggestions for a prefix."""
        completions = []
        
        # Tag completions
        for tag in self.parser.html5_tags:
            if tag.startswith(prefix.lower()):
                completions.append({
                    'label': tag,
                    'kind': 'Keyword',
                    'detail': 'HTML tag',
                    'insert_text': f'{tag}>$1</{tag}>$0' if tag not in self.parser.void_elements else f'{tag}>',
                    'documentation': f'HTML <{tag}> element'
                })
        
        # Emmet abbreviation completions
        emmet_patterns = [
            ('div.class', 'div with class'),
            ('div#id', 'div with ID'),
            ('ul>li*3', 'unordered list with 3 items'),
            ('table>tr>td*3', 'table with row and 3 cells'),
            ('form>input[type=text]+input[type=submit]', 'form with text input and submit button'),
            ('nav>ul>li*5>a', 'navigation with 5 menu items'),
            ('header+main+footer', 'page structure'),
            ('article>h1+p*3', 'article with heading and paragraphs'),
            ('section.container>div.row>div.col*3', 'grid layout'),
            ('img[src alt]', 'image with attributes'),
        ]
        
        for pattern, description in emmet_patterns:
            if pattern.startswith(prefix.lower()) or prefix.lower() in pattern:
                expanded = self.expand(pattern)
                completions.append({
                    'label': pattern,
                    'kind': 'Snippet',
                    'detail': description,
                    'insert_text': expanded,
                    'documentation': f'Emmet: {pattern}\n\nExpands to:\n{expanded[:200]}...' if len(expanded) > 200 else f'Emmet: {pattern}\n\nExpands to:\n{expanded}'
                })
        
        return completions


class JinjaEmmetIntegration:
    """Integration layer for Emmet with Jinja2 templates."""
    
    def __init__(self):
        self.expander = EmmetExpander()
        
        # Jinja2-aware Emmet snippets
        self.jinja_snippets = {
            'for': '{% for $1 in $2 %}\n    $3\n{% endfor %}$0',
            'if': '{% if $1 %}\n    $2\n{% endif %}$0',
            'ifelse': '{% if $1 %}\n    $2\n{% else %}\n    $3\n{% endif %}$0',
            'block': '{% block $1 %}\n    $2\n{% endblock %}$0',
            'extend': '{% extends "$1" %}$0',
            'include': '{% include "$1" %}$0',
            'set': '{% set $1 = $2 %}$0',
            'macro': '{% macro $1($2) %}\n    $3\n{% endmacro %}$0',
            'call': '{% call $1($2) %}\n    $3\n{% endcall %}$0',
            'with': '{% with $1 = $2 %}\n    $3\n{% endwith %}$0',
            'comment': '{# $1 #}$0',
            'var': '{{ $1 }}$0',
            'filter': '{{ $1|$2 }}$0',
            'url': '{{ url_for("$1") }}$0',
            'csrf': '<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>$0',
        }
    
    def expand_with_jinja_context(self, abbreviation: str, context: Dict[str, str] = None) -> str:
        """Expand Emmet abbreviation with Jinja2 context awareness."""
        if abbreviation in self.jinja_snippets:
            return self.jinja_snippets[abbreviation]
        
        # Check for Jinja2 enhanced patterns
        if abbreviation.startswith('j:'):
            return self._expand_jinja_pattern(abbreviation[2:], context or {})
        
        # Regular Emmet expansion with Jinja2 enhancements
        return self.expander.expand(abbreviation, with_jinja=True)
    
    def _expand_jinja_pattern(self, pattern: str, context: Dict[str, str]) -> str:
        """Expand Jinja2-specific patterns."""
        jinja_patterns = {
            'form': '<form method="post">\n    {{ csrf_token() }}\n    $1\n    <input type="submit" value="$2">\n</form>$0',
            'table': '{% for item in $1 %}\n<tr>\n    <td>{{ item.$2 }}</td>\n</tr>\n{% endfor %}$0',
            'list': '{% for item in $1 %}\n<li>{{ item }}</li>\n{% endfor %}$0',
            'select': '<select name="$1">\n{% for option in $2 %}\n    <option value="{{ option.value }}">{{ option.label }}</option>\n{% endfor %}\n</select>$0',
            'if-form': '{% if form.$1.errors %}\n    <div class="error">{{ form.$1.errors[0] }}</div>\n{% endif %}\n{{ form.$1 }}$0',
        }
        
        return jinja_patterns.get(pattern, pattern)
    
    def get_jinja_completions(self, prefix: str) -> List[Dict[str, str]]:
        """Get Jinja2-aware completions."""
        completions = []
        
        # Jinja2 snippet completions
        for snippet_key, snippet_value in self.jinja_snippets.items():
            if snippet_key.startswith(prefix.lower()):
                completions.append({
                    'label': snippet_key,
                    'kind': 'Snippet',
                    'detail': 'Jinja2 snippet',
                    'insert_text': snippet_value,
                    'documentation': f'Jinja2 snippet: {snippet_key}'
                })
        
        # Enhanced Emmet completions
        emmet_completions = self.expander.get_completions(prefix)
        
        # Add Jinja2 enhanced patterns
        if prefix.startswith('j:'):
            jinja_patterns = [
                ('j:form', 'Jinja2 form with CSRF'),
                ('j:table', 'Jinja2 table iteration'),
                ('j:list', 'Jinja2 list iteration'),
                ('j:select', 'Jinja2 select with options'),
                ('j:if-form', 'Jinja2 form field with error handling'),
            ]
            
            for pattern, description in jinja_patterns:
                if pattern.startswith(prefix.lower()):
                    expanded = self.expand_with_jinja_context(pattern)
                    completions.append({
                        'label': pattern,
                        'kind': 'Snippet',
                        'detail': description,
                        'insert_text': expanded,
                        'documentation': f'Jinja2 Emmet: {pattern}'
                    })
        
        return completions + emmet_completions


# Global instance for easy access
emmet_integration = JinjaEmmetIntegration()