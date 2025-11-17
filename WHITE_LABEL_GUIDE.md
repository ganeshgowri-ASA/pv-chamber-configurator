# White-Label Configuration Guide

## Overview

The White-Label Manager allows you to customize the PV Chamber Configurator with your company's branding, including logos, colors, fonts, and company information.

## Features

- **Logo Upload**: Upload and manage company logos (PNG, JPG, SVG)
- **Brand Colors**: Customize primary and secondary brand colors
- **Font Selection**: Choose from professional font families
- **Company Information**: Set company name, address, contact details
- **Branding Preview**: Preview changes before applying
- **Configuration Persistence**: Save and restore branding settings

## Getting Started

### 1. Access White-Label Settings

In the Streamlit app, navigate to the "White-Label Settings" tab.

### 2. Upload Your Logo

#### Requirements

- **Formats**: PNG, JPG, JPEG, SVG
- **Maximum Size**: 2MB
- **Maximum Dimensions**: 1000x500 pixels
- **Recommended**: Transparent background PNG for best results

#### Steps

1. Click "Choose File" under Logo Upload
2. Select your logo file
3. Preview the logo
4. Click "Upload Logo" to apply

```python
# Programmatic upload
from modules import WhiteLabelManager

wl_manager = WhiteLabelManager()
success, message = wl_manager.upload_logo(uploaded_file)

if success:
    print("Logo uploaded successfully!")
```

### 3. Set Company Information

Update your company details:

- **Company Name**: Your organization's name
- **Address**: Complete business address
- **Email**: Contact email address
- **Phone**: Contact phone number
- **Website**: Company website URL

```python
company_data = {
    'name': 'Acme Solar Testing',
    'address': '123 Innovation Drive, Tech Park, Bangalore 560001',
    'email': 'contact@acmesolar.com',
    'phone': '+91-80-1234-5678',
    'website': 'https://acmesolar.com'
}

wl_manager.set_company_info(company_data)
```

### 4. Configure Brand Colors

#### Color Selection

Choose colors that represent your brand:

- **Primary Color**: Used for buttons, headers, main UI elements
- **Secondary Color**: Used for links, accents, secondary elements

#### Color Format

Use hex color codes:
- 6-digit: `#1E40AF`
- 3-digit: `#F00`

```python
wl_manager.set_brand_colors(
    primary='#1E40AF',    # Deep blue
    secondary='#3B82F6'   # Light blue
)
```

#### Recommended Color Combinations

**Professional Blue**:
- Primary: `#1E40AF`
- Secondary: `#3B82F6`

**Modern Green**:
- Primary: `#047857`
- Secondary: `#10B981`

**Corporate Gray**:
- Primary: `#374151`
- Secondary: `#6B7280`

**Energy Orange**:
- Primary: `#EA580C`
- Secondary: `#FB923C`

### 5. Select Font Family

Choose from professional font families:

- **Helvetica**: Classic, clean, widely recognized
- **Arial**: Universal, highly readable
- **Roboto**: Modern, geometric, Google's signature font
- **Open Sans**: Friendly, optimized for legibility
- **Lato**: Semi-rounded, professional warmth
- **Montserrat**: Urban, geometric elegance
- **Source Sans Pro**: Clean, Adobe's open-source font
- **Inter**: Highly readable, designed for UI
- **Poppins**: Geometric, modern Indian-friendly

```python
wl_manager.set_font_family('Roboto')
```

## Configuration File

### Location

`config/white_label_config.json`

### Structure

```json
{
  "company": {
    "name": "Your Company Name",
    "address": "123 Street, City, State, PIN",
    "email": "contact@company.com",
    "phone": "+91-XXX-XXX-XXXX",
    "website": "https://company.com"
  },
  "branding": {
    "logo_path": "assets/white_label/logo.png",
    "primary_color": "#1E40AF",
    "secondary_color": "#3B82F6",
    "font_family": "Helvetica"
  },
  "locale": "en_US",
  "last_updated": "2025-01-20T10:30:00Z"
}
```

## API Reference

### Initialization

```python
from modules import WhiteLabelManager

# Use default config path
wl_manager = WhiteLabelManager()

# Or specify custom path
wl_manager = WhiteLabelManager('custom/path/config.json')
```

### Logo Management

#### Upload Logo

```python
success, message = wl_manager.upload_logo(uploaded_file)
```

#### Validate Logo

```python
is_valid, message = wl_manager.validate_logo(uploaded_file)
```

#### Get Logo Path

```python
logo_path = wl_manager.get_logo_path()
```

#### Get Logo as Base64

```python
# For embedding in HTML/CSS
logo_base64 = wl_manager.get_logo_base64()
# Returns: "data:image/png;base64,iVBORw0KGgo..."
```

### Branding Configuration

#### Apply Branding

```python
branding = wl_manager.apply_branding()
# Returns dict with company, branding, and logo_base64
```

#### Preview Branding

```python
preview = wl_manager.preview_branding()
print(f"Company: {preview['company_name']}")
print(f"Primary Color: {preview['primary_color']}")
```

#### Get CSS Variables

```python
css = wl_manager.get_css_variables()
# Returns CSS with :root variables
```

### Configuration Management

#### Save Configuration

```python
wl_manager.save_config()
```

#### Load Configuration

```python
wl_manager.load_config()
```

#### Reset to Default

```python
wl_manager.reset_to_default()
```

#### Export Branding Package

```python
wl_manager.export_branding_package('branding_backup.json')
```

## Advanced Usage

### Custom CSS Integration

```python
import streamlit as st
from modules import WhiteLabelManager

wl_manager = WhiteLabelManager()

# Get CSS variables
css_vars = wl_manager.get_css_variables()

# Apply to Streamlit
st.markdown(f"""
<style>
{css_vars}

.custom-element {{
    background-color: var(--primary-color);
    color: white;
}}
</style>
""", unsafe_allow_html=True)
```

### Logo in Reports

```python
logo_base64 = wl_manager.get_logo_base64()

if logo_base64:
    html_report = f"""
    <html>
      <body>
        <img src="{logo_base64}" style="width: 200px;">
        <h1>PV Chamber Test Report</h1>
        ...
      </body>
    </html>
    """
```

### Conditional Branding

```python
# Apply different branding based on user/client
if client_type == 'premium':
    wl_manager.load_config('config/premium_branding.json')
else:
    wl_manager.load_config('config/standard_branding.json')
```

## Branding Application Across Modules

White-label branding is automatically applied to:

1. **Main Application**: Headers, titles, colors
2. **Reports (Phase 8)**: PDF headers, footers, logos
3. **Quotes (Phase 6)**: Email templates, PDF quotes
4. **Business Analysis (Phase 7)**: Charts color schemes
5. **Virtual HMI (Phase 5)**: Control panel styling

## Best Practices

### Logo Design

1. **Vector Format**: Use SVG for scalability
2. **Transparent Background**: PNG with transparency works best
3. **Horizontal Layout**: Logos wider than tall display better
4. **Size**: Keep under 1MB for fast loading
5. **Color**: Ensure logo works with your brand colors

### Color Selection

1. **Contrast**: Ensure sufficient contrast for readability (WCAG AA minimum)
2. **Consistency**: Use colors from your existing brand guidelines
3. **Testing**: Preview on different screens and backgrounds
4. **Accessibility**: Consider color-blind users

### Font Selection

1. **Readability**: Choose fonts optimized for screen reading
2. **Consistency**: Match your company's existing typography
3. **Fallback**: System will fallback to sans-serif if font unavailable

## Troubleshooting

### Logo Not Appearing

1. Check file format is supported (PNG, JPG, SVG)
2. Verify file size is under 2MB
3. Check permissions on `assets/white_label/` directory
4. Ensure logo path in config is correct

```python
# Debug logo issues
logo_path = wl_manager.get_logo_path()
if logo_path:
    print(f"Logo path: {logo_path}")
    print(f"File exists: {Path(logo_path).exists()}")
else:
    print("No logo configured")
```

### Colors Not Applying

1. Clear browser cache
2. Check hex color format is valid
3. Reload the Streamlit app

```python
# Validate colors
is_valid = wl_manager._is_valid_hex_color('#1E40AF')
print(f"Color valid: {is_valid}")
```

### Configuration Not Saving

1. Check write permissions on `config/` directory
2. Verify JSON syntax in config file
3. Check disk space

```python
# Test save
success = wl_manager.save_config()
if not success:
    print("Failed to save configuration")
```

## Security Considerations

1. **File Uploads**: Only allow trusted users to upload logos
2. **File Validation**: Always validate uploaded files
3. **XSS Prevention**: Sanitize company information inputs
4. **Path Traversal**: Don't allow custom file paths from users

## Migration Guide

### From Previous Version

If upgrading from a version without white-labeling:

1. Backup existing configuration
2. Install new requirements: `pip install Pillow>=10.0.0`
3. Run application to generate default config
4. Upload your logo and update settings
5. Test all branding elements

### Exporting Configuration

```python
# Export for backup or migration
wl_manager.export_branding_package('backups/branding_2025_01_20.json')
```

### Importing Configuration

```python
# Restore from backup
wl_manager.load_config('backups/branding_2025_01_20.json')
```

## Examples

### Complete Branding Setup

```python
from modules import WhiteLabelManager

# Initialize
wl_manager = WhiteLabelManager()

# Set company info
wl_manager.set_company_info({
    'name': 'SolarTech India',
    'address': 'Tower A, Tech Park, Bangalore 560001, India',
    'email': 'info@solartech.in',
    'phone': '+91-80-4567-8900',
    'website': 'https://solartech.in'
})

# Set colors
wl_manager.set_brand_colors(
    primary='#047857',
    secondary='#10B981'
)

# Set font
wl_manager.set_font_family('Inter')

# Save
wl_manager.save_config()

print("Branding configured successfully!")
```

## Support

For issues or questions:
- Check the logs: `logging.getLogger('WhiteLabelManager')`
- Review configuration file: `config/white_label_config.json`
- Test with default settings: `wl_manager.reset_to_default()`
