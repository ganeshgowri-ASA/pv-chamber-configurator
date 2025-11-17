import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
from datetime import datetime
from pathlib import Path

# Import Phase 9 modules
from modules import IntegrationLayer, WhiteLabelManager, I18nManager, ConfigManager

# Page configuration
st.set_page_config(
    page_title="PV Chamber Configurator",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.integration_layer = IntegrationLayer(st.session_state)
    st.session_state.white_label_manager = WhiteLabelManager()
    st.session_state.i18n_manager = I18nManager()
    st.session_state.config_manager = ConfigManager()

    # Set default values
    st.session_state.current_locale = 'en_US'
    st.session_state.branding_applied = False

# Shorthand for translation
def t(key, **kwargs):
    """Translate text using i18n manager"""
    return st.session_state.i18n_manager.translate(key, **kwargs)

# Apply custom CSS for branding
def apply_custom_css():
    """Apply custom CSS based on white-label settings"""
    wl_manager = st.session_state.white_label_manager
    css_vars = wl_manager.get_css_variables()

    custom_css = f"""
    <style>
    {css_vars}

    .stButton > button {{
        background-color: var(--primary-color);
        color: white;
    }}

    .stButton > button:hover {{
        background-color: var(--secondary-color);
    }}

    h1, h2, h3 {{
        font-family: var(--font-family);
    }}

    .metric-card {{
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid var(--primary-color);
    }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

apply_custom_css()

# Display logo if available
logo_base64 = st.session_state.white_label_manager.get_logo_base64()
if logo_base64:
    st.markdown(
        f'<img src="{logo_base64}" style="max-width: 300px; max-height: 100px; margin-bottom: 20px;">',
        unsafe_allow_html=True
    )

# Title and description
company_name = st.session_state.white_label_manager.config['company']['name']
st.title(f"🔬 {t('app_title')}")
st.markdown(f"""
{t('app_subtitle')}
{t('app_description')}
""")

# Sidebar
with st.sidebar:
    st.header(t('sidebar.title'))

    # Language selector
    st.subheader(t('sidebar.language'))
    available_locales = st.session_state.i18n_manager.get_available_locales()

    locale_options = {loc['code']: loc['name'] for loc in available_locales}
    selected_locale = st.selectbox(
        t('sidebar.language'),
        options=list(locale_options.keys()),
        format_func=lambda x: locale_options[x],
        index=list(locale_options.keys()).index(st.session_state.current_locale),
        label_visibility="collapsed"
    )

    if selected_locale != st.session_state.current_locale:
        st.session_state.i18n_manager.set_locale(selected_locale)
        st.session_state.current_locale = selected_locale
        st.rerun()

    st.divider()

    # Company branding info
    st.header("🎨 " + t('headings.company_branding'))

    company_info = st.session_state.white_label_manager.config['company']
    st.text_input(t('labels.company_name'), company_info['name'], key='sidebar_company_name', disabled=True)
    st.text_area(t('labels.address'), company_info['address'], key='sidebar_address', disabled=True, height=80)
    st.text_input(t('labels.email'), company_info['email'], key='sidebar_email', disabled=True)

    st.divider()

    # Quick stats
    st.subheader("📊 " + t('sidebar.quick_stats'))
    st.metric(t('sidebar.total_cost'), "₹1.37 Cr")
    st.metric(t('sidebar.delivery'), "22 weeks")
    st.metric(t('sidebar.warranty'), "36 months")

    st.divider()

    # Configuration management
    st.subheader("⚙️ " + t('sidebar.config_management'))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 " + t('buttons.save'), use_container_width=True):
            st.session_state.show_save_modal = True

    with col2:
        if st.button("📂 " + t('buttons.load'), use_container_width=True):
            st.session_state.show_load_modal = True

# Main tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📐 " + t('tabs.chamber_design'),
    "💡 " + t('tabs.uv_system'),
    "💰 " + t('tabs.quote_generator'),
    "📈 " + t('tabs.business_analysis'),
    "🖥️ " + t('tabs.virtual_hmi'),
    "🎨 " + t('tabs.white_label')
])

with tab1:
    st.header(t('headings.chamber_design'))

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(t('labels.dimensions'))

        length = st.number_input(
            t('labels.length'),
            value=st.session_state.get('chamber_length', 3200),
            step=100,
            help=t('tooltips.chamber_volume'),
            key='chamber_length'
        )

        width = st.number_input(
            t('labels.width'),
            value=st.session_state.get('chamber_width', 2100),
            step=100,
            key='chamber_width'
        )

        height = st.number_input(
            t('labels.height'),
            value=st.session_state.get('chamber_height', 2200),
            step=100,
            key='chamber_height'
        )

        volume = (length * width * height) / 1e9
        st.info(f"📦 {t('labels.internal_volume')}: {volume:.2f} {t('units.m3')}")

        # Store in integration layer
        st.session_state.integration_layer.set_module_data('phase1_core', {
            'length': length,
            'width': width,
            'height': height,
            'volume': volume
        })

    with col2:
        st.subheader(t('labels.performance'))

        temp_range = st.slider(
            t('labels.temperature_range'),
            -45, 105, (-45, 105),
            help=t('tooltips.temp_uniformity'),
            key='temp_range'
        )

        humidity_range = st.slider(
            t('labels.humidity_range'),
            40, 95, (40, 95),
            help=t('tooltips.humidity_uniformity'),
            key='humidity_range'
        )

        uv_intensity = st.slider(
            t('labels.uv_intensity'),
            25, 250, 60,
            help=t('tooltips.uv_intensity_info'),
            key='uv_intensity'
        )

        st.success("✓ " + t('messages.info.iec_compliant'))

with tab2:
    st.header(t('headings.uv_optical_system'))

    col1, col2 = st.columns(2)
    with col1:
        led_type = st.selectbox(
            t('labels.led_type'),
            ["LED (45% efficiency)", "Metal Halide (35%)", "Fluorescent (25%)"],
            help=t('tooltips.led_efficiency'),
            key='led_type'
        )

        num_modules = st.number_input(
            t('labels.num_modules'),
            value=2, min_value=1, max_value=4,
            key='num_modules'
        )

        # Store UV system data
        st.session_state.integration_layer.set_module_data('phase2_uv', {
            'led_type': led_type,
            'num_modules': num_modules,
            'uv_intensity': uv_intensity
        })

    with col2:
        st.metric(t('labels.required_leds'), "28 " + t('units.units'))
        st.metric(t('labels.total_uv_power'), "2.4 " + t('units.kw'))
        st.metric(t('labels.uniformity'), "±8.5" + t('units.percent'))

with tab3:
    st.header("💰 " + t('headings.commercial_quote'))

    st.subheader(t('headings.cost_breakdown'))

    cost_data = {
        "Component": [
            t('cost_components.chamber_system'),
            t('cost_components.uv_led_arrays'),
            t('cost_components.refrigeration'),
            t('cost_components.controls_hmi'),
            t('cost_components.dc_power_supply'),
            t('cost_components.uniformity_robot'),
            t('cost_components.water_treatment'),
            t('cost_components.installation'),
            t('cost_components.calibration')
        ],
        f"{t('labels.company_name')} ({t('units.lakhs')})": [35, 16, 8, 7, 6, 12, 6.3, 5, 3.5]
    }

    df_cost = pd.DataFrame(cost_data)
    df_cost[f"Cost ({t('units.lakhs')})"] = df_cost[f"{t('labels.company_name')} ({t('units.lakhs')})"] * 100000

    st.dataframe(df_cost[[cost_data["Component"][0].__class__.__name__.replace("'", ""), f"{t('labels.company_name')} ({t('units.lakhs')})"]].rename(columns={
        cost_data["Component"][0].__class__.__name__.replace("'", ""): "Component"
    }), use_container_width=True)

    # Recreate dataframe with correct column names
    df_cost_clean = pd.DataFrame({
        "Component": cost_data["Component"],
        "Cost (₹L)": cost_data[f"{t('labels.company_name')} ({t('units.lakhs')})"]
    })

    total_cost = df_cost_clean["Cost (₹L)"].sum()
    st.success(f"### Total Project Cost: ₹{total_cost:.1f} Lakhs (₹{total_cost/100:.2f} Crores)")

    # Cost breakdown chart
    fig = go.Figure(data=[go.Pie(
        labels=df_cost_clean["Component"],
        values=df_cost_clean["Cost (₹L)"],
        hole=0.4
    )])
    fig.update_layout(title=t('headings.cost_breakdown'))
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("📈 " + t('headings.business_metrics'))

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(t('metrics.ten_year_tco'), "₹2.27 Cr", "+66%")
        st.metric(t('metrics.roi_period'), "0.58 " + t('units.years'))

    with col2:
        st.metric(t('metrics.annual_revenue'), "₹12.5 L")
        st.metric(t('metrics.co2_emissions'), "15.2 " + t('units.tonnes_yr'))

    with col3:
        st.metric(t('metrics.energy_cost'), "₹18.5 L/yr")
        st.metric(t('metrics.mtbf'), "20,000 " + t('units.hours'))

with tab5:
    st.header("🖥️ " + t('headings.virtual_hmi_monitoring'))

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(t('metrics.temperature'), "85.0" + t('units.celsius'), "±0.2" + t('units.celsius'))
        st.progress(85/105)

    with col2:
        st.metric(t('metrics.humidity'), "85.0" + t('units.rh'), "±0.5" + t('units.rh'))
        st.progress(85/100)

    with col3:
        st.metric(t('labels.uv_intensity'), "248 " + t('units.w_m2'), "±2 " + t('units.w_m2'))
        st.progress(248/250)

    st.info(f"🔄 {t('messages.info.system_running')} | ⏰ {t('metrics.runtime')}: 1,245 {t('units.hours')} | ✅ {t('messages.info.calibrated')}")

with tab6:
    st.header("🎨 " + t('headings.white_label_config'))

    # Company Information
    st.subheader(t('headings.company_branding'))

    col1, col2 = st.columns(2)

    with col1:
        company_name_input = st.text_input(
            t('labels.company_name'),
            st.session_state.white_label_manager.config['company']['name'],
            placeholder=t('placeholders.company_name')
        )

        company_address = st.text_area(
            t('labels.address'),
            st.session_state.white_label_manager.config['company']['address'],
            placeholder=t('placeholders.address')
        )

        company_email = st.text_input(
            t('labels.email'),
            st.session_state.white_label_manager.config['company']['email'],
            placeholder=t('placeholders.email')
        )

    with col2:
        company_phone = st.text_input(
            t('labels.phone'),
            st.session_state.white_label_manager.config['company']['phone'],
            placeholder=t('placeholders.phone')
        )

        company_website = st.text_input(
            t('labels.website'),
            st.session_state.white_label_manager.config['company']['website'],
            placeholder=t('placeholders.website')
        )

    # Update company info button
    if st.button(t('buttons.update') + " Company Info", type="primary"):
        company_data = {
            'name': company_name_input,
            'address': company_address,
            'email': company_email,
            'phone': company_phone,
            'website': company_website
        }

        if st.session_state.white_label_manager.set_company_info(company_data):
            st.success(t('messages.success.settings_updated'))
            st.rerun()
        else:
            st.error(t('messages.error.validation_failed'))

    st.divider()

    # Logo Upload
    st.subheader(t('headings.logo_upload'))

    uploaded_file = st.file_uploader(
        t('labels.logo'),
        type=['png', 'jpg', 'jpeg', 'svg'],
        help=t('tooltips.logo_requirements')
    )

    if uploaded_file is not None:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.image(uploaded_file, caption=t('buttons.preview'), width=300)

        with col2:
            if st.button(t('buttons.upload') + " Logo", type="primary"):
                success, message = st.session_state.white_label_manager.upload_logo(uploaded_file)

                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    # Display current logo
    current_logo = st.session_state.white_label_manager.get_logo_path()
    if current_logo:
        st.info(f"Current logo: {Path(current_logo).name}")

    st.divider()

    # Brand Colors
    st.subheader(t('headings.brand_colors'))

    col1, col2 = st.columns(2)

    with col1:
        primary_color = st.color_picker(
            t('labels.primary_color'),
            st.session_state.white_label_manager.config['branding']['primary_color'],
            help=t('tooltips.primary_color_info')
        )

    with col2:
        secondary_color = st.color_picker(
            t('labels.secondary_color'),
            st.session_state.white_label_manager.config['branding']['secondary_color'],
            help=t('tooltips.secondary_color_info')
        )

    # Font family selector
    font_family = st.selectbox(
        t('labels.font_family'),
        st.session_state.white_label_manager.FONT_FAMILIES,
        index=st.session_state.white_label_manager.FONT_FAMILIES.index(
            st.session_state.white_label_manager.config['branding']['font_family']
        )
    )

    # Apply branding button
    if st.button(t('buttons.apply') + " Branding", type="primary"):
        if st.session_state.white_label_manager.set_brand_colors(primary_color, secondary_color):
            st.session_state.white_label_manager.set_font_family(font_family)
            st.success(t('messages.success.branding_applied'))
            st.rerun()
        else:
            st.error(t('messages.error.validation_failed'))

    # Reset button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button(t('buttons.reset') + " to Default", type="secondary"):
            if st.session_state.white_label_manager.reset_to_default():
                st.success(t('messages.success.settings_updated'))
                st.rerun()

# Configuration Save Modal
if st.session_state.get('show_save_modal', False):
    with st.expander("💾 " + t('headings.save_configuration'), expanded=True):
        config_name = st.text_input(
            t('labels.configuration_name'),
            placeholder=t('placeholders.config_name')
        )

        config_description = st.text_area(
            t('labels.description'),
            placeholder=t('placeholders.description')
        )

        # Collect all configuration data
        config_data = {
            'chamber_specs': st.session_state.integration_layer.get_module_data('phase1_core'),
            'uv_system': st.session_state.integration_layer.get_module_data('phase2_uv'),
            'white_label': st.session_state.white_label_manager.config,
            'user_preferences': {
                'language': st.session_state.current_locale
            }
        }

        col1, col2 = st.columns(2)

        with col1:
            if st.button(t('buttons.save') + " Configuration", type="primary"):
                if config_name:
                    output_path = f"config/saved_configs/{config_name}.json"

                    if st.session_state.config_manager.save_configuration(config_data, output_path):
                        st.success(t('messages.success.config_saved'))
                        st.session_state.show_save_modal = False
                    else:
                        st.error(t('messages.error.config_save_failed'))
                else:
                    st.warning(t('validation.required_field'))

        with col2:
            if st.button(t('buttons.cancel')):
                st.session_state.show_save_modal = False
                st.rerun()

# Configuration Load Modal
if st.session_state.get('show_load_modal', False):
    with st.expander("📂 " + t('headings.load_configuration'), expanded=True):
        uploaded_config = st.file_uploader(
            t('buttons.load') + " Configuration File",
            type=['json'],
            help=t('tooltips.config_save_info')
        )

        # Also show templates
        st.subheader(t('headings.configuration_templates'))
        templates = st.session_state.config_manager.get_config_templates()

        if templates:
            template_names = [t['name'] for t in templates]
            selected_template = st.selectbox(
                t('labels.template_name'),
                [''] + template_names
            )

            if selected_template:
                template_data = st.session_state.config_manager.load_template(selected_template)

                if template_data:
                    st.json(template_data.get('description', ''))

                    if st.button(t('buttons.load') + " Template", type="primary"):
                        if st.session_state.config_manager.apply_configuration(template_data, st.session_state):
                            st.success(t('messages.success.config_loaded'))
                            st.session_state.show_load_modal = False
                            st.rerun()
                        else:
                            st.error(t('messages.error.config_load_failed'))
        else:
            st.info(t('messages.info.no_templates'))

        col1, col2 = st.columns(2)

        with col1:
            if uploaded_config and st.button(t('buttons.load') + " from File", type="primary"):
                # Save uploaded file temporarily
                temp_path = "config/temp_upload.json"
                Path("config").mkdir(exist_ok=True)

                with open(temp_path, 'wb') as f:
                    f.write(uploaded_config.getbuffer())

                config_data = st.session_state.config_manager.load_configuration(temp_path)

                if config_data:
                    if st.session_state.config_manager.apply_configuration(config_data, st.session_state):
                        st.success(t('messages.success.config_loaded'))
                        st.session_state.show_load_modal = False
                        st.rerun()
                    else:
                        st.error(t('messages.error.config_load_failed'))
                else:
                    st.error(t('messages.error.invalid_file'))

        with col2:
            if st.button(t('buttons.cancel')):
                st.session_state.show_load_modal = False
                st.rerun()

# Footer
st.divider()
company_info = st.session_state.white_label_manager.config['company']
st.markdown(f"""
---
**{company_info['name']}** | {company_info['address']} | {company_info['email']}
{t('footer.generated_on')}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
*{t('footer.version')}*
""")
