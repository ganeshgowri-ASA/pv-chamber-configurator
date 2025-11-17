"""
PV Chamber Configurator - Modules Package
Phase 9: Integration Layer + White-Labeling + Internationalization
"""

from .integration_layer import IntegrationLayer
from .white_label_manager import WhiteLabelManager
from .i18n_manager import I18nManager
from .config_manager import ConfigManager

__all__ = [
    'IntegrationLayer',
    'WhiteLabelManager',
    'I18nManager',
    'ConfigManager'
]

__version__ = '1.0.0'
