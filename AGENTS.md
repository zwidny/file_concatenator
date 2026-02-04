# AGENTS.md - Development Guide for file_concatenator

This document provides guidelines for AI agents working on the `file_concatenator` project.

## Project Overview

`file_concatenator` is a Python tool that converts directory structures and file contents into a single Markdown file. It supports recursive traversal, automatic code highlighting, and conversion of binary files (PDF, Word, Excel, etc.) using markitdown.

## Development Environment

### Python Version
- **Python 3.12+** required (specified in `.python-version` and `pyproject.toml`)
- Uses `uv` for dependency management (see `uv.lock`)
- Virtual environment: `.venv/`

### Project Structure
```
file_concatenator/
├── src/file_concatenator/
│   ├── __init__.py      # Package exports (main, DirectoryToMarkdown)
│   ├── core.py          # Core processing logic (528 lines)
│   └── cli.py           # Command-line interface (65 lines)
├── pyproject.toml       # Project configuration
├── README.md           # Documentation (Chinese)
└── ._combined.md       # Example output
```

## Build, Test, and Lint Commands

### Installation & Setup
```bash
# Install with dev dependencies (using uv)
uv sync --dev

# Or install with pip (if uv not available)
pip install -e ".[dev]"
```

### Building
```bash
# Build package
python -m build

# Build wheel only
python -m build --wheel

# Clean build artifacts
rm -rf dist/ build/ *.egg-info/
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=file_concatenator

# Run specific test file (when tests exist)
pytest tests/test_core.py

# Run single test function
pytest tests/test_core.py::test_function_name -v

# Run tests with verbose output
pytest -v

# Run tests and show coverage report
pytest --cov=file_concatenator --cov-report=term-missing
```

### Linting & Formatting
```bash
# Run ruff linter
ruff check .

# Fix linting issues automatically
ruff check --fix .

# Run ruff formatter
ruff format .

# Check formatting without applying
ruff format --check .

# Run black formatter
black .

# Check black formatting
black --check .

# Run mypy type checking
mypy src/

# Run all checks at once
ruff check . && ruff format --check . && mypy src/ && black --check .
```

### Quality Assurance Checklist
Before committing changes, always run:
```bash
# Complete quality check
ruff check . && ruff format --check . && mypy src/ && black --check . && pytest
```

## Code Style Guidelines

### Import Organization
```python
# Standard library imports
import os
import re
import fnmatch
from datetime import datetime
from typing import List, Optional, Dict, Any

# Third-party imports
# (none currently besides markitdown in core.py)

# Local imports
from .core import DirectoryToMarkdown
```

**Rules:**
1. Group imports: stdlib → third-party → local
2. Use absolute imports within package: `from .core import DirectoryToMarkdown`
3. Avoid wildcard imports (`from module import *`)
4. Import only what's needed

### Type Annotations
```python
def process(self, input_dir: str, output_file: str) -> bool:
    """处理目录并生成Markdown文件"""
    
def _load_ignore_patterns(self) -> List[str]:
    """加载所有忽略模式"""
    
def _should_ignore(self, path: str, relative_path: str, ignore_patterns: List[str]) -> bool:
```

**Rules:**
1. Use `typing` module for complex types: `List[str]`, `Dict[str, Any]`, `Optional[str]`
2. Always annotate function parameters and return types
3. Use `Optional[T]` for values that can be `None`
4. Use `Any` sparingly; prefer specific types when possible
5. Enable strict type checking: `disallow_untyped_defs = true` in mypy config

### Naming Conventions
```python
# Classes: PascalCase
class DirectoryToMarkdown:

# Methods and functions: snake_case
def process_directory(self, path: str):
def _private_helper_method(self):

# Constants: UPPER_SNAKE_CASE
DEFAULT_IGNORE_PATTERNS = [".git", "__pycache__"]

# Variables: snake_case
file_size = os.path.getsize(filepath)
ignore_patterns = []
```

**Rules:**
1. Public methods: descriptive snake_case
2. Private methods: prefix with underscore `_`
3. Class names: PascalCase
4. Module-level constants: UPPER_SNAKE_CASE
5. Variable names: descriptive snake_case

### Error Handling
```python
try:
    with open(filepath, "r", encoding=encoding) as f:
        return f.read()
except (UnicodeDecodeError, LookupError):
    continue
except Exception as e:
    if self.verbose:
        print(f"✗ 读取忽略文件时出错: {str(e)}")
    return None
```

**Rules:**
1. Use specific exception types when possible
2. Catch multiple exceptions with tuple: `except (TypeError, ValueError):`
3. Provide meaningful error messages
4. Use `self.verbose` flag for debug output
5. Return `None` or default values for recoverable errors

### Documentation
```python
def process(self, input_dir: str, output_file: str) -> bool:
    """处理目录并生成Markdown文件
    
    Args:
        input_dir: 要处理的目录路径
        output_file: 输出Markdown文件路径
        
    Returns:
        bool: 处理是否成功
        
    Raises:
        FileNotFoundError: 当输入目录不存在时
    """
```

**Rules:**
1. Write docstrings for all public classes and methods
2. Use triple quotes with proper indentation
3. Document parameters, return values, and exceptions
4. Keep comments in Chinese (matching existing codebase)
5. Use `Args:`, `Returns:`, `Raises:` sections for complex methods

### Formatting Rules
- **Line length**: 128 characters (configured in black and ruff)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for docstrings, single quotes for strings
- **Trailing commas**: Include in multi-line collections
- **Blank lines**: 
  - 2 blank lines between top-level definitions
  - 1 blank line between methods
  - No blank line at end of file

### File Organization
1. Keep related functionality together in modules
2. Separate CLI logic from core business logic
3. Use `__init__.py` for package exports
4. Follow the existing pattern: core logic in `core.py`, CLI in `cli.py`

## Project-Specific Patterns

### Chinese Language Support
- Code comments and user messages are in Chinese
- Error messages should be bilingual or Chinese-only
- Keep Chinese comments when modifying existing code

### File Processing Patterns
```python
# Pattern for recursive directory traversal
for root, dirs, files in os.walk(input_dir):
    # Filter ignored directories
    dirs[:] = [d for d in dirs if not self._should_ignore(...)]
    
    # Process files
    for filename in files:
        self._process_file(...)
```

### Configuration Management
- All tool configuration is in `pyproject.toml`
- No separate config files for black, ruff, mypy
- Version pinning in `uv.lock`

## Git Workflow

### Commit Messages
- Use descriptive commit messages
- Reference issues when applicable
- Keep commits focused on single changes

### Branching
- `main` branch for stable releases
- Feature branches for development
- Follow semantic versioning for releases

## Release Process

1. Update version in `src/file_concatenator/__init__.py`
2. Update version in `pyproject.toml`
3. Run full test suite: `pytest`
4. Run all linting: `ruff check . && ruff format --check . && mypy src/`
5. Build package: `python -m build`
6. Test installation: `pip install dist/*.whl`
7. Create git tag: `git tag v1.0.x`
8. Push to repository

## Troubleshooting

### Common Issues
1. **Import errors**: Ensure working from project root, virtual environment activated
2. **Type errors**: Run `mypy src/` to identify issues
3. **Formatting issues**: Run `ruff format .` to fix automatically
4. **Test failures**: Check pytest output for specific error details

### Performance Considerations
- The tool processes potentially large directory structures
- Use generators and lazy evaluation where appropriate
- Be mindful of memory usage when processing large files
- Implement proper error handling for file system operations

## Additional Resources

- [Python Packaging User Guide](https://packaging.python.org/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Black Code Style](https://black.readthedocs.io/)
- [mypy Type Checking](https://mypy.readthedocs.io/)
- [pytest Testing Framework](https://docs.pytest.org/)