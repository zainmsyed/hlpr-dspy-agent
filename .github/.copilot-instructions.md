# Copilot Instructions for hlpr AI Agent

## Development Guidelines

### Package Management with UV
```bash
# Add dependencies
uv add package-name

# Development dependencies  
uv add --dev pytest ruff

# Run commands
uv run python -m src.cli check-setup
uv run pytest
uvx run ruff check  # Linting
uvx run ruff format  # Formatting
```
always use uv add for adding dependencies to pyproject.toml