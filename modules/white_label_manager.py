"""
White Label Manager for PV Chamber Configurator
Handles logo upload, company branding, and customization
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import base64
from io import BytesIO


class WhiteLabelManager:
    """
    Manages white-label configuration including logos, branding, and company information.
    """

    # Supported image formats
    SUPPORTED_FORMATS = ['png', 'jpg', 'jpeg', 'svg']

    # Image constraints
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
    MAX_WIDTH = 1000
    MAX_HEIGHT = 500

    # Professional font families
    FONT_FAMILIES = [
        'Helvetica',
        'Arial',
        'Roboto',
        'Open Sans',
        'Lato',
        'Montserrat',
        'Source Sans Pro',
        'Inter',
        'Poppins'
    ]

    def __init__(self, config_path: str = 'config/white_label_config.json'):
        """
        Initialize the white label manager.

        Args:
            config_path: Path to the white label configuration file
        """
        self.config_path = Path(config_path)
        self.logger = self._setup_logger()
        self.config = self._load_default_config()

        # Create necessary directories
        self._create_directories()

        # Load existing config if available
        if self.config_path.exists():
            self.load_config()

        self.logger.info("White Label Manager initialized")

    def _setup_logger(self) -> logging.Logger:
        """Setup logging for the white label manager."""
        logger = logging.getLogger('WhiteLabelManager')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _create_directories(self) -> None:
        """Create necessary directories for white label assets."""
        directories = [
            'assets/white_label',
            'config'
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default white label configuration."""
        return {
            'company': {
                'name': 'Your Company Name',
                'address': '123 Street, City, State, PIN',
                'email': 'contact@company.com',
                'phone': '+91-XXX-XXX-XXXX',
                'website': 'https://company.com'
            },
            'branding': {
                'logo_path': None,
                'primary_color': '#1E40AF',
                'secondary_color': '#3B82F6',
                'font_family': 'Helvetica'
            },
            'locale': 'en_US',
            'last_updated': datetime.now().isoformat()
        }

    # Logo Management
    def upload_logo(self, uploaded_file) -> Tuple[bool, str]:
        """
        Upload and process logo file.

        Args:
            uploaded_file: File object from Streamlit file_uploader

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate file
            is_valid, message = self.validate_logo(uploaded_file)
            if not is_valid:
                return False, message

            # Get file extension
            file_extension = uploaded_file.name.split('.')[-1].lower()

            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"logo_{timestamp}.{file_extension}"
            filepath = Path('assets/white_label') / filename

            # Save file
            with open(filepath, 'wb') as f:
                f.write(uploaded_file.getbuffer())

            # Update config
            self.config['branding']['logo_path'] = str(filepath)
            self.save_config()

            self.logger.info(f"Logo uploaded successfully: {filepath}")
            return True, f"Logo uploaded successfully as {filename}"

        except Exception as e:
            error_msg = f"Failed to upload logo: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def validate_logo(self, uploaded_file) -> Tuple[bool, str]:
        """
        Validate logo file.

        Args:
            uploaded_file: File object to validate

        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        # Check if file exists
        if uploaded_file is None:
            return False, "No file provided"

        # Check file size
        file_size = len(uploaded_file.getvalue())
        if file_size > self.MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            return False, f"File size ({size_mb:.2f}MB) exceeds maximum allowed size (2MB)"

        # Check file extension
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension not in self.SUPPORTED_FORMATS:
            return False, f"Unsupported file format. Allowed: {', '.join(self.SUPPORTED_FORMATS)}"

        # For raster images (PNG, JPG), check dimensions
        if file_extension in ['png', 'jpg', 'jpeg']:
            try:
                from PIL import Image
                image = Image.open(uploaded_file)
                width, height = image.size

                if width > self.MAX_WIDTH or height > self.MAX_HEIGHT:
                    return False, f"Image dimensions ({width}x{height}) exceed maximum allowed ({self.MAX_WIDTH}x{self.MAX_HEIGHT})"

                # Reset file pointer
                uploaded_file.seek(0)

            except ImportError:
                self.logger.warning("PIL not available, skipping dimension check")
            except Exception as e:
                return False, f"Failed to validate image: {str(e)}"

        return True, "File is valid"

    def optimize_logo(self, input_path: str, max_width: int = 400) -> bool:
        """
        Optimize logo image (resize and compress).

        Args:
            input_path: Path to input image
            max_width: Maximum width for the optimized image

        Returns:
            bool: True if successful
        """
        try:
            from PIL import Image

            img = Image.open(input_path)

            # Calculate new dimensions maintaining aspect ratio
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

            # Save optimized image
            img.save(input_path, optimize=True, quality=85)

            self.logger.info(f"Logo optimized: {input_path}")
            return True

        except ImportError:
            self.logger.warning("PIL not available, skipping optimization")
            return False
        except Exception as e:
            self.logger.error(f"Failed to optimize logo: {str(e)}")
            return False

    def get_logo_path(self) -> Optional[str]:
        """
        Get the path to the current logo.

        Returns:
            str: Path to logo or None if not set
        """
        logo_path = self.config['branding'].get('logo_path')

        if logo_path and Path(logo_path).exists():
            return logo_path

        return None

    def get_logo_base64(self) -> Optional[str]:
        """
        Get logo as base64 encoded string for embedding.

        Returns:
            str: Base64 encoded logo or None
        """
        logo_path = self.get_logo_path()
        if not logo_path:
            return None

        try:
            with open(logo_path, 'rb') as f:
                encoded = base64.b64encode(f.read()).decode()

            # Determine MIME type
            ext = Path(logo_path).suffix.lower()
            mime_types = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.svg': 'image/svg+xml'
            }
            mime_type = mime_types.get(ext, 'image/png')

            return f"data:{mime_type};base64,{encoded}"

        except Exception as e:
            self.logger.error(f"Failed to encode logo: {str(e)}")
            return None

    # Branding
    def set_company_info(self, company_data: Dict[str, str]) -> bool:
        """
        Set company information.

        Args:
            company_data: Dictionary with company information

        Returns:
            bool: True if successful
        """
        try:
            self.config['company'].update(company_data)
            self.config['last_updated'] = datetime.now().isoformat()
            self.save_config()

            self.logger.info("Company information updated")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update company info: {str(e)}")
            return False

    def set_brand_colors(self, primary: str, secondary: str) -> bool:
        """
        Set brand colors.

        Args:
            primary: Primary color (hex format)
            secondary: Secondary color (hex format)

        Returns:
            bool: True if successful
        """
        try:
            # Validate hex color format
            if not self._is_valid_hex_color(primary):
                raise ValueError(f"Invalid primary color format: {primary}")
            if not self._is_valid_hex_color(secondary):
                raise ValueError(f"Invalid secondary color format: {secondary}")

            self.config['branding']['primary_color'] = primary
            self.config['branding']['secondary_color'] = secondary
            self.config['last_updated'] = datetime.now().isoformat()
            self.save_config()

            self.logger.info(f"Brand colors updated: primary={primary}, secondary={secondary}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update brand colors: {str(e)}")
            return False

    def _is_valid_hex_color(self, color: str) -> bool:
        """Validate hex color format."""
        if not color.startswith('#'):
            return False
        if len(color) not in [4, 7]:  # #RGB or #RRGGBB
            return False
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False

    def set_font_family(self, font_name: str) -> bool:
        """
        Set brand font family.

        Args:
            font_name: Font family name

        Returns:
            bool: True if successful
        """
        try:
            if font_name not in self.FONT_FAMILIES:
                self.logger.warning(f"Font {font_name} not in recommended list")

            self.config['branding']['font_family'] = font_name
            self.config['last_updated'] = datetime.now().isoformat()
            self.save_config()

            self.logger.info(f"Font family updated: {font_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update font family: {str(e)}")
            return False

    def apply_branding(self) -> Dict[str, Any]:
        """
        Get branding configuration for application.

        Returns:
            Dict with branding configuration
        """
        return {
            'company': self.config['company'],
            'branding': self.config['branding'],
            'logo_base64': self.get_logo_base64()
        }

    # Configuration
    def save_config(self) -> bool:
        """
        Save configuration to file.

        Returns:
            bool: True if successful
        """
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)

            self.logger.info(f"Configuration saved to {self.config_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {str(e)}")
            return False

    def load_config(self) -> bool:
        """
        Load configuration from file.

        Returns:
            bool: True if successful
        """
        try:
            with open(self.config_path, 'r') as f:
                loaded_config = json.load(f)

            # Merge with default config to ensure all keys exist
            self.config = self._load_default_config()
            self._deep_update(self.config, loaded_config)

            self.logger.info(f"Configuration loaded from {self.config_path}")
            return True
        except FileNotFoundError:
            self.logger.warning(f"Config file not found: {self.config_path}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            return False

    def _deep_update(self, target: dict, source: dict) -> None:
        """Deep update target dict with source dict."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value

    def reset_to_default(self) -> bool:
        """
        Reset configuration to default values.

        Returns:
            bool: True if successful
        """
        try:
            self.config = self._load_default_config()
            self.save_config()

            self.logger.info("Configuration reset to defaults")
            return True
        except Exception as e:
            self.logger.error(f"Failed to reset configuration: {str(e)}")
            return False

    def preview_branding(self) -> Dict[str, Any]:
        """
        Get branding preview data.

        Returns:
            Dict with preview information
        """
        return {
            'company_name': self.config['company']['name'],
            'logo_available': self.get_logo_path() is not None,
            'primary_color': self.config['branding']['primary_color'],
            'secondary_color': self.config['branding']['secondary_color'],
            'font_family': self.config['branding']['font_family'],
            'last_updated': self.config.get('last_updated', 'Never')
        }

    def get_css_variables(self) -> str:
        """
        Get CSS variables for branding.

        Returns:
            str: CSS variable declarations
        """
        return f"""
        :root {{
            --primary-color: {self.config['branding']['primary_color']};
            --secondary-color: {self.config['branding']['secondary_color']};
            --font-family: {self.config['branding']['font_family']}, sans-serif;
        }}
        """

    def export_branding_package(self, output_path: str) -> bool:
        """
        Export complete branding package as JSON.

        Args:
            output_path: Path to save the package

        Returns:
            bool: True if successful
        """
        try:
            package = {
                'config': self.config,
                'logo_base64': self.get_logo_base64(),
                'exported_at': datetime.now().isoformat()
            }

            with open(output_path, 'w') as f:
                json.dump(package, f, indent=2)

            self.logger.info(f"Branding package exported to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export branding package: {str(e)}")
            return False
