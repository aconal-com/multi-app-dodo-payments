# Contributing to Dodo Payments Microservice

First off, thank you for considering contributing to this project! 🎉

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

**When submitting a bug report, please include:**
- Clear and descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Error messages and stack traces
- Relevant logs

**Template:**
```markdown
**Description:**
A clear description of the bug.

**Steps to Reproduce:**
1. Step one
2. Step two
3. ...

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Environment:**
- OS: [e.g., macOS 13.0]
- Python: [e.g., 3.11.5]
- FastAPI: [e.g., 0.109.0]
- Docker: [e.g., 24.0.5]

**Logs:**
```
Paste relevant logs here
```
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues.

**When submitting an enhancement suggestion, please include:**
- Clear and descriptive title
- Detailed description of the proposed feature
- Why this enhancement would be useful
- Possible implementation approach
- Examples of how it would be used

### Pull Requests

**Good pull requests** include:
- Clear description of changes
- Reference to related issues
- Tests for new functionality
- Updated documentation
- Follows code style guidelines

**Process:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Write/update tests
5. Ensure tests pass
6. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
7. Push to branch (`git push origin feature/AmazingFeature`)
8. Open a Pull Request

## Development Setup

### Prerequisites
- Python 3.11+
- MySQL 8.0+
- Docker & Docker Compose (optional)
- Git

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/aniketkarne/multi-app-dodo-payments.git
cd multi-app-dodo-payments

# Add upstream remote
git remote add upstream https://github.com/aniketkarne/multi-app-dodo-payments.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Setup database
mysql -u root -p < payments-db-structure.sql

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Run tests
pytest

# Run application
python main.py
```

## Code Style

### Python Style Guide
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use [Black](https://github.com/psf/black) for code formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Use type hints for all functions

**Format code:**
```bash
# Format with Black
black .

# Sort imports
isort .

# Lint with flake8
flake8 .
```

### Code Standards

**Function Documentation:**
```python
def create_checkout_session(
    app_name: str,
    user_id: str,
    product_id: str
) -> Dict[str, Any]:
    """
    Create a Dodo checkout session.
    
    Args:
        app_name: Application identifier
        user_id: User identifier
        product_id: Product to purchase
    
    Returns:
        Dictionary with session_id, checkout_url, expires_at
    
    Raises:
        HTTPException: If app or product not found
    """
    pass
```

**Variable Naming:**
- Use descriptive names
- snake_case for functions and variables
- PascalCase for classes
- UPPER_CASE for constants

**Comments:**
- Write self-documenting code
- Add comments for complex logic
- Explain "why", not "what"

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

**Examples:**
```
feat(payments): add refund processing endpoint

fix(webhook): handle missing event_id in payload

docs: update API documentation for credits endpoint

test(credits): add tests for deduction edge cases
```

## Testing

### Writing Tests

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_checkout_invalid_product():
    """Test checkout with invalid product"""
    response = client.post(
        "/payments/checkout",
        headers={"X-API-Key": "test_key"},
        json={
            "app_name": "test-app",
            "user_id": "user_123",
            "product_id": "invalid_product"
        }
    )
    assert response.status_code == 404
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_payments.py

# Run specific test
pytest tests/test_payments.py::test_create_checkout

# Run with verbose output
pytest -v
```

## Documentation

### Update Documentation

When adding features, update:
- `README.md` - Main documentation
- `QUICKSTART.md` - If setup changes
- `PROJECT_STRUCTURE.md` - If files/structure changes
- API docstrings - For code documentation

### Documentation Style

- Use clear, concise language
- Include code examples
- Add diagrams for complex flows
- Keep docs up-to-date with code

## Project Structure

```
payments-service/
├── main.py              # App entry point
├── config.py            # Configuration
├── database.py          # Models
├── routers/             # API endpoints
├── services/            # Business logic
├── middleware/          # Middleware
├── scripts/             # Utility scripts
└── tests/               # Test files
```

## Database Migrations

When modifying database schema:

1. Update `database.py` models
2. Update `payments-db-structure.sql`
3. Create migration script if needed
4. Test migration on fresh database
5. Document changes in CHANGELOG.md

## Release Process

1. Update version in `main.py`
2. Update `CHANGELOG.md`
3. Create pull request
4. After merge, create release tag
5. GitHub Actions will build & publish

## Getting Help

- **Questions?** Open a [Discussion](https://github.com/aniket/multi-app-dodo-payments/discussions)
- **Bug?** Open an [Issue](https://github.com/aniketkarne/multi-app-dodo-payments/issues)
- **Chat?** Join our [Discord](#) (if available)

## Recognition

Contributors will be recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- GitHub insights

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing! 🚀**

