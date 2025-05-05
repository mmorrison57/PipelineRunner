# Coding Standards for MCP Project

## General Guidelines
- Use clear and concise comments to explain complex logic.
- Follow consistent indentation and formatting rules.
- Use meaningful variable and function names.

## Python Guidelines
- Use Python 3.9 or later.
- Follow PEP 8 style guide for Python code.
- Use type hints for function signatures and variables.
- Prefer list comprehensions over loops for simple transformations.
- Use `logging` module for logging instead of `print` statements.

## Error Handling
- Use `try`/`except` blocks to handle exceptions.
- Log all exceptions with meaningful messages.
- Avoid catching generic exceptions (e.g., `except Exception:`).

## Version Control
- Commit code frequently with meaningful commit messages.
- Use feature branches for new features and bug fixes.
- Rebase feature branches before merging into the main branch.

## Testing
- Write unit tests for all new code.
- Use `pytest` as the testing framework.
- Ensure all tests pass before merging code.

## Documentation
- Use docstrings to document functions, classes, and modules.
- Maintain an up-to-date README file with project information.
- Document any external dependencies and how to install them.