#!/usr/bin/env python3
"""
Test script for Jinja2 HTML Language Server
This script provides comprehensive testing for all LSP server functionality.
"""

import sys
import json
import asyncio
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from typing import List, Dict, Any

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent))

from lsprotocol.types import (
    Position,
    Range,
    CompletionParams,
    CompletionTriggerKind,
    TextDocumentIdentifier,
    HoverParams,
    DidOpenTextDocumentParams,
    TextDocumentItem,
    DidChangeTextDocumentParams,
    VersionedTextDocumentIdentifier,
    TextDocumentContentChangeEvent
)

from main import Jinja2HTMLLanguageServer, server
from completion_provider import Jinja2HTMLCompletionProvider, CompletionContext
from emmet_support import EmmetExpander, EmmetParser, JinjaEmmetIntegration


class MockDocument:
    """Mock document for testing."""
    
    def __init__(self, source: str, uri: str = "file:///test.html.j2"):
        self.source = source
        self.uri = uri
        self.lines = source.split('\n')


class TestEmmetParser(unittest.TestCase):
    """Test Emmet parsing functionality."""
    
    def setUp(self):
        self.parser = EmmetParser()
    
    def test_simple_tag_parsing(self):
        """Test parsing simple HTML tags."""
        nodes = self.parser.parse("div")
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].tag, "div")
        self.assertEqual(nodes[0].classes, [])
        self.assertIsNone(nodes[0].id)
    
    def test_class_parsing(self):
        """Test parsing elements with classes."""
        nodes = self.parser.parse("div.container.main")
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].tag, "div")
        self.assertEqual(nodes[0].classes, ["container", "main"])
    
    def test_id_parsing(self):
        """Test parsing elements with IDs."""
        nodes = self.parser.parse("div#header")
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].tag, "div")
        self.assertEqual(nodes[0].id, "header")
    
    def test_attribute_parsing(self):
        """Test parsing elements with attributes."""
        nodes = self.parser.parse("input[type=text name=username]")
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].tag, "input")
        self.assertEqual(nodes[0].attributes["type"], "text")
        self.assertEqual(nodes[0].attributes["name"], "username")
    
    def test_content_parsing(self):
        """Test parsing elements with content."""
        nodes = self.parser.parse("p{Hello World}")
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].tag, "p")
        self.assertEqual(nodes[0].content, "Hello World")
    
    def test_multiplication(self):
        """Test element multiplication."""
        nodes = self.parser.parse("li*3")
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].tag, "li")
        self.assertEqual(nodes[0].repeat, 3)
    
    def test_child_operator(self):
        """Test child operator parsing."""
        nodes = self.parser.parse("ul>li")
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].tag, "ul")
        self.assertEqual(len(nodes[0].children), 1)
        self.assertEqual(nodes[0].children[0].tag, "li")


class TestEmmetExpander(unittest.TestCase):
    """Test Emmet expansion functionality."""
    
    def setUp(self):
        self.expander = EmmetExpander()
    
    def test_simple_expansion(self):
        """Test simple tag expansion."""
        result = self.expander.expand("div")
        self.assertIn("<div>", result)
        self.assertIn("</div>", result)
        self.assertIn("$", result)  # Should contain tab stops
    
    def test_class_expansion(self):
        """Test class expansion."""
        result = self.expander.expand("div.container")
        self.assertIn('class="container"', result)
    
    def test_id_expansion(self):
        """Test ID expansion."""
        result = self.expander.expand("div#header")
        self.assertIn('id="header"', result)
    
    def test_attribute_expansion(self):
        """Test attribute expansion."""
        result = self.expander.expand("input[type=text]")
        self.assertIn('type="text"', result)
    
    def test_multiplication_expansion(self):
        """Test multiplication expansion."""
        result = self.expander.expand("li*3")
        # Should contain multiple <li> tags
        self.assertEqual(result.count("<li>"), 3)
        self.assertEqual(result.count("</li>"), 3)
    
    def test_nested_expansion(self):
        """Test nested element expansion."""
        result = self.expander.expand("ul>li")
        self.assertIn("<ul>", result)
        self.assertIn("<li>", result)
        self.assertIn("</li>", result)
        self.assertIn("</ul>", result)
    
    def test_void_elements(self):
        """Test void element expansion."""
        result = self.expander.expand("img[src=test.jpg alt=Test]")
        self.assertIn("<img", result)
        self.assertNotIn("</img>", result)  # Void elements shouldn't have closing tags
    
    def test_snippet_expansion(self):
        """Test predefined snippet expansion."""
        result = self.expander.expand("!")
        self.assertIn("<!DOCTYPE html>", result)
        self.assertIn("<html", result)
        self.assertIn("<head>", result)
        self.assertIn("<body>", result)


class TestJinjaEmmetIntegration(unittest.TestCase):
    """Test Jinja2-Emmet integration."""
    
    def setUp(self):
        self.integration = JinjaEmmetIntegration()
    
    def test_jinja_snippet_expansion(self):
        """Test Jinja2 snippet expansion."""
        result = self.integration.expand_with_jinja_context("for")
        self.assertIn("{% for", result)
        self.assertIn("{% endfor %}", result)
    
    def test_if_snippet_expansion(self):
        """Test if statement expansion."""
        result = self.integration.expand_with_jinja_context("if")
        self.assertIn("{% if", result)
        self.assertIn("{% endif %}", result)
    
    def test_block_snippet_expansion(self):
        """Test block expansion."""
        result = self.integration.expand_with_jinja_context("block")
        self.assertIn("{% block", result)
        self.assertIn("{% endblock %}", result)
    
    def test_jinja_enhanced_patterns(self):
        """Test Jinja2 enhanced patterns."""
        result = self.integration.expand_with_jinja_context("j:form")
        self.assertIn("<form", result)
        self.assertIn("csrf_token", result)
        self.assertIn("method=\"post\"", result)
    
    def test_variable_expansion(self):
        """Test variable expansion."""
        result = self.integration.expand_with_jinja_context("var")
        self.assertIn("{{", result)
        self.assertIn("}}", result)
    
    def test_comment_expansion(self):
        """Test comment expansion."""
        result = self.integration.expand_with_jinja_context("comment")
        self.assertIn("{#", result)
        self.assertIn("#}", result)


class TestCompletionProvider(unittest.TestCase):
    """Test completion provider functionality."""
    
    def setUp(self):
        self.provider = Jinja2HTMLCompletionProvider()
    
    def test_context_detection_html(self):
        """Test HTML context detection."""
        request = self.provider.analyze_completion_context("<div", 4)
        self.assertEqual(request.context, CompletionContext.HTML)
    
    def test_context_detection_jinja_expression(self):
        """Test Jinja2 expression context detection."""
        request = self.provider.analyze_completion_context("{{ user.", 7)
        self.assertEqual(request.context, CompletionContext.JINJA_EXPRESSION)
    
    def test_context_detection_jinja_statement(self):
        """Test Jinja2 statement context detection."""
        request = self.provider.analyze_completion_context("{% for ", 7)
        self.assertEqual(request.context, CompletionContext.JINJA_STATEMENT)
    
    def test_context_detection_jinja_comment(self):
        """Test Jinja2 comment context detection."""
        request = self.provider.analyze_completion_context("{# comment ", 11)
        self.assertEqual(request.context, CompletionContext.JINJA_COMMENT)
    
    def test_attribute_name_context(self):
        """Test HTML attribute name context detection."""
        request = self.provider.analyze_completion_context("<div class", 10)
        self.assertEqual(request.context, CompletionContext.ATTRIBUTE_NAME)
    
    def test_attribute_value_context(self):
        """Test HTML attribute value context detection."""
        request = self.provider.analyze_completion_context('<div class="', 12)
        self.assertEqual(request.context, CompletionContext.ATTRIBUTE_VALUE)
    
    def test_html_completions(self):
        """Test HTML tag completions."""
        request = self.provider.analyze_completion_context("<di", 3)
        request.word = "di"
        completions = self.provider._get_html_completions(request)
        
        # Should include div
        div_completions = [c for c in completions if c.label == "div"]
        self.assertTrue(len(div_completions) > 0)
    
    def test_jinja_expression_completions(self):
        """Test Jinja2 expression completions."""
        document_content = "{{ user.name }}\n{% for item in items %}"
        request = self.provider.analyze_completion_context("{{ use", 5)
        request.word = "use"
        completions = self.provider._get_jinja_expression_completions(request, document_content)
        
        # Should include variables and filters
        labels = [c.label for c in completions]
        self.assertIn("user", labels)  # Variable
        # Should also include filters starting with "use" if any
    
    def test_jinja_statement_completions(self):
        """Test Jinja2 statement completions."""
        request = self.provider.analyze_completion_context("{% fo", 5)
        request.word = "fo"
        completions = self.provider._get_jinja_statement_completions(request, "")
        
        # Should include "for" keyword
        labels = [c.label for c in completions]
        self.assertIn("for", labels)
    
    def test_variable_extraction(self):
        """Test variable extraction from templates."""
        template = """
        {{ user.name }}
        {% for item in items %}
            {{ item.title|upper }}
        {% endfor %}
        {% set total = items|length %}
        """
        
        variables = self.provider._extract_variables(template)
        expected_vars = {"user", "item", "items", "total"}
        self.assertTrue(expected_vars.issubset(variables))
    
    def test_css_class_extraction(self):
        """Test CSS class extraction."""
        template = '''
        <div class="container main">
        <span class="highlight">
        '''
        
        classes = self.provider._extract_css_classes(template)
        expected_classes = {"container", "main", "highlight"}
        self.assertTrue(expected_classes.issubset(classes))
    
    def test_css_id_extraction(self):
        """Test CSS ID extraction."""
        template = '''
        <div id="header">
        <section id="content">
        '''
        
        ids = self.provider._extract_css_ids(template)
        expected_ids = {"header", "content"}
        self.assertTrue(expected_ids.issubset(ids))


class TestLanguageServer(unittest.TestCase):
    """Test language server functionality."""
    
    def setUp(self):
        self.server = Jinja2HTMLLanguageServer()
    
    def test_server_initialization(self):
        """Test server initialization."""
        self.assertIsNotNone(self.server.completion_provider)
        self.assertIsNotNone(self.server.emmet)
    
    def test_completion_items_generation(self):
        """Test completion items generation."""
        document = MockDocument('<div class="test">')
        position = Position(line=0, character=15)
        
        items = self.server.get_completion_items(document, position)
        self.assertIsInstance(items, list)
    
    def test_document_validation(self):
        """Test document validation."""
        # Test valid document
        valid_doc = MockDocument('{{ user.name }}')
        diagnostics = self.server.validate_document(valid_doc)
        self.assertIsInstance(diagnostics, list)
        
        # Test invalid document with unclosed Jinja2 block
        invalid_doc = MockDocument('{{ user.name')
        diagnostics = self.server.validate_document(invalid_doc)
        self.assertTrue(len(diagnostics) > 0)
    
    def test_jinja2_context_variables(self):
        """Test Jinja2 context variable extraction."""
        document = MockDocument("""
        {{ user.name }}
        {% for item in items %}
            {{ item.title }}
        {% endfor %}
        """)
        
        variables = self.server.completion_provider._extract_variables(document.source)
        self.assertIn("user", variables)
        self.assertIn("item", variables)
        self.assertIn("items", variables)


class TestLSPProtocol(unittest.TestCase):
    """Test LSP protocol compliance."""
    
    def setUp(self):
        self.server = server  # Use the global server instance
    
    def test_completion_feature(self):
        """Test completion feature."""
        # Mock document
        doc_uri = "file:///test.html.j2"
        
        # Create completion params
        params = CompletionParams(
            text_document=TextDocumentIdentifier(uri=doc_uri),
            position=Position(line=0, character=5)
        )
        
        # Mock workspace.get_document
        with patch.object(self.server.workspace, 'get_document') as mock_get_doc:
            mock_doc = MockDocument('<div>')
            mock_get_doc.return_value = mock_doc
            
            # This would normally be called by the LSP framework
            # We're testing the function directly
            from main import completion
            result = completion(params)
            
            self.assertIsNotNone(result)
            self.assertIsInstance(result.items, list)
    
    def test_hover_feature(self):
        """Test hover feature."""
        doc_uri = "file:///test.html.j2"
        
        params = HoverParams(
            text_document=TextDocumentIdentifier(uri=doc_uri),
            position=Position(line=0, character=5)
        )
        
        with patch.object(self.server.workspace, 'get_document') as mock_get_doc:
            mock_doc = MockDocument('{{ user|title }}')
            mock_get_doc.return_value = mock_doc
            
            from main import hover
            result = hover(params)
            
            # Result can be None if no hover info is available
            if result is not None:
                self.assertIsNotNone(result.contents)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def setUp(self):
        self.server = Jinja2HTMLLanguageServer()
        self.provider = self.server.completion_provider
        self.emmet = self.server.emmet
    
    def test_html_emmet_completion_flow(self):
        """Test complete HTML + Emmet completion flow."""
        # Test HTML context
        document = MockDocument('<div>')
        position = Position(line=0, character=4)
        
        completions = self.server.get_completion_items(document, position)
        self.assertTrue(len(completions) > 0)
        
        # Should include both HTML tags and Emmet snippets
        labels = [c.label for c in completions]
        self.assertTrue(any("div" in label for label in labels))
    
    def test_jinja2_completion_flow(self):
        """Test complete Jinja2 completion flow."""
        # Test Jinja2 expression context
        document = MockDocument('{{ user.')
        position = Position(line=0, character=7)
        
        completions = self.server.get_completion_items(document, position)
        self.assertIsInstance(completions, list)
        
        # Test Jinja2 statement context
        document = MockDocument('{% fo')
        position = Position(line=0, character=5)
        
        completions = self.server.get_completion_items(document, position)
        self.assertTrue(len(completions) > 0)
        
        labels = [c.label for c in completions]
        self.assertIn("for", labels)
    
    def test_mixed_content_completion(self):
        """Test completion in mixed HTML/Jinja2 content."""
        template = """
        <div class="container">
            {% for user in users %}
                <span>{{ user.name|
        """
        
        document = MockDocument(template)
        # Position after the pipe character
        position = Position(line=3, character=32)
        
        completions = self.server.get_completion_items(document, position)
        self.assertTrue(len(completions) > 0)
        
        # Should include Jinja2 filters
        labels = [c.label for c in completions]
        self.assertIn("title", labels)
        self.assertIn("upper", labels)
    
    def test_attribute_completion_flow(self):
        """Test HTML attribute completion flow."""
        # Test attribute name completion
        document = MockDocument('<div ')
        position = Position(line=0, character=5)
        
        completions = self.server.get_completion_items(document, position)
        labels = [c.label for c in completions]
        self.assertIn("class", labels)
        self.assertIn("id", labels)
        
        # Test attribute value completion
        document = MockDocument('<input type="')
        position = Position(line=0, character=13)
        
        completions = self.server.get_completion_items(document, position)
        labels = [c.label for c in completions]
        self.assertIn("text", labels)
        self.assertIn("password", labels)
    
    def test_diagnostic_generation(self):
        """Test diagnostic generation for various error conditions."""
        # Test unclosed Jinja2 expression
        document = MockDocument('{{ user.name')
        diagnostics = self.server.validate_document(document)
        self.assertTrue(len(diagnostics) > 0)
        self.assertEqual(diagnostics[0].message, "Unclosed Jinja2 expression")
        
        # Test unclosed Jinja2 statement
        document = MockDocument('{% for user in users')
        diagnostics = self.server.validate_document(document)
        self.assertTrue(len(diagnostics) > 0)
        self.assertEqual(diagnostics[0].message, "Unclosed Jinja2 statement")
        
        # Test unclosed HTML tag
        document = MockDocument('<div><span>content</div>')
        diagnostics = self.server.validate_document(document)
        # This should generate a warning about unclosed span tag
        span_warnings = [d for d in diagnostics if "span" in d.message]
        self.assertTrue(len(span_warnings) > 0)


def run_performance_tests():
    """Run performance tests for large documents."""
    print("\n" + "="*50)
    print("PERFORMANCE TESTS")
    print("="*50)
    
    import time
    
    # Large template for performance testing
    large_template = """
    <!DOCTYPE html>
    <html>
    <head><title>Test</title></head>
    <body>
    """ + "\n".join([
        f"""
        <div class="item-{i}">
            {{% for user in users %}}
                <span>{{{{ user.name_{i}|title }}}}</span>
                <p>{{{{ user.email_{i}|lower }}}}</p>
            {{% endfor %}}
        </div>
        """ for i in range(100)
    ]) + """
    </body>
    </html>
    """
    
    server = Jinja2HTMLLanguageServer()
    document = MockDocument(large_template)
    
    # Test completion performance
    start_time = time.time()
    for i in range(10):
        position = Position(line=10 + i, character=20)
        completions = server.get_completion_items(document, position)
    completion_time = time.time() - start_time
    
    print(f"Completion time for 10 requests on large document: {completion_time:.3f}s")
    
    # Test validation performance
    start_time = time.time()
    for i in range(5):
        diagnostics = server.validate_document(document)
    validation_time = time.time() - start_time
    
    print(f"Validation time for 5 runs on large document: {validation_time:.3f}s")
    
    # Test variable extraction performance
    start_time = time.time()
    for i in range(10):
        variables = server.completion_provider._extract_variables(large_template)
    extraction_time = time.time() - start_time
    
    print(f"Variable extraction time for 10 runs: {extraction_time:.3f}s")
    print(f"Variables found: {len(variables)}")


def main():
    """Run all tests."""
    print("Jinja2 HTML Language Server - Test Suite")
    print("="*50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestEmmetParser,
        TestEmmetExpander,
        TestJinjaEmmetIntegration,
        TestCompletionProvider,
        TestLanguageServer,
        TestLSPProtocol,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Run performance tests
    run_performance_tests()
    
    # Print summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split(':', 1)[-1].strip()}")
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())