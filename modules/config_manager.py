"""
Configuration Manager for PV Chamber Configurator
Handles saving, loading, and validating configurations
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib


class ConfigManager:
    """
    Manages configuration save/load functionality for the PV Chamber Configurator.
    Handles full system configurations and templates.
    """

    # Configuration version for compatibility checking
    CONFIG_VERSION = "1.0"

    # Required configuration sections
    REQUIRED_SECTIONS = [
        'chamber_specs',
        'uv_system',
        'user_preferences'
    ]

    # Optional configuration sections
    OPTIONAL_SECTIONS = [
        'cfd_settings',
        'suppliers',
        'test_recipes',
        'white_label',
        'hmi_settings',
        'quote_parameters',
        'business_metrics'
    ]

    def __init__(self, templates_dir: str = 'config/config_templates'):
        """
        Initialize the configuration manager.

        Args:
            templates_dir: Directory for configuration templates
        """
        self.templates_dir = Path(templates_dir)
        self.logger = self._setup_logger()

        # Create templates directory
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("Config Manager initialized")

    def _setup_logger(self) -> logging.Logger:
        """Setup logging for the config manager."""
        logger = logging.getLogger('ConfigManager')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def save_configuration(self, config_data: Dict[str, Any], output_path: str,
                          include_metadata: bool = True) -> bool:
        """
        Save configuration to file.

        Args:
            config_data: Configuration data to save
            output_path: Output file path
            include_metadata: Whether to include metadata

        Returns:
            bool: True if successful
        """
        try:
            # Create configuration structure
            full_config = {
                'config_version': self.CONFIG_VERSION,
                'saved_date': datetime.now().isoformat()
            }

            if include_metadata:
                full_config['metadata'] = {
                    'created_by': 'PV Chamber Configurator',
                    'file_hash': None  # Will be computed after
                }

            # Add configuration data
            full_config.update(config_data)

            # Compute hash of configuration
            if include_metadata:
                config_str = json.dumps(config_data, sort_keys=True)
                file_hash = hashlib.sha256(config_str.encode()).hexdigest()
                full_config['metadata']['file_hash'] = file_hash

            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            # Save to file
            with open(output_path, 'w') as f:
                json.dump(full_config, f, indent=2)

            self.logger.info(f"Configuration saved to {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save configuration: {str(e)}")
            return False

    def load_configuration(self, config_path: str) -> Optional[Dict[str, Any]]:
        """
        Load configuration from file.

        Args:
            config_path: Path to configuration file

        Returns:
            Dict with configuration data or None if failed
        """
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)

            # Validate configuration
            is_valid, message = self.validate_config(config_data)

            if not is_valid:
                self.logger.error(f"Configuration validation failed: {message}")
                return None

            self.logger.info(f"Configuration loaded from {config_path}")
            return config_data

        except FileNotFoundError:
            self.logger.error(f"Configuration file not found: {config_path}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in configuration file: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            return None

    def validate_config(self, config_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate configuration structure and data.

        Args:
            config_data: Configuration to validate

        Returns:
            Tuple of (is_valid, message)
        """
        # Check version
        if 'config_version' not in config_data:
            return False, "Missing config_version"

        version = config_data['config_version']
        if version != self.CONFIG_VERSION:
            self.logger.warning(f"Config version mismatch: {version} vs {self.CONFIG_VERSION}")
            # Could implement version migration here

        # Check required sections
        for section in self.REQUIRED_SECTIONS:
            if section not in config_data:
                return False, f"Missing required section: {section}"

        # Validate chamber specs if present
        if 'chamber_specs' in config_data:
            chamber_specs = config_data['chamber_specs']

            # Check for required chamber parameters
            required_params = ['length', 'width', 'height']
            for param in required_params:
                if param not in chamber_specs:
                    return False, f"Missing chamber parameter: {param}"

                # Validate ranges
                value = chamber_specs[param]
                if not isinstance(value, (int, float)) or value <= 0:
                    return False, f"Invalid chamber {param}: {value}"

        # Validate UV system if present
        if 'uv_system' in config_data:
            uv_system = config_data['uv_system']

            if 'uv_intensity' in uv_system:
                intensity = uv_system['uv_intensity']
                if not 0 <= intensity <= 1000:
                    return False, f"UV intensity out of range: {intensity}"

        # Verify file hash if present
        if 'metadata' in config_data and 'file_hash' in config_data['metadata']:
            stored_hash = config_data['metadata']['file_hash']

            # Create a copy without metadata for hash verification
            verify_data = {k: v for k, v in config_data.items() if k != 'metadata'}
            config_str = json.dumps(verify_data, sort_keys=True)
            computed_hash = hashlib.sha256(config_str.encode()).hexdigest()

            if stored_hash != computed_hash:
                self.logger.warning("Configuration file hash mismatch - file may have been modified")

        return True, "Configuration is valid"

    def apply_configuration(self, config_data: Dict[str, Any], session_state=None) -> bool:
        """
        Apply configuration to the application.

        Args:
            config_data: Configuration to apply
            session_state: Streamlit session state (optional)

        Returns:
            bool: True if successful
        """
        try:
            # If session_state is provided, update it
            if session_state is not None:
                for key, value in config_data.items():
                    if key not in ['config_version', 'saved_date', 'metadata']:
                        session_state[key] = value

            self.logger.info("Configuration applied successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to apply configuration: {str(e)}")
            return False

    def get_config_templates(self) -> List[Dict[str, str]]:
        """
        Get list of available configuration templates.

        Returns:
            List of template info dicts
        """
        templates = []

        for template_file in self.templates_dir.glob('*.json'):
            try:
                with open(template_file, 'r') as f:
                    template_data = json.load(f)

                templates.append({
                    'name': template_file.stem,
                    'path': str(template_file),
                    'description': template_data.get('description', 'No description'),
                    'created': template_data.get('saved_date', 'Unknown')
                })

            except Exception as e:
                self.logger.error(f"Error reading template {template_file}: {e}")

        return templates

    def create_template(self, name: str, config_data: Dict[str, Any],
                       description: str = '') -> bool:
        """
        Create a configuration template.

        Args:
            name: Template name
            config_data: Configuration data
            description: Template description

        Returns:
            bool: True if successful
        """
        try:
            # Add template metadata
            template_data = config_data.copy()
            template_data['description'] = description
            template_data['template_name'] = name
            template_data['created_date'] = datetime.now().isoformat()

            # Save template
            template_path = self.templates_dir / f"{name}.json"

            return self.save_configuration(
                template_data,
                str(template_path),
                include_metadata=True
            )

        except Exception as e:
            self.logger.error(f"Failed to create template: {str(e)}")
            return False

    def load_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Load a configuration template.

        Args:
            template_name: Name of the template

        Returns:
            Dict with template data or None
        """
        template_path = self.templates_dir / f"{template_name}.json"
        return self.load_configuration(str(template_path))

    def delete_template(self, template_name: str) -> bool:
        """
        Delete a configuration template.

        Args:
            template_name: Name of template to delete

        Returns:
            bool: True if successful
        """
        try:
            template_path = self.templates_dir / f"{template_name}.json"

            if template_path.exists():
                template_path.unlink()
                self.logger.info(f"Template deleted: {template_name}")
                return True
            else:
                self.logger.warning(f"Template not found: {template_name}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to delete template: {str(e)}")
            return False

    def merge_configurations(self, base_config: Dict[str, Any],
                           overlay_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge two configurations (overlay takes precedence).

        Args:
            base_config: Base configuration
            overlay_config: Configuration to overlay

        Returns:
            Dict with merged configuration
        """
        merged = base_config.copy()

        for key, value in overlay_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                # Recursively merge dictionaries
                merged[key] = self.merge_configurations(merged[key], value)
            else:
                # Override value
                merged[key] = value

        return merged

    def export_partial_config(self, full_config: Dict[str, Any],
                             sections: List[str], output_path: str) -> bool:
        """
        Export only specific sections of configuration.

        Args:
            full_config: Full configuration
            sections: List of section names to export
            output_path: Output file path

        Returns:
            bool: True if successful
        """
        try:
            partial_config = {}

            for section in sections:
                if section in full_config:
                    partial_config[section] = full_config[section]
                else:
                    self.logger.warning(f"Section not found in config: {section}")

            # Add metadata
            partial_config['config_version'] = self.CONFIG_VERSION
            partial_config['saved_date'] = datetime.now().isoformat()
            partial_config['partial_export'] = True
            partial_config['exported_sections'] = sections

            return self.save_configuration(partial_config, output_path)

        except Exception as e:
            self.logger.error(f"Failed to export partial config: {str(e)}")
            return False

    def compare_configurations(self, config1: Dict[str, Any],
                              config2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two configurations and return differences.

        Args:
            config1: First configuration
            config2: Second configuration

        Returns:
            Dict with differences
        """
        differences = {
            'only_in_config1': [],
            'only_in_config2': [],
            'different_values': {}
        }

        # Flatten both configs
        flat1 = self._flatten_dict(config1)
        flat2 = self._flatten_dict(config2)

        # Find keys only in config1
        for key in flat1:
            if key not in flat2:
                differences['only_in_config1'].append(key)

        # Find keys only in config2
        for key in flat2:
            if key not in flat1:
                differences['only_in_config2'].append(key)

        # Find different values
        for key in flat1:
            if key in flat2 and flat1[key] != flat2[key]:
                differences['different_values'][key] = {
                    'config1': flat1[key],
                    'config2': flat2[key]
                }

        return differences

    def _flatten_dict(self, d: dict, parent_key: str = '', sep: str = '.') -> dict:
        """Flatten nested dictionary with dot notation keys."""
        items = []

        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k

            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))

        return dict(items)

    def get_config_summary(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a summary of configuration data.

        Args:
            config_data: Configuration to summarize

        Returns:
            Dict with summary information
        """
        summary = {
            'version': config_data.get('config_version', 'Unknown'),
            'saved_date': config_data.get('saved_date', 'Unknown'),
            'sections': list(config_data.keys()),
            'section_count': len([k for k in config_data.keys()
                                if k not in ['config_version', 'saved_date', 'metadata']])
        }

        # Add specific summaries for important sections
        if 'chamber_specs' in config_data:
            chamber = config_data['chamber_specs']
            summary['chamber_volume'] = (
                chamber.get('length', 0) *
                chamber.get('width', 0) *
                chamber.get('height', 0)
            ) / 1e9  # Convert to m³

        if 'uv_system' in config_data:
            summary['uv_intensity'] = config_data['uv_system'].get('uv_intensity', 'Not set')

        return summary
