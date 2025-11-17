"""
White-Label Branding Configuration UI
Allows customization of company branding, colors, and logos
"""

import streamlit as st
import yaml
import os
from PIL import Image
import io


def load_config() -> dict:
    """Load configuration from YAML file"""
    config_path = "config.yaml"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}


def save_config(config: dict) -> bool:
    """Save configuration to YAML file"""
    try:
        config_path = "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        return True
    except Exception as e:
        st.error(f"Error saving configuration: {e}")
        return False


def render_branding_config():
    """Render branding configuration UI"""

    st.title("⚙️ White-Label Branding Configuration")

    st.markdown("""
    Customize this application with your company's branding. Changes will be applied
    immediately and saved for future sessions.
    """)

    # Load current config
    config = load_config()

    # Create tabs for different configuration sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏢 Company Info",
        "🎨 Colors & Theme",
        "🖼️ Logo & Images",
        "⚙️ Technical Defaults"
    ])

    # Tab 1: Company Information
    with tab1:
        st.subheader("Company Information")

        col1, col2 = st.columns(2)

        with col1:
            company_name = st.text_input(
                "Company Name",
                value=config.get('company', {}).get('name', 'PV Testing Solutions'),
                help="Your company's legal name"
            )

            company_tagline = st.text_input(
                "Tagline",
                value=config.get('company', {}).get('tagline', 'Professional Photovoltaic Test Equipment'),
                help="Company tagline or slogan"
            )

            company_address = st.text_area(
                "Address",
                value=config.get('company', {}).get('address', 'India'),
                help="Complete company address"
            )

        with col2:
            company_phone = st.text_input(
                "Phone",
                value=config.get('company', {}).get('phone', '+91-XXXXXXXXXX'),
                help="Contact phone number"
            )

            company_email = st.text_input(
                "Email",
                value=config.get('company', {}).get('email', 'info@pvtesting.com'),
                help="Contact email address"
            )

            company_website = st.text_input(
                "Website",
                value=config.get('company', {}).get('website', 'https://www.pvtesting.com'),
                help="Company website URL"
            )

        if st.button("💾 Save Company Information", key="save_company"):
            if 'company' not in config:
                config['company'] = {}

            config['company']['name'] = company_name
            config['company']['tagline'] = company_tagline
            config['company']['address'] = company_address
            config['company']['phone'] = company_phone
            config['company']['email'] = company_email
            config['company']['website'] = company_website

            if save_config(config):
                st.success("✅ Company information saved successfully!")
                st.rerun()

    # Tab 2: Colors & Theme
    with tab2:
        st.subheader("Colors & Theme")

        st.markdown("""
        Customize the color scheme of the application. Choose colors that match your brand identity.
        """)

        col1, col2, col3 = st.columns(3)

        with col1:
            primary_color = st.color_picker(
                "Primary Color",
                value=config.get('branding', {}).get('primary_color', '#1E88E5'),
                help="Main brand color (used for headers, buttons)"
            )

        with col2:
            secondary_color = st.color_picker(
                "Secondary Color",
                value=config.get('branding', {}).get('secondary_color', '#FFA726'),
                help="Secondary accent color"
            )

        with col3:
            accent_color = st.color_picker(
                "Accent Color",
                value=config.get('branding', {}).get('accent_color', '#43A047'),
                help="Accent color for highlights"
            )

        st.markdown("---")

        show_powered_by = st.checkbox(
            "Show 'Powered by PV Configurator' footer",
            value=config.get('branding', {}).get('show_powered_by', True),
            help="Display attribution in reports and exports"
        )

        if st.button("💾 Save Theme Settings", key="save_theme"):
            if 'branding' not in config:
                config['branding'] = {}

            config['branding']['primary_color'] = primary_color
            config['branding']['secondary_color'] = secondary_color
            config['branding']['accent_color'] = accent_color
            config['branding']['show_powered_by'] = show_powered_by

            if save_config(config):
                st.success("✅ Theme settings saved successfully!")

                # Update Streamlit theme
                update_streamlit_theme(primary_color, secondary_color)

                st.info("🔄 Some theme changes may require refreshing the page.")

    # Tab 3: Logo & Images
    with tab3:
        st.subheader("Logo & Images")

        st.markdown("""
        Upload your company logo to personalize reports and the application interface.
        Recommended: PNG format with transparent background, minimum 200x200 pixels.
        """)

        # Logo upload
        uploaded_logo = st.file_uploader(
            "Upload Company Logo",
            type=['png', 'jpg', 'jpeg'],
            help="Upload your company logo (PNG, JPG, or JPEG)"
        )

        if uploaded_logo is not None:
            # Display preview
            image = Image.open(uploaded_logo)

            col1, col2 = st.columns([1, 2])

            with col1:
                st.image(image, caption="Logo Preview", use_container_width=True)

            with col2:
                st.write("**Image Details:**")
                st.write(f"- Format: {image.format}")
                st.write(f"- Size: {image.size[0]} x {image.size[1]} pixels")
                st.write(f"- Mode: {image.mode}")

                if st.button("💾 Save Logo", key="save_logo"):
                    # Save logo to assets folder
                    logo_path = os.path.join("assets", "company_logo.png")
                    os.makedirs("assets", exist_ok=True)

                    # Convert to PNG and save
                    if image.mode == 'RGBA':
                        image.save(logo_path, 'PNG')
                    else:
                        # Convert to RGBA if not already
                        image.convert('RGBA').save(logo_path, 'PNG')

                    # Update config
                    if 'branding' not in config:
                        config['branding'] = {}
                    config['branding']['logo_path'] = logo_path

                    if save_config(config):
                        st.success("✅ Logo saved successfully!")
                        st.rerun()

        # Show current logo if exists
        current_logo_path = config.get('branding', {}).get('logo_path')
        if current_logo_path and os.path.exists(current_logo_path):
            st.markdown("---")
            st.subheader("Current Logo")
            col1, col2 = st.columns([1, 2])

            with col1:
                st.image(current_logo_path, caption="Current Logo", use_container_width=True)

            with col2:
                if st.button("🗑️ Remove Logo", key="remove_logo"):
                    config['branding']['logo_path'] = None
                    if save_config(config):
                        st.success("✅ Logo removed successfully!")
                        st.rerun()

    # Tab 4: Technical Defaults
    with tab4:
        st.subheader("Technical Defaults")

        st.markdown("""
        Set default values for technical parameters. These will be pre-populated in the calculators.
        """)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Units & Currency**")

            currency = st.selectbox(
                "Currency",
                options=["INR", "USD", "EUR", "GBP"],
                index=["INR", "USD", "EUR", "GBP"].index(
                    config.get('defaults', {}).get('currency', 'INR')
                )
            )

            currency_symbols = {"INR": "₹", "USD": "$", "EUR": "€", "GBP": "£"}
            currency_symbol = currency_symbols.get(currency, "₹")

            st.markdown("**Default Units:**")
            st.write("- Length: meters (m)")
            st.write("- Temperature: Celsius (°C)")
            st.write("- Power: kilowatts (kW)")
            st.write("- Volume: cubic meters per hour (m³/h)")

        with col2:
            st.markdown("**Default Chamber Dimensions**")

            chamber_length = st.number_input(
                "Length (m)",
                value=config.get('technical', {}).get('default_chamber', {}).get('length', 3.2),
                min_value=1.0,
                max_value=10.0,
                step=0.1
            )

            chamber_width = st.number_input(
                "Width (m)",
                value=config.get('technical', {}).get('default_chamber', {}).get('width', 2.1),
                min_value=1.0,
                max_value=10.0,
                step=0.1
            )

            chamber_height = st.number_input(
                "Height (m)",
                value=config.get('technical', {}).get('default_chamber', {}).get('height', 2.2),
                min_value=1.0,
                max_value=10.0,
                step=0.1
            )

        st.markdown("---")

        st.markdown("**Default PV Module Specifications**")

        col3, col4 = st.columns(2)

        with col3:
            module_length = st.number_input(
                "Module Length (m)",
                value=config.get('technical', {}).get('default_module', {}).get('length', 2.2),
                min_value=0.5,
                max_value=5.0,
                step=0.1
            )

            module_width = st.number_input(
                "Module Width (m)",
                value=config.get('technical', {}).get('default_module', {}).get('width', 1.3),
                min_value=0.5,
                max_value=3.0,
                step=0.1
            )

        with col4:
            module_thickness = st.number_input(
                "Module Thickness (m)",
                value=config.get('technical', {}).get('default_module', {}).get('thickness', 0.04),
                min_value=0.01,
                max_value=0.10,
                step=0.01,
                format="%.3f"
            )

            module_mass = st.number_input(
                "Module Mass (kg)",
                value=config.get('technical', {}).get('default_module', {}).get('mass', 62),
                min_value=10,
                max_value=200,
                step=1
            )

            module_power = st.number_input(
                "Module Max Power (W)",
                value=config.get('technical', {}).get('default_module', {}).get('max_power', 650),
                min_value=100,
                max_value=1000,
                step=10
            )

        if st.button("💾 Save Technical Defaults", key="save_technical"):
            if 'defaults' not in config:
                config['defaults'] = {}
            if 'technical' not in config:
                config['technical'] = {}

            config['defaults']['currency'] = currency
            config['defaults']['currency_symbol'] = currency_symbol

            config['technical']['default_chamber'] = {
                'length': chamber_length,
                'width': chamber_width,
                'height': chamber_height
            }

            config['technical']['default_module'] = {
                'length': module_length,
                'width': module_width,
                'thickness': module_thickness,
                'mass': module_mass,
                'max_power': module_power
            }

            if save_config(config):
                st.success("✅ Technical defaults saved successfully!")

    # Show raw config (for debugging)
    with st.expander("🔧 Advanced: View Raw Configuration"):
        st.json(config)


def update_streamlit_theme(primary_color: str, secondary_color: str):
    """
    Update Streamlit theme configuration

    Args:
        primary_color: Primary color hex code
        secondary_color: Secondary color hex code
    """
    theme_config = f"""
[theme]
primaryColor = "{primary_color}"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "{secondary_color}22"
textColor = "#262730"
font = "sans serif"
"""

    config_dir = ".streamlit"
    config_file = os.path.join(config_dir, "config.toml")

    os.makedirs(config_dir, exist_ok=True)

    # Read existing config
    existing_config = ""
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            existing_config = f.read()

    # Update theme section
    if '[theme]' in existing_config:
        # Replace existing theme
        parts = existing_config.split('[theme]')
        before_theme = parts[0]

        # Find next section
        after_theme = parts[1]
        if '\n[' in after_theme:
            next_section_idx = after_theme.index('\n[')
            after_theme = after_theme[next_section_idx:]
        else:
            after_theme = ""

        new_config = before_theme + theme_config + after_theme
    else:
        # Append theme
        new_config = existing_config + "\n" + theme_config

    # Write updated config
    with open(config_file, 'w') as f:
        f.write(new_config)


def get_company_info() -> dict:
    """Get company information from config"""
    config = load_config()
    return config.get('company', {
        'name': 'PV Testing Solutions',
        'tagline': 'Professional Photovoltaic Test Equipment'
    })


def get_logo_path() -> str:
    """Get company logo path"""
    config = load_config()
    logo_path = config.get('branding', {}).get('logo_path')

    if logo_path and os.path.exists(logo_path):
        return logo_path

    return None


def display_header_with_branding():
    """Display application header with company branding"""
    company_info = get_company_info()
    logo_path = get_logo_path()

    col1, col2 = st.columns([1, 4])

    with col1:
        if logo_path:
            st.image(logo_path, width=150)

    with col2:
        st.title(company_info.get('name', 'PV Testing Solutions'))
        st.markdown(f"*{company_info.get('tagline', 'Professional Photovoltaic Test Equipment')}*")
