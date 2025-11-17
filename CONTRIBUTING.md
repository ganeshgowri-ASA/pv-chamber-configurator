# Contributing to PV Chamber Configurator

Thank you for your interest in contributing to the PV Chamber Configurator project!

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- Virtual environment (recommended)

### Local Development

```bash
# Clone repository
git clone <repository-url>
cd pv-chamber-configurator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8

# Run application
streamlit run app.py
```

## Code Style Guidelines

### Python Code Style

We follow PEP 8 with the following specifics:

- **Line length**: 100 characters maximum
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Grouped (stdlib, third-party, local) and sorted alphabetically
- **Naming conventions**:
  - Classes: `PascalCase`
  - Functions/variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`

### Code Formatting

Use `black` for automatic formatting:

```bash
# Format all Python files
black modules/ tests/ app.py

# Check formatting (CI/CD)
black --check modules/ tests/ app.py
```

### Linting

Use `flake8` for linting:

```bash
# Run linter
flake8 modules/ tests/ app.py

# With specific rules
flake8 --max-line-length=100 --ignore=E203,W503 modules/
```

## Testing

### Writing Tests

All new features must include tests:

```python
# tests/test_my_module.py
import unittest
from modules.my_module import MyClass

class TestMyClass(unittest.TestCase):
    def setUp(self):
        self.instance = MyClass()

    def test_my_feature(self):
        result = self.instance.my_method()
        self.assertEqual(result, expected_value)

    def test_edge_case(self):
        with self.assertRaises(ValueError):
            self.instance.my_method(invalid_input)
```

### Running Tests

```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_core_calculations.py

# With coverage report
pytest --cov=modules --cov-report=html tests/

# Coverage minimum threshold
pytest --cov=modules --cov-fail-under=80 tests/
```

### Test Coverage Requirements

- **Minimum coverage**: 80% for new modules
- **Critical modules**: 90%+ coverage (calculations, compliance, reports)
- **UI modules**: 60%+ coverage (Streamlit components harder to test)

## Git Workflow

### Branch Naming

- **Feature branches**: `claude/feature-name-sessionid`
- **Bug fixes**: `claude/bugfix-description-sessionid`
- **Documentation**: `claude/docs-update-sessionid`

### Commit Messages

Follow conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `chore`: Maintenance

**Examples:**

```
feat(cfd): Add transient temperature response simulation

- Implement ramp rate calculation
- Add IEC compliance checking
- Include visualization of temperature profile

Closes #123
```

```
fix(quote-gen): Correct currency formatting for lakhs/crores

- Fix decimal places for Indian currency
- Add proper comma separators
- Update tests

Fixes #456
```

### Pull Request Process

1. **Create feature branch** from main
2. **Implement changes** with tests
3. **Run full test suite**: `pytest tests/`
4. **Format code**: `black modules/ tests/`
5. **Lint code**: `flake8 modules/ tests/`
6. **Update documentation** if needed
7. **Create pull request** with description
8. **Address review comments**
9. **Merge after approval**

## Adding New Features

### Module Structure

```python
# modules/my_new_module.py

"""
Module description and purpose.

This module provides functionality for...
"""

import standard_library
import third_party
from modules import local_module


class MyNewClass:
    """
    Class description.

    Attributes:
        attr1 (type): Description
        attr2 (type): Description

    Example:
        >>> instance = MyNewClass(param1, param2)
        >>> result = instance.method()
    """

    def __init__(self, param1: type, param2: type):
        """
        Initialize MyNewClass.

        Args:
            param1: Description
            param2: Description

        Raises:
            ValueError: If param1 is invalid
        """
        self.attr1 = param1
        self.attr2 = param2

    def public_method(self, arg: type) -> type:
        """
        Method description.

        Args:
            arg: Argument description

        Returns:
            Return value description

        Raises:
            TypeError: If arg is wrong type
        """
        return self._private_method(arg)

    def _private_method(self, arg: type) -> type:
        """Private helper method."""
        # Implementation
        pass
```

### Documentation Requirements

All new features must include:

1. **Docstrings**: Google-style docstrings for all classes and functions
2. **Type hints**: Use Python type hints where possible
3. **Examples**: Include usage examples in docstrings
4. **README updates**: Update README.md if user-facing
5. **CHANGELOG entry**: Add entry to CHANGELOG.md

### Adding a New Phase

If adding a new phase (Phase 11+):

1. Create module file: `modules/phase11_module.py`
2. Add imports to `app.py`
3. Create visualization module if needed
4. Add to `modules/__init__.py`
5. Create test file: `tests/test_phase11_module.py`
6. Update documentation
7. Create phase-specific README

## Code Review Checklist

Before submitting PR, verify:

- [ ] All tests pass
- [ ] Code is formatted (black)
- [ ] Code is linted (flake8)
- [ ] Coverage meets threshold (80%+)
- [ ] Docstrings are complete
- [ ] Type hints are added
- [ ] No hardcoded credentials/secrets
- [ ] Error handling is implemented
- [ ] Edge cases are tested
- [ ] Documentation is updated
- [ ] CHANGELOG is updated

## Common Patterns

### Error Handling

```python
try:
    result = risky_operation()
except SpecificError as e:
    st.error(f"Operation failed: {str(e)}")
    logger.error(f"Error details: {e}", exc_info=True)
    return None
```

### Streamlit Caching

```python
@st.cache_data
def load_data():
    """Load data with caching."""
    return expensive_operation()

@st.cache_resource
def initialize_model():
    """Initialize model with caching."""
    return Model()
```

### Configuration

```python
# Use configuration files, not hardcoded values
config = load_config('config/settings.json')
value = config.get('key', default_value)
```

## Performance Guidelines

- **Avoid loops in Streamlit main thread**: Use caching
- **Large datasets**: Use generators or chunking
- **Database queries**: Use indexes and LIMIT clauses
- **CFD simulations**: Provide progress indicators
- **Report generation**: Show spinner during long operations

## Security Guidelines

- **Never commit secrets**: Use environment variables or Streamlit secrets
- **Validate user input**: Sanitize all inputs
- **SQL injection**: Use parameterized queries
- **File uploads**: Validate file types and sizes
- **SMTP passwords**: Use app-specific passwords, not account passwords

## Documentation Standards

### Code Comments

```python
# Good comment: Explains WHY, not WHAT
# Calculate thermal efficiency using ISO 17025 methodology
thermal_eff = heat_output / heat_input

# Bad comment: States the obvious
# Add 1 to counter
counter += 1
```

### README Updates

When adding features, update:
- Feature list
- Installation instructions if needed
- Configuration examples
- Usage examples

## Questions or Issues?

- **Technical questions**: Contact maintainers via email
- **Bug reports**: Open issue with reproduction steps
- **Feature requests**: Discuss with team before implementing

---

**Thank you for contributing to PV Chamber Configurator!**

*Maintainers: Zenitek Solutions | info@zenitek.com*
