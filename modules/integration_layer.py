"""
Integration Layer for PV Chamber Configurator
Unified API for all modules with data flow orchestration and state management
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class IntegrationLayer:
    """
    Unified integration layer for all PV Chamber Configurator modules.
    Manages data flow, dependencies, and state across all phases.
    """

    def __init__(self, session_state=None):
        """
        Initialize the integration layer.

        Args:
            session_state: Streamlit session state object for persistence
        """
        self.session_state = session_state
        self.logger = self._setup_logger()

        # Module registry
        self.modules = {
            'phase1_core': {'name': 'Core Calculations', 'data': {}, 'initialized': False},
            'phase2_uv': {'name': 'UV Optical System', 'data': {}, 'initialized': False},
            'phase3_cfd': {'name': 'CFD Simulation', 'data': {}, 'initialized': False},
            'phase4_supplier': {'name': 'Supplier Database', 'data': {}, 'initialized': False},
            'phase5_hmi': {'name': 'Virtual HMI + Robot', 'data': {}, 'initialized': False},
            'phase6_quote': {'name': 'Quote Generator', 'data': {}, 'initialized': False},
            'phase7_business': {'name': 'Business Analysis', 'data': {}, 'initialized': False},
            'phase8_reports': {'name': 'Report Generator', 'data': {}, 'initialized': False},
            'phase10_compliance': {'name': 'Compliance Checker', 'data': {}, 'initialized': False}
        }

        # Dependency graph (which modules depend on which)
        self.dependencies = {
            'phase2_uv': ['phase1_core'],
            'phase3_cfd': ['phase1_core'],
            'phase6_quote': ['phase1_core', 'phase2_uv', 'phase3_cfd', 'phase4_supplier', 'phase5_hmi'],
            'phase7_business': ['phase6_quote'],
            'phase8_reports': ['phase1_core', 'phase2_uv', 'phase3_cfd', 'phase6_quote', 'phase7_business'],
            'phase10_compliance': ['phase1_core', 'phase2_uv']
        }

        self.logger.info("Integration Layer initialized")

    def _setup_logger(self) -> logging.Logger:
        """Setup logging for the integration layer."""
        logger = logging.getLogger('IntegrationLayer')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    # Module Orchestration
    def initialize_all_modules(self) -> bool:
        """
        Initialize all modules in dependency order.

        Returns:
            bool: True if successful
        """
        try:
            for module_id in self.modules:
                self.modules[module_id]['initialized'] = True

            self.logger.info("All modules initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Module initialization failed: {str(e)}")
            return False

    def get_module_data(self, module_name: str) -> Dict[str, Any]:
        """
        Get data from a specific module.

        Args:
            module_name: Module identifier (e.g., 'phase1_core')

        Returns:
            Dict containing module data
        """
        if module_name not in self.modules:
            self.logger.warning(f"Module {module_name} not found")
            return {}

        return self.modules[module_name]['data'].copy()

    def set_module_data(self, module_name: str, data: Dict[str, Any]) -> bool:
        """
        Set data for a specific module.

        Args:
            module_name: Module identifier
            data: Data dictionary to set

        Returns:
            bool: True if successful
        """
        if module_name not in self.modules:
            self.logger.error(f"Module {module_name} not found")
            return False

        try:
            self.modules[module_name]['data'].update(data)
            self.modules[module_name]['last_updated'] = datetime.now().isoformat()

            # Propagate changes to dependent modules
            self.propagate_changes(module_name, self._get_dependent_modules(module_name))

            self.logger.info(f"Data updated for module {module_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update module {module_name}: {str(e)}")
            return False

    def _get_dependent_modules(self, source_module: str) -> List[str]:
        """Get list of modules that depend on the source module."""
        dependent = []
        for module, deps in self.dependencies.items():
            if source_module in deps:
                dependent.append(module)
        return dependent

    def propagate_changes(self, source_module: str, affected_modules: List[str]) -> None:
        """
        Propagate changes from source module to affected modules.

        Args:
            source_module: Module that changed
            affected_modules: List of modules affected by the change
        """
        if not affected_modules:
            return

        source_data = self.get_module_data(source_module)

        for module in affected_modules:
            if module in self.modules:
                # Mark module as needing recalculation
                self.modules[module]['needs_update'] = True
                self.modules[module]['update_source'] = source_module
                self.logger.info(f"Propagated changes from {source_module} to {module}")

    # Data Flow
    def collect_all_data(self) -> Dict[str, Any]:
        """
        Collect data from all modules into a single dictionary.

        Returns:
            Dict containing all module data
        """
        all_data = {
            'timestamp': datetime.now().isoformat(),
            'modules': {}
        }

        for module_id, module_info in self.modules.items():
            all_data['modules'][module_id] = {
                'name': module_info['name'],
                'data': module_info['data'],
                'initialized': module_info['initialized']
            }

        return all_data

    def validate_data_consistency(self) -> Dict[str, List[str]]:
        """
        Validate data consistency across modules.

        Returns:
            Dict containing validation results and any errors
        """
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }

        # Check dependencies
        for module, deps in self.dependencies.items():
            for dep in deps:
                if dep not in self.modules:
                    validation_results['valid'] = False
                    validation_results['errors'].append(
                        f"Module {module} depends on {dep} which doesn't exist"
                    )
                elif not self.modules[dep]['initialized']:
                    validation_results['warnings'].append(
                        f"Module {module} depends on uninitialized module {dep}"
                    )

        # Check for circular dependencies
        if self._has_circular_dependencies():
            validation_results['valid'] = False
            validation_results['errors'].append("Circular dependencies detected")

        self.logger.info(f"Validation complete: {validation_results}")
        return validation_results

    def _has_circular_dependencies(self) -> bool:
        """Check for circular dependencies in the module graph."""
        visited = set()
        rec_stack = set()

        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)

            if node in self.dependencies:
                for neighbor in self.dependencies[node]:
                    if neighbor not in visited:
                        if has_cycle(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        return True

            rec_stack.remove(node)
            return False

        for module in self.modules:
            if module not in visited:
                if has_cycle(module):
                    return True

        return False

    def resolve_dependencies(self) -> List[str]:
        """
        Resolve module dependencies and return execution order.

        Returns:
            List of module names in dependency order
        """
        # Topological sort using Kahn's algorithm
        in_degree = {module: 0 for module in self.modules}

        for deps in self.dependencies.values():
            for dep in deps:
                if dep in in_degree:
                    in_degree[dep] += 1

        queue = [module for module, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            module = queue.pop(0)
            result.append(module)

            if module in self.dependencies:
                for dep in self.dependencies[module]:
                    if dep in in_degree:
                        in_degree[dep] -= 1
                        if in_degree[dep] == 0:
                            queue.append(dep)

        return result

    # State Management
    def save_session_state(self, filepath: Optional[str] = None) -> bool:
        """
        Save current session state to file.

        Args:
            filepath: Optional custom filepath

        Returns:
            bool: True if successful
        """
        if filepath is None:
            filepath = 'config/session_state.json'

        try:
            state_data = {
                'saved_at': datetime.now().isoformat(),
                'modules': self.modules,
                'version': '1.0'
            }

            Path(filepath).parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, 'w') as f:
                json.dump(state_data, f, indent=2)

            self.logger.info(f"Session state saved to {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save session state: {str(e)}")
            return False

    def load_session_state(self, filepath: Optional[str] = None) -> bool:
        """
        Load session state from file.

        Args:
            filepath: Optional custom filepath

        Returns:
            bool: True if successful
        """
        if filepath is None:
            filepath = 'config/session_state.json'

        try:
            with open(filepath, 'r') as f:
                state_data = json.load(f)

            self.modules = state_data['modules']

            self.logger.info(f"Session state loaded from {filepath}")
            return True
        except FileNotFoundError:
            self.logger.warning(f"Session state file not found: {filepath}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to load session state: {str(e)}")
            return False

    def reset_to_defaults(self) -> None:
        """Reset all modules to default state."""
        for module_id in self.modules:
            self.modules[module_id]['data'] = {}
            self.modules[module_id]['initialized'] = False
            self.modules[module_id].pop('needs_update', None)
            self.modules[module_id].pop('update_source', None)

        self.logger.info("All modules reset to defaults")

    # Utility Methods
    def get_module_status(self) -> Dict[str, Any]:
        """
        Get status of all modules.

        Returns:
            Dict containing module status information
        """
        status = {
            'total_modules': len(self.modules),
            'initialized_modules': sum(1 for m in self.modules.values() if m['initialized']),
            'modules_needing_update': sum(1 for m in self.modules.values() if m.get('needs_update', False)),
            'module_details': {}
        }

        for module_id, module_info in self.modules.items():
            status['module_details'][module_id] = {
                'name': module_info['name'],
                'initialized': module_info['initialized'],
                'needs_update': module_info.get('needs_update', False),
                'has_data': bool(module_info['data'])
            }

        return status

    def export_module_data(self, module_name: str, filepath: str) -> bool:
        """
        Export module data to JSON file.

        Args:
            module_name: Module to export
            filepath: Output file path

        Returns:
            bool: True if successful
        """
        try:
            data = self.get_module_data(module_name)

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            self.logger.info(f"Module {module_name} data exported to {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export module data: {str(e)}")
            return False
