"""
Report Templates Module
Management and loading of report templates
"""

import json
import os
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path


class ReportTemplate:
    """Report template configuration"""

    def __init__(self, template_config: Dict[str, Any]):
        """
        Initialize template from configuration

        Args:
            template_config: Template configuration dictionary
        """
        self.config = template_config
        self.name = template_config.get('name', 'Untitled')
        self.report_type = template_config.get('report_type', 'general')
        self.version = template_config.get('version', '1.0')

        # Branding
        self.branding = template_config.get('branding', {})
        self.company_name = self.branding.get('company_name', '')
        self.logo_path = self.branding.get('logo_path', '')
        self.primary_color = self.branding.get('primary_color', '#2c5aa0')
        self.secondary_color = self.branding.get('secondary_color', '#1f4788')

        # Layout settings
        self.layout = template_config.get('layout', {})
        self.page_size = self.layout.get('page_size', 'A4')
        self.orientation = self.layout.get('orientation', 'portrait')
        self.margins = self.layout.get('margins', {
            'top': 20, 'bottom': 20, 'left': 15, 'right': 15
        })

        # Typography
        self.typography = template_config.get('typography', {})
        self.font_family = self.typography.get('font_family', 'Helvetica')
        self.font_sizes = self.typography.get('font_sizes', {
            'title': 24, 'header': 16, 'subheader': 14, 'body': 11
        })

        # Report sections
        self.sections = template_config.get('sections', [])

        # Watermark settings
        self.watermark = template_config.get('watermark', {})

    def get_section_order(self) -> List[str]:
        """Get ordered list of section names"""
        return [section['name'] for section in self.sections]

    def get_section_config(self, section_name: str) -> Optional[Dict]:
        """
        Get configuration for a specific section

        Args:
            section_name: Name of the section

        Returns:
            Section configuration or None
        """
        for section in self.sections:
            if section['name'] == section_name:
                return section
        return None

    def is_section_enabled(self, section_name: str) -> bool:
        """
        Check if a section is enabled

        Args:
            section_name: Name of the section

        Returns:
            True if enabled
        """
        section = self.get_section_config(section_name)
        if section:
            return section.get('enabled', True)
        return False


class TemplateManager:
    """Manages report templates"""

    def __init__(self, templates_dir: str = 'templates/report_templates'):
        """
        Initialize template manager

        Args:
            templates_dir: Directory containing template JSON files
        """
        self.templates_dir = templates_dir
        self.templates = {}
        self._load_templates()

    def _load_templates(self):
        """Load all templates from directory"""
        if not os.path.exists(self.templates_dir):
            return

        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.json'):
                template_path = os.path.join(self.templates_dir, filename)
                try:
                    with open(template_path, 'r') as f:
                        config = json.load(f)
                        template = ReportTemplate(config)
                        self.templates[template.name] = template
                except Exception as e:
                    print(f"Error loading template {filename}: {e}")

    def get_template(self, template_name: str) -> Optional[ReportTemplate]:
        """
        Get a template by name

        Args:
            template_name: Name of the template

        Returns:
            ReportTemplate or None
        """
        return self.templates.get(template_name)

    def list_templates(self) -> List[str]:
        """
        Get list of available template names

        Returns:
            List of template names
        """
        return list(self.templates.keys())

    def list_templates_by_type(self, report_type: str) -> List[str]:
        """
        Get templates filtered by report type

        Args:
            report_type: Report type to filter

        Returns:
            List of matching template names
        """
        return [
            name for name, template in self.templates.items()
            if template.report_type == report_type
        ]

    def create_custom_template(self, config: Dict[str, Any],
                              save_path: Optional[str] = None) -> ReportTemplate:
        """
        Create a custom template from configuration

        Args:
            config: Template configuration
            save_path: Optional path to save template JSON

        Returns:
            ReportTemplate instance
        """
        template = ReportTemplate(config)

        # Add to templates
        self.templates[template.name] = template

        # Save if path provided
        if save_path:
            with open(save_path, 'w') as f:
                json.dump(config, f, indent=2)

        return template

    def validate_template(self, template_config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate template configuration

        Args:
            template_config: Configuration to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check required fields
        required_fields = ['name', 'report_type', 'sections']
        for field in required_fields:
            if field not in template_config:
                errors.append(f"Missing required field: {field}")

        # Validate sections
        if 'sections' in template_config:
            sections = template_config['sections']
            if not isinstance(sections, list):
                errors.append("'sections' must be a list")
            else:
                for i, section in enumerate(sections):
                    if 'name' not in section:
                        errors.append(f"Section {i} missing 'name' field")

        # Validate branding if present
        if 'branding' in template_config:
            branding = template_config['branding']
            if 'logo_path' in branding:
                logo_path = branding['logo_path']
                if logo_path and not os.path.exists(logo_path):
                    errors.append(f"Logo file not found: {logo_path}")

        return (len(errors) == 0, errors)


def load_template(template_name: str,
                 templates_dir: str = 'templates/report_templates') -> Optional[ReportTemplate]:
    """
    Load a specific template

    Args:
        template_name: Name of the template file (without .json)
        templates_dir: Directory containing templates

    Returns:
        ReportTemplate or None
    """
    template_path = os.path.join(templates_dir, f'{template_name}.json')

    if not os.path.exists(template_path):
        return None

    try:
        with open(template_path, 'r') as f:
            config = json.load(f)
            return ReportTemplate(config)
    except Exception as e:
        print(f"Error loading template: {e}")
        return None


def get_default_template(report_type: str) -> ReportTemplate:
    """
    Get default template for a report type

    Args:
        report_type: Type of report

    Returns:
        ReportTemplate with default configuration
    """
    default_configs = {
        'technical_specification': {
            'name': 'Default Technical Specification',
            'report_type': 'technical_specification',
            'version': '1.0',
            'branding': {
                'company_name': 'Company Name',
                'primary_color': '#2c5aa0',
                'secondary_color': '#1f4788'
            },
            'layout': {
                'page_size': 'A4',
                'orientation': 'portrait',
                'margins': {'top': 20, 'bottom': 20, 'left': 15, 'right': 15}
            },
            'typography': {
                'font_family': 'Helvetica',
                'font_sizes': {'title': 24, 'header': 16, 'subheader': 14, 'body': 11}
            },
            'sections': [
                {'name': 'Executive Summary', 'enabled': True},
                {'name': 'Chamber Specifications', 'enabled': True},
                {'name': 'Performance Characteristics', 'enabled': True},
                {'name': 'CFD Simulation Results', 'enabled': True},
                {'name': 'UV System Analysis', 'enabled': True},
                {'name': 'Component List', 'enabled': True},
                {'name': 'Appendices', 'enabled': True}
            ]
        },
        'test_execution': {
            'name': 'Default Test Execution',
            'report_type': 'test_execution',
            'version': '1.0',
            'branding': {
                'company_name': 'Company Name',
                'primary_color': '#2c5aa0'
            },
            'layout': {'page_size': 'A4'},
            'sections': [
                {'name': 'Test Parameters', 'enabled': True},
                {'name': 'Data Logs', 'enabled': True},
                {'name': 'Uniformity Measurements', 'enabled': True},
                {'name': 'Alarm History', 'enabled': True},
                {'name': 'Pass/Fail Status', 'enabled': True}
            ]
        },
        'compliance': {
            'name': 'Default Compliance',
            'report_type': 'compliance',
            'version': '1.0',
            'branding': {
                'company_name': 'Company Name',
                'primary_color': '#2c5aa0'
            },
            'layout': {'page_size': 'A4'},
            'sections': [
                {'name': 'IEC Compliance', 'enabled': True},
                {'name': 'Calibration Certificates', 'enabled': True},
                {'name': 'Uncertainty Budgets', 'enabled': True},
                {'name': 'Traceability Chain', 'enabled': True}
            ]
        },
        'commercial_proposal': {
            'name': 'Default Commercial Proposal',
            'report_type': 'commercial_proposal',
            'version': '1.0',
            'branding': {
                'company_name': 'Company Name',
                'primary_color': '#2c5aa0'
            },
            'layout': {'page_size': 'A4'},
            'sections': [
                {'name': 'Executive Summary', 'enabled': True},
                {'name': 'Technical Specifications', 'enabled': True},
                {'name': 'Quote and Pricing', 'enabled': True},
                {'name': 'ROI Analysis', 'enabled': True},
                {'name': 'Payment Terms', 'enabled': True},
                {'name': 'Delivery Timeline', 'enabled': True}
            ]
        },
        'business_analysis': {
            'name': 'Default Business Analysis',
            'report_type': 'business_analysis',
            'version': '1.0',
            'branding': {
                'company_name': 'Company Name',
                'primary_color': '#2c5aa0'
            },
            'layout': {'page_size': 'A4'},
            'sections': [
                {'name': 'TCO Breakdown', 'enabled': True},
                {'name': 'ROI Metrics', 'enabled': True},
                {'name': 'Competitive Comparison', 'enabled': True},
                {'name': 'Sensitivity Analysis', 'enabled': True}
            ]
        }
    }

    config = default_configs.get(report_type, default_configs['technical_specification'])
    return ReportTemplate(config)
