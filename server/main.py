#!/usr/bin/env python3
"""
Jinja2 HTML Language Server
A language server for Jinja2 HTML templates with auto-completion, diagnostics, and Emmet support.
"""

import asyncio
import logging
import sys
from typing import List, Optional, Dict, Any, Union
import re
import json
from pathlib import Path

from pygls.server import LanguageServer
from pygls.workspace import Document
from lsprotocol.types import (
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionParams,
    Diagnostic,
    DiagnosticSeverity,
    DidChangeTextDocumentParams,
    DidOpenTextDocumentParams,
    HoverParams,
    Hover,
    MarkupContent,
    MarkupKind,
    Position,
    Range,
    TextEdit,
    InsertTextFormat,
    CompletionTriggerKind,
    DocumentFormattingParams,
    FormattingOptions
)

try:
    from .completion_provider import Jinja2HTMLCompletionProvider
    from .emmet_support import emmet_integration
except ImportError:
    from completion_provider import Jinja2HTMLCompletionProvider
    from emmet_support import emmet_integration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jinja2-html-lsp.log'),
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger(__name__)

class Jinja2HTMLLanguageServer(LanguageServer):
    """Language server for Jinja2 HTML templates."""
    
    def __init__(self):
        super().__init__("jinja2-html-lsp", "0.1.0")
        
        # Initialize completion provider
        self.completion_provider = Jinja2HTMLCompletionProvider()
        
        # Initialize emmet integration
        self.emmet = emmet_integration
        
        # Cache for document analysis
        self._document_cache = {}

    def get_completion_items(self, document: Document, position: Position) -> List[CompletionItem]:
        """Generate completion items using the enhanced completion provider."""
        line = document.lines[position.line]
        
        # Analyze completion context
        request = self.completion_provider.analyze_completion_context(line, position.character)
        
        # Get completions from the provider
        completions = self.completion_provider.provide_completions(request, document.source)
        
        return completions

    def validate_document(self, document: Document) -> List[Diagnostic]:
        """Validate the document and return diagnostics."""
        diagnostics = []
        lines = document.lines
        
        for line_num, line in enumerate(lines):
            # Check for unclosed Jinja2 blocks
            if '{{' in line and '}}' not in line:
                diagnostics.append(Diagnostic(
                    range=Range(
                        start=Position(line=line_num, character=line.find('{{')),
                        end=Position(line=line_num, character=len(line))
                    ),
                    message="Unclosed Jinja2 expression",
                    severity=DiagnosticSeverity.Error
                ))
            
            if '{%' in line and '%}' not in line:
                diagnostics.append(Diagnostic(
                    range=Range(
                        start=Position(line=line_num, character=line.find('{%')),
                        end=Position(line=line_num, character=len(line))
                    ),
                    message="Unclosed Jinja2 statement",
                    severity=DiagnosticSeverity.Error
                ))
            
            # Check for unclosed HTML tags (basic check)
            open_tags = re.findall(r'<([a-zA-Z]+)', line)
            close_tags = re.findall(r'</([a-zA-Z]+)', line)
            
            for tag in open_tags:
                if tag not in ['br', 'hr', 'img', 'input', 'meta', 'link']:  # Self-closing tags
                    if tag not in close_tags:
                        diagnostics.append(Diagnostic(
                            range=Range(
                                start=Position(line=line_num, character=line.find(f'<{tag}')),
                                end=Position(line=line_num, character=line.find(f'<{tag}') + len(tag) + 1)
                            ),
                            message=f"Unclosed HTML tag: {tag}",
                            severity=DiagnosticSeverity.Warning
                        ))
        
        return diagnostics


# Create the language server instance
server = Jinja2HTMLLanguageServer()

@server.feature("textDocument/completion")
def completion(params: CompletionParams) -> CompletionList:
    """Provide completion items."""
    document = server.workspace.get_document(params.text_document.uri)
    items = server.get_completion_items(document, params.position)
    
    return CompletionList(
        is_incomplete=False,
        items=items
    )

@server.feature("textDocument/hover")
def hover(params: HoverParams) -> Optional[Hover]:
    """Provide hover information."""
    document = server.workspace.get_document(params.text_document.uri)
    line = document.lines[params.position.line]
    
    # Get word at position
    word_start = params.position.character
    word_end = params.position.character
    
    while word_start > 0 and line[word_start - 1].isalnum():
        word_start -= 1
    while word_end < len(line) and line[word_end].isalnum():
        word_end += 1
    
    word = line[word_start:word_end]
    
    # Check Jinja2 filters
    filter_info = server.completion_provider.jinja2_filters.get(word)
    if filter_info:
        args_info = ""
        if 'args' in filter_info:
            args_info = f"\n\n**Arguments:** {', '.join(filter_info['args'])}"
        
        return Hover(
            contents=MarkupContent(
                kind=MarkupKind.Markdown,
                value=f"**Jinja2 Filter: {word}**\n\n{filter_info['description']}{args_info}"
            )
        )
    
    # Check Jinja2 functions
    func_info = server.completion_provider.jinja2_functions.get(word)
    if func_info:
        args_info = ""
        if 'args' in func_info:
            args_info = f"\n\n**Arguments:** {', '.join(func_info['args'])}"
        
        return Hover(
            contents=MarkupContent(
                kind=MarkupKind.Markdown,
                value=f"**Jinja2 Function: {word}**\n\n{func_info['description']}{args_info}"
            )
        )
    
    # Check Jinja2 keywords
    keyword_info = server.completion_provider.jinja2_keywords.get(word)
    if keyword_info:
        return Hover(
            contents=MarkupContent(
                kind=MarkupKind.Markdown,
                value=f"**Jinja2 Keyword: {word}**\n\n{keyword_info['description']}"
            )
        )
    
    # Check HTML tags
    tag_info = server.completion_provider.html_tags.get(word)
    if tag_info:
        attrs_info = ""
        if 'attributes' in tag_info:
            attrs_info = f"\n\n**Common attributes:** {', '.join(tag_info['attributes'])}"
        
        return Hover(
            contents=MarkupContent(
                kind=MarkupKind.Markdown,
                value=f"**HTML Element: <{word}>**\n\n{tag_info.get('description', f'HTML {word} element')}{attrs_info}"
            )
        )
    
    return None

@server.feature("textDocument/didOpen")
def did_open(params: DidOpenTextDocumentParams):
    """Handle document open event."""
    document = server.workspace.get_document(params.text_document.uri)
    diagnostics = server.validate_document(document)
    server.publish_diagnostics(params.text_document.uri, diagnostics)

@server.feature("textDocument/didChange")
def did_change(params: DidChangeTextDocumentParams):
    """Handle document change event."""
    document = server.workspace.get_document(params.text_document.uri)
    diagnostics = server.validate_document(document)
    server.publish_diagnostics(params.text_document.uri, diagnostics)

def main():
    """Main entry point for the language server."""
    logger.info("Starting Jinja2 HTML Language Server")
    
    # Start the server
    server.start_io()

if __name__ == "__main__":
    main()