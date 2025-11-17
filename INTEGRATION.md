# Integration Layer Documentation

## Overview

The Integration Layer provides a unified API for managing data flow and orchestration across all modules in the PV Chamber Configurator system. It handles module dependencies, state management, and data consistency.

## Architecture

### Module Registry

The Integration Layer maintains a registry of all system modules:

- **Phase 1**: Core Calculations (chamber specs, thermal calculations)
- **Phase 2**: UV Optical System
- **Phase 3**: CFD Simulation
- **Phase 4**: Supplier Database
- **Phase 5**: Virtual HMI + Robot
- **Phase 6**: Quote Generator
- **Phase 7**: Business Analysis
- **Phase 8**: Report Generator
- **Phase 10**: Compliance Checker

### Dependency Graph

Modules have dependencies on each other:

```
phase1_core (foundation)
├── phase2_uv (depends on chamber specs)
├── phase3_cfd (depends on chamber specs)
└── phase6_quote
    ├── phase1_core
    ├── phase2_uv
    ├── phase3_cfd
    ├── phase4_supplier
    └── phase5_hmi
```

## API Reference

### Initialization

```python
from modules import IntegrationLayer

# Initialize with optional session state
integration = IntegrationLayer(session_state=st.session_state)
```

### Module Orchestration

#### Initialize All Modules

```python
integration.initialize_all_modules()
```

Initializes all modules in dependency order.

#### Get Module Data

```python
data = integration.get_module_data('phase1_core')
```

Retrieve data from a specific module.

#### Set Module Data

```python
integration.set_module_data('phase1_core', {
    'length': 3200,
    'width': 2100,
    'height': 2200
})
```

Set data for a module. Automatically propagates changes to dependent modules.

### Data Flow

#### Collect All Data

```python
all_data = integration.collect_all_data()
```

Collects data from all modules into a single dictionary.

#### Validate Data Consistency

```python
validation = integration.validate_data_consistency()

if validation['valid']:
    print("All data is consistent")
else:
    print("Errors:", validation['errors'])
```

#### Resolve Dependencies

```python
execution_order = integration.resolve_dependencies()
# Returns: ['phase1_core', 'phase2_uv', 'phase3_cfd', ...]
```

Returns modules in topological order based on dependencies.

### State Management

#### Save Session State

```python
integration.save_session_state('config/session.json')
```

Save current state to file for persistence.

#### Load Session State

```python
integration.load_session_state('config/session.json')
```

Restore state from saved file.

#### Reset to Defaults

```python
integration.reset_to_defaults()
```

Reset all modules to default state.

### Utility Methods

#### Get Module Status

```python
status = integration.get_module_status()
print(f"Total modules: {status['total_modules']}")
print(f"Initialized: {status['initialized_modules']}")
```

#### Export Module Data

```python
integration.export_module_data('phase1_core', 'exports/chamber_specs.json')
```

## Data Flow Diagram

```
User Input → Integration Layer → Module Registry
                    ↓
            Dependency Resolution
                    ↓
         Module Update Propagation
                    ↓
            Data Validation
                    ↓
           State Persistence
```

## Best Practices

### 1. Always Use the Integration Layer

Don't access module data directly. Always use the Integration Layer API:

```python
# Good
integration.set_module_data('phase1_core', data)

# Bad
modules['phase1_core']['data'] = data  # Bypasses change propagation
```

### 2. Handle Dependencies

When updating a module that others depend on, the Integration Layer automatically marks dependent modules for recalculation:

```python
# Update chamber specs
integration.set_module_data('phase1_core', {'length': 3500})

# UV system is automatically marked as needing update
status = integration.get_module_data('phase2_uv')
# status['needs_update'] == True
```

### 3. Validate Before Critical Operations

```python
validation = integration.validate_data_consistency()

if validation['valid']:
    generate_quote()
else:
    display_errors(validation['errors'])
```

### 4. Regular State Saves

```python
# Save state after significant operations
integration.set_module_data('phase1_core', chamber_data)
integration.save_session_state()
```

## Error Handling

The Integration Layer uses logging for error tracking:

```python
import logging

# Enable debug logging
logging.getLogger('IntegrationLayer').setLevel(logging.DEBUG)
```

Common errors:

- **ModuleNotFound**: Attempting to access a non-existent module
- **CircularDependency**: Dependency graph has circular references
- **ValidationError**: Data consistency check failed

## Integration with Streamlit

```python
import streamlit as st
from modules import IntegrationLayer

# Initialize in session state
if 'integration_layer' not in st.session_state:
    st.session_state.integration_layer = IntegrationLayer(st.session_state)

# Use throughout the app
integration = st.session_state.integration_layer

# Update module data from UI
chamber_length = st.number_input("Length", value=3200)
integration.set_module_data('phase1_core', {'length': chamber_length})

# Retrieve data for display
uv_data = integration.get_module_data('phase2_uv')
st.write(f"UV Intensity: {uv_data.get('uv_intensity', 0)} W/m²")
```

## Performance Considerations

1. **Lazy Loading**: Modules are only initialized when accessed
2. **Incremental Updates**: Only changed data triggers propagation
3. **Caching**: Module data is cached in session state

## Extending the Integration Layer

### Adding New Modules

```python
# In integration_layer.py, add to modules registry:
self.modules['phase11_new'] = {
    'name': 'New Module',
    'data': {},
    'initialized': False
}

# Add dependencies if needed:
self.dependencies['phase11_new'] = ['phase1_core']
```

### Custom Validation Rules

```python
# Override validate_data_consistency() for custom rules
def validate_data_consistency(self):
    validation = super().validate_data_consistency()

    # Add custom validation
    chamber_data = self.get_module_data('phase1_core')
    if chamber_data.get('length', 0) < 1000:
        validation['valid'] = False
        validation['errors'].append("Chamber too small")

    return validation
```

## Troubleshooting

### Module Not Updating

Check if the module is marked as needing an update:

```python
status = integration.get_module_status()
for module_id, details in status['module_details'].items():
    if details['needs_update']:
        print(f"{module_id} needs recalculation")
```

### Circular Dependencies

Use the validation method:

```python
validation = integration.validate_data_consistency()
if "Circular dependencies" in validation['errors']:
    # Review dependency graph
    print(integration.dependencies)
```

### State Not Persisting

Ensure save is called after updates:

```python
integration.set_module_data('phase1_core', data)
integration.save_session_state()  # Don't forget this!
```

## Version History

- **v1.0**: Initial release with all core functionality
