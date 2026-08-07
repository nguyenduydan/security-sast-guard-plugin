"""Tests for ASTContextEngine scope resolution."""

from src.domain.ast_context_engine import ASTContextEngine


def test_resolve_html_inline_event_scope():
    engine = ASTContextEngine()
    line = '<button onclick="switchTab(\'profile\')">Tab</button>'
    scope = engine.resolve_scope("index.html", 10, line)
    assert scope == "html-inline-event"


def test_resolve_js_regex_scope():
    engine = ASTContextEngine()
    line = "var matches = filenameRegex.exec(disposition);"
    scope = engine.resolve_scope("download.js", 20, line)
    assert scope == "client-js-regex"


def test_resolve_server_code_scope():
    engine = ASTContextEngine()
    line = 'import subprocess\nsubprocess.run(["ls"])'
    scope = engine.resolve_scope("app.py", 5, line)
    assert scope == "server-code"
