# Orange DevOps Task - Project Structure

This repository contains the Orange DevOps Task projects, organized as separate modules using UV for package management.

## Project Structure

```
orange-devops-task/
├── car-fleet-api/          # Flask API for car fleet management
│   ├── car_fleet/          # Python package with business logic
│   ├── app.py              # Flask application
│   ├── pyproject.toml      # UV project configuration
│   ├── uv.lock             # Dependency lock file
│   ├── Dockerfile          # Container image definition
│   └── .venv/              # Virtual environment (ignored in git)
│
├── k8s-tests-project/      # Kubernetes E2E tests
│   ├── test_k8s_e2e.py     # Test suite
│   ├── nginx-healthcheck.yaml  # Test pod manifest
│   ├── pyproject.toml      # UV project configuration
│   ├── uv.lock             # Dependency lock file
│   └── .venv/              # Virtual environment (ignored in git)
│
├── k8s-manifests/          # Kubernetes deployment manifests
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ingress.yaml
│
└── Documentation files     # API docs, architecture, guides, etc.
```

## Package Manager: UV

This project uses [UV](https://github.com/astral-sh/uv) - a fast Python package manager and project management tool.

### Why UV?

- **Fast**: 10-100x faster than pip
- **Reliable**: Deterministic dependency resolution with lock files
- **Modern**: Built-in support for pyproject.toml and PEP standards
- **Docker-friendly**: Official Docker images with optimized caching

### Prerequisites

Install UV:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Working with Each Project

### Car Fleet API

```bash
cd car-fleet-api

# Install dependencies
uv sync

# Run the application
uv run python app.py

# Add a new dependency
uv add <package-name>

# Build Docker image
docker build -t car-fleet-api:latest .
```

### K8s Tests

```bash
cd k8s-tests-project

# Install dependencies
uv sync --no-install-project

# Run tests
uv run pytest test_k8s_e2e.py -v

# Run specific test
uv run pytest test_k8s_e2e.py::TestClusterStatus -v
```

## Common UV Commands

| Command | Description |
|---------|-------------|
| `uv sync` | Install/update all dependencies from lock file |
| `uv sync --all-groups` | Install all dependency groups (including optional) |
| `uv add <package>` | Add a new dependency |
| `uv remove <package>` | Remove a dependency |
| `uv run <command>` | Run a command in the project environment |
| `uv lock` | Update the lock file without installing |
| `uv pip list` | List installed packages |
| `uv python install <version>` | Install a specific Python version |

## Benefits of This Structure

1. **Separation of Concerns**: Each component is independently managed
2. **Clean Dependencies**: No mixing of API and test dependencies
3. **Easy Development**: Work on each component without affecting others
4. **Better CI/CD**: Can build and test components separately
5. **Scalable**: Easy to add new projects/modules
6. **Modern Tooling**: UV provides fast, reliable package management

## Migration Notes

- Replaced `requirements.txt` with `pyproject.toml` for modern Python packaging
- Each project has its own virtual environment (`.venv/`)
- Lock files (`uv.lock`) ensure reproducible builds
- Old `venv/` directories have been removed
