# Developer Guide

This document provides guidance for developers working on the platform-linux_arm codebase.

## Table of Contents

1. [Development Setup](#development-setup)
2. [Running Tests](#running-tests)
3. [Code Quality](#code-quality)
4. [Contributing Guidelines](#contributing-guidelines)
5. [Release Process](#release-process)

---

## Development Setup

### Prerequisites

- Python 3.7 or later
- Git
- PlatformIO Core 6.0+

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/sfo2001/platform-linux_arm.git
   cd platform-linux_arm
   ```

2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. Install the platform in development mode (symlink):
   ```bash
   pio pkg install --global --platform symlink://.
   ```

---

## Running Tests

### Unit Tests

The project uses pytest for unit testing. Tests are located in the `tests/` directory.

#### Quick Start

Run all tests:
```bash
pytest
```

Run with verbose output:
```bash
pytest -v
```

Run specific test file:
```bash
pytest tests/test_platform.py -v
```

Run specific test class:
```bash
pytest tests/test_platform.py::TestIsNative -v
```

Run specific test method:
```bash
pytest tests/test_platform.py::TestIsNative::test_is_native_on_linux_arm -v
```

#### Coverage Reports

Generate coverage report:
```bash
pytest --cov=. --cov-report=term-missing
```

Generate HTML coverage report:
```bash
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in your browser
```

Generate XML coverage report (for CI):
```bash
pytest --cov=. --cov-report=xml
```

#### Test Markers

Tests are marked for categorization:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Integration Tests

For integration testing with actual hardware, see [`docs/TESTING.md`](docs/TESTING.md).

---

## Code Quality

### Code Formatting

This project uses Black for code formatting:

```bash
# Check formatting
black --check .

# Auto-format code
black .
```

### Import Sorting

This project uses isort for import organization:

```bash
# Check import order
isort --check-only --diff .

# Auto-sort imports
isort .
```

### Linting

This project uses pylint for static code analysis:

```bash
# Run pylint on all Python files
pylint *.py

# Run pylint on specific module
pylint platform.py
```

### Type Checking

This project uses mypy for type checking:

```bash
# Run type checking
mypy platform.py ssh_utils.py platform_config.py
```

### Pre-commit Checks

Run all quality checks before committing:

```bash
# Format code
black .
isort .

# Run tests
pytest

# Run linting (optional)
pylint *.py
```

---

## Testing Best Practices

### Writing Tests

1. **Test File Naming**: Test files should match the pattern `test_*.py`
2. **Test Function Naming**: Test functions should match the pattern `test_*`
3. **Test Class Naming**: Test classes should match the pattern `Test*`

4. **Test Structure**: Follow the Arrange-Act-Assert pattern
   ```python
   def test_example():
       # Arrange - Set up test data and mocks
       mock_env = Mock()

       # Act - Execute the code under test
       result = function_under_test(mock_env)

       # Assert - Verify the result
       assert result == expected_value
   ```

5. **Use Fixtures**: Leverage pytest fixtures from `tests/conftest.py` for common setup:
   ```python
   def test_with_fixture(mock_env, temp_project_dir):
       # Use fixtures directly as function parameters
       assert temp_project_dir.exists()
   ```

6. **Mock External Dependencies**: Use `unittest.mock` to isolate units:
   ```python
   @patch('platform.get_systype')
   def test_with_mock(mock_get_systype):
       mock_get_systype.return_value = 'linux_arm'
       assert Linux_armPlatform._is_native() is True
   ```

7. **Test Edge Cases**: Include tests for error conditions and boundary cases
   ```python
   def test_invalid_input_raises_error():
       with pytest.raises(ValueError, match="expected error message"):
           function_that_should_raise(invalid_input)
   ```

### Coverage Goals

- **Core Modules**: Aim for 80%+ coverage
  - `platform.py`: 80%+
  - `ssh_utils.py`: 90%+
  - `platform_config.py`: 80%+

- **Builder Scripts**: Aim for 50%+ coverage
  - `builder/main.py`: 50%+
  - `builder/frameworks/*.py`: 50%+

### Continuous Integration

Tests run automatically on GitHub Actions for:
- Every push to `develop` and `main` branches
- Every pull request

See `.github/workflows/tests.yml` for CI configuration.

---

## Contributing Guidelines

### Git Workflow

This project uses git-flow:

- `develop`: Main development branch
- `main`/`master`: Production-ready releases
- `feature/*`: Feature branches
- `release/*`: Release preparation branches
- `hotfix/*`: Emergency fixes for production

### Commit Messages

Follow conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```bash
feat(platform): add support for Raspberry Pi 5
fix(upload): handle timeout errors gracefully
docs(testing): add unit testing documentation
test(platform): improve coverage for _is_native method
```

### Pull Request Process

1. Create a feature branch from `develop`:
   ```bash
   git checkout develop
   git pull
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and add tests:
   ```bash
   # Make changes
   # Add tests
   pytest  # Verify tests pass
   ```

3. Format and lint your code:
   ```bash
   black .
   isort .
   ```

4. Commit your changes:
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

5. Push and create pull request:
   ```bash
   git push origin feature/your-feature-name
   # Create PR on GitHub targeting 'develop' branch
   ```

6. Ensure CI passes and address review feedback

---

## Release Process

### Version Numbering

This project uses semantic versioning (SemVer):
- **Major** (1.x.x): Breaking changes
- **Minor** (x.1.x): New features (backward compatible)
- **Patch** (x.x.1): Bug fixes (backward compatible)

### Release Checklist

1. **Update Version**:
   ```json
   // platform.json
   {
     "version": "1.7.0"
   }
   ```

2. **Update Changelog**: Document all changes since last release

3. **Run Full Test Suite**:
   ```bash
   pytest
   ```

4. **Create Release Branch**:
   ```bash
   git checkout develop
   git checkout -b release/v1.7.0
   ```

5. **Final Testing**: Verify all examples build successfully

6. **Merge to Main**:
   ```bash
   git checkout main
   git merge --no-ff release/v1.7.0
   git tag -a v1.7.0 -m "Release v1.7.0"
   git push origin main --tags
   ```

7. **Merge Back to Develop**:
   ```bash
   git checkout develop
   git merge --no-ff release/v1.7.0
   git push origin develop
   ```

8. **Publish Release**: Create GitHub release from tag

---

## Project Structure

```
platform-linux_arm/
├── .github/
│   └── workflows/         # CI/CD workflows
│       ├── examples.yml   # Integration tests
│       ├── tests.yml      # Unit tests
│       └── release.yml    # Release automation
├── boards/                # Board definitions (JSON)
├── builder/               # SCons build scripts
│   ├── frameworks/        # Framework integration
│   └── main.py           # Main build script
├── docs/                  # Documentation
├── examples/              # Example projects
├── tests/                 # Unit tests
│   ├── conftest.py       # Shared fixtures
│   ├── test_platform.py  # Platform tests
│   ├── test_ssh_utils.py # SSH utilities tests
│   └── test_platform_config.py  # Config tests
├── platform.py            # Main platform class
├── platform_config.py     # Configuration support
├── platform_constants.py  # Constants definitions
├── ssh_utils.py           # SSH utilities
├── platform.json          # Platform manifest
├── pytest.ini             # Pytest configuration
├── .coveragerc            # Coverage configuration
└── requirements-dev.txt   # Development dependencies
```

---

## Useful Commands

### Development

```bash
# Install platform in development mode
pio pkg install --global --platform symlink://.

# Build example project
cd examples/lgpio-blink
pio run

# Clean build artifacts
pio run --target clean

# Upload to target device
pio run --target upload
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/test_platform.py

# Run tests in watch mode (requires pytest-watch)
ptw
```

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
pylint platform.py

# Type check
mypy platform.py
```

---

## Resources

- **PlatformIO Documentation**: https://docs.platformio.org/
- **PlatformIO Platform Development**: https://docs.platformio.org/en/latest/platforms/creating_platform.html
- **pytest Documentation**: https://docs.pytest.org/
- **Black Formatter**: https://black.readthedocs.io/
- **Conventional Commits**: https://www.conventionalcommits.org/

---

## Getting Help

- **Issues**: https://github.com/sfo2001/platform-linux_arm/issues
- **Discussions**: https://github.com/sfo2001/platform-linux_arm/discussions
- **Wiki**: https://github.com/sfo2001/platform-linux_arm/wiki

---

**Document Version**: 1.0
**Last Updated**: 2025-11-15
