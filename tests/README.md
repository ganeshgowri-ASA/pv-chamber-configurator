# Test Suite for PV Chamber Configurator - Phase 9

## Overview

This directory contains comprehensive test suites for Phase 9 modules:

- Integration Layer
- White-Label Manager
- I18n Manager
- Config Manager

## Running Tests

### Run All Tests

```bash
python -m pytest tests/
```

### Run Specific Test File

```bash
python tests/test_integration_layer.py
python tests/test_white_label_manager.py
python tests/test_i18n_manager.py
python tests/test_config_manager.py
```

### Run with Coverage

```bash
python -m pytest tests/ --cov=modules --cov-report=html
```

## Test Files

### test_integration_layer.py

Tests for the Integration Layer module:
- Module initialization
- Data flow management
- Dependency resolution
- State persistence
- Change propagation

### test_white_label_manager.py

Tests for White-Label configuration:
- Logo upload and validation
- Company information management
- Brand color configuration
- Font family selection
- Configuration save/load

### test_i18n_manager.py

Tests for Internationalization:
- Translation loading
- Locale switching
- Missing key detection
- Translation coverage
- RTL language support

### test_config_manager.py

Tests for Configuration Management:
- Configuration save/load
- Template management
- Configuration validation
- Partial configuration export
- Configuration merging

## Test Coverage

Current coverage targets:
- Integration Layer: >90%
- White-Label Manager: >85%
- I18n Manager: >85%
- Config Manager: >90%

## Writing New Tests

### Test Structure

```python
import unittest
from modules import ModuleName

class TestModuleName(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.module = ModuleName()

    def tearDown(self):
        """Clean up after tests"""
        pass

    def test_feature(self):
        """Test specific feature"""
        result = self.module.method()
        self.assertEqual(result, expected)
```

### Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Remove temporary files in tearDown
3. **Descriptive**: Use clear test names
4. **Coverage**: Test both success and failure cases
5. **Fixtures**: Use setUp for common initialization

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Commits to main branch
- Scheduled daily runs

## Troubleshooting

### Import Errors

If you get import errors, ensure the parent directory is in the path:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### File Permissions

Some tests create temporary files. Ensure write permissions:

```bash
chmod -R 755 tests/
```

### Missing Dependencies

Install test dependencies:

```bash
pip install -r requirements.txt
pip install pytest pytest-cov
```

## Test Data

Test data files are created automatically in:
- `tests/test_locales/` - Translation test files
- `tests/test_templates/` - Configuration templates
- `tests/temp_*.json` - Temporary test files (cleaned up automatically)
