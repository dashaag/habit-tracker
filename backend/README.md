# HERE Inference API

## Project Overview

The HERE Inference API provides endpoints for processing and serving inference results. The project is built using FastAPI and includes database integration with SQLAlchemy and Alembic for migrations.

## Prerequisites

- Python 3.12.10
- [`uv`](https://github.com/astral-sh/uv) (see below for install instructions)

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd here-inference-api
   ```
2. **Install uv (if not already installed)**
   ```bash
   curl -Ls https://astral.sh/uv/install.sh | sh
   ```
   Or see the [official installation instructions](https://github.com/astral-sh/uv#installation).
3. **Install Dependencies & Create Virtual Environment**
   Install both the main application dependencies and the development tools (like Ruff, Pyright, pre-commit):
   ```bash
   uv sync --extra dev
   ```
   > `uv sync` will automatically create and manage `.venv` for you if it does not already exist.
4. **Activate the Virtual Environment**
   ```bash
   source .venv/bin/activate  # On Unix/macOS
   # OR
   .venv\Scripts\activate     # On Windows
   ```
5. **Set Up Pre-commit Hooks**
   Ensure pre-commit is installed (handled by `uv sync` as it's in `pyproject.toml`). Then, install the git hooks:
   ```bash
   pre-commit install
   ```
6. **Environment Configuration**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` as needed.
7. **Database Setup**
   ```bash
   alembic upgrade head
   ```

## Running the Application

You can start the FastAPI server in two ways:

- **From the command line:**
  ```bash
  uvicorn app.main:app --reload --port 5001
  ```
- **From VSCode:**
  Use the included `.vscode/launch.json` configuration for convenient debugging and running. Simply select the "FastAPI: local" configuration in the Run & Debug panel and start debugging.

The API will be available at http://localhost:5001

API documentation is automatically generated and available at:

- Swagger UI: http://localhost:5001/docs
- ReDoc: http://localhost:5001/redoc

## Project Structure

- `app/`: Main application code
  - `api/`: API endpoints and controllers
    - `controllers/`: Route handlers and endpoint definitions
  - `common/`: Common application code
    - `app_settings.py`: Application settings
  - `core/`: Core application components
  - `crud/`: Database CRUD operations
  - `db/`: Database connection and configuration
  - `models/`: Data models and database schemas
  - `schemas/`: Pydantic models for request/response validation
  - `tests/`: Test files
- `persistence/`: Alembic migration configuration
  - `versions/`: Migration script files
- `alembic.ini`: Alembic configuration file

## Development

- **Adding New Migrations**
  ```bash
  alembic revision --autogenerate -m "Description of changes"
  ```
- **Running Tests**
  ```bash
  # Command to run tests (if applicable)
  ```

## Code Quality Tools

This project uses **Ruff** for extremely fast Python linting and code formatting.

Ruff's configuration is defined in the `[tool.ruff]` section of `pyproject.toml`. It replaces the need for separate tools like Black, isort, Flake8, etc.

Pre-commit hooks (`.pre-commit-config.yaml`) are configured to run Ruff automatically before each commit, ensuring consistent code style and quality.

Example configuration snippet from `pyproject.toml`:

```toml
[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
select = ["E", "W", "F", "I", "UP"] # Base rules: pycodestyle, pyflakes, isort, pyupgrade

[tool.ruff.format]
# Formatting options (e.g., quote style) are also configured here.
```

## Package Management with uv

- **Add dependency:** `uv add <package>`
- **Remove dependency:** `uv remove <package>`
- **Upgrade dependency:** `uv add --upgrade <package>`
- **Sync/install:** `uv sync`

> All dependencies are managed in `pyproject.toml`. See the [uv documentation](https://github.com/astral-sh/uv) for more details.

## Troubleshooting

### Pre-commit Issues

If you encounter issues with pre-commit hooks when using external Git tools:

1. Make sure pre-commit is installed in your virtual environment
2. If you see an error about pre-commit not being found, the hook might be looking for Python in the wrong location. The hook script in `.git/hooks/pre-commit` should use a relative path to find your virtual environment's Python interpreter.
