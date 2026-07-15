import os
import json
from click.testing import CliRunner
from zenith.scanner.secrets import DependencyScanner
from zenith.ai.inference import _parse_output_static
from zenith.cli import scan

def test_recursive_dependency_scanner(tmp_path):
    # Setup mock .git and package.json at root
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    
    pkg = tmp_path / "package.json"
    pkg.write_text(json.dumps({"dependencies": {"boto3": "1.0.0", "stripe": "^8.0"}}), encoding="utf-8")
    
    # Create deeply nested directory simulating a file being edited
    nested = tmp_path / "src" / "lib" / "deep"
    nested.mkdir(parents=True)
    
    # Execute scanner tracking up from nested
    deps = DependencyScanner.get_all_dependencies(str(nested))
    
    assert "boto3" in deps
    assert "stripe" in deps

def test_binary_file_graceful_cli(tmp_path):
    # Simulate scanning a binary image file
    binary_file = tmp_path / "icon.png"
    binary_file.write_bytes(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\xff')
    
    runner = CliRunner()
    result = runner.invoke(scan, [str(binary_file)])
    
    # The CLI shouldn't crash with UnicodeDecodeError, it should skip gracefully
    assert "Skipping binary or malformed file" in result.output
    assert result.exit_code == 0

def test_parse_output_static_garbage_handling():
    # If LLM produces garbage non-JSON text, test our fallback heuristics
    garbage_output = "I am an AI, the answer is Yes! 100% confidence"
    
    # 1. Test heuristic logic overrides (contains 'test' string)
    snippet_test = 'password = "test_123"'
    res_test = _parse_output_static(garbage_output, snippet_test)
    assert res_test["is_live"] is False
    assert res_test["confidence"] == 0.5
    assert "AI Parsing Error" in res_test["reason"]
    
    # 2. Prod heuristic logic
    snippet_prod = 'aws_secret_key = "AKIAIOSFODNN7ABCD123"'
    res_prod = _parse_output_static(garbage_output, snippet_prod)
    assert res_prod["is_live"] is True
