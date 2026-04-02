---
applyTo: "**/*.py"
---

# Python Coding Conventions

## Naming Conventions

- Use snake_case for variables and functions
- Use PascalCase for class names
- Use UPPERCASE for constants

## Code Style

- Follow PEP 8 style guidelines
- Limit line length to 88 characters (ruff format standard)
- Use type hints for function signatures
- In _PYSCRIPT_CODE blocks, use type hints for function signatures
- In scripts/**/*.py, use the `uv run --script` shebang and include PEP 723 Inline Script Metadata (/// script) for dependencies and Python version requirements
- Use `int | None` union syntax (Python 3.10+) rather than `Optional[int]`

## Docstrings

- Every public function and class should have a docstring
- Use a single-line docstring for trivial functions
- Use multi-line Google-style docstrings for non-trivial functions:
  - First line: brief imperative summary
  - `Args:` section for parameters that are not self-explanatory
  - `Returns:` section when the return value is not obvious

## Best Practices

- Python code will be linted and formatted with ruff check and ruff format
- **Always run `ruff check .` and `ruff format .` before creating a PR.**  Fix every
  violation before pushing.  Never suppress a ruff rule with `# noqa` unless there
  is a documented reason.
- Ruff check and ruff format will be run as pre-commit hooks to ensure code quality before commits
- Read the ruff configuration from pyproject.toml
- Use assignment expressions (the walrus operator) for concise code when appropriate
- Use dict, list, and set comprehensions for simple transformations
- Avoid using mutable default arguments in functions
- Where possible, function arguments should have just one datatype except where that would create a mutable default argument
- Use meaningful variable and function names
- Avoid string concatenation with the + operator
- Prefer f-strings for string formatting
- Use context managers (with statements) for resource management
- Prefer `pathlib.Path` over `os.path` for file system operations
- Avoid bare `except` clauses; catch specific exception types
- Use ASCII characters in docstrings and comments (e.g. `x` not `×`)

## Dependency Management

- `pytest` must be listed in **both** `[project.optional-dependencies].test`
  **and** `[dependency-groups].test` in `pyproject.toml`.
  - `pip install .[test]` reads `[project.optional-dependencies]` (used by
    GitHub Actions CI).
  - `uv` reads `[dependency-groups]` (used for local development).
  - Both must be kept in sync so pytest is available in all environments.

```python
# Avoid
file = open('data.txt')
content = file.read()
file.close()

# Prefer
with open('data.txt') as file:
    content = file.read()
```

```python
# Avoid
def func(names: list[str] = []) -> None:

# Prefer
def func(names: list[str] | None = None) -> None:
    names = names or []
