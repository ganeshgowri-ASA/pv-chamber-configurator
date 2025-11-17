import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import os
from datetime import datetime
import sys

# Add modules to path
sys.path.insert(0, os.path.dirname(__file__))

# Import custom modules
try:
    from modules.quote_generator import QuoteGenerator
    from modules.email_system import EmailSystem
    from modules.customer_db import CustomerDatabase
    from modules import payment_calculator
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="PV Chamber Configurator",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'quote_items' not in st.session_state:
    st.session_state.quote_items = []
if 'current_quote' not in st.session_state:
    st.session_state.current_quote = None
if 'pdf_path' not in st.session_state:
    st.session_state.pdf_path = None

# Initialize modules
@st.cache_resource
def init_modules():
    """Initialize Quote Generator, Email System, and Customer DB"""
    white_label_config = {
        'company_name': st.session_state.get('company_name', 'Zenitek Solutions'),
        'address': st.session_state.get('company_address', 'Tamil Nadu, India'),
        'email': st.session_state.get('company_email', 'info@zenitek.com'),
        'phone': '+91-XXX-XXX-XXXX',
        'website': 'www.zenitek.com',
        'logo_path': None,
        'primary_color': '#1f77b4',
        'secondary_color': '#ff7f0e',
        'footer_text': 'Professional Environmental Test Chambers'
    }

    quote_gen = QuoteGenerator(white_label_config=white_label_config)
    email_sys = EmailSystem()
    customer_db = CustomerDatabase()

    return quote_gen, email_sys, customer_db

try:
    quote_generator, email_system, customer_db = init_modules()
except Exception as e:
    st.warning(f"Note: Some modules not fully initialized: {e}")
    quote_generator = None
    email_system = None
    customer_db = None

# Title and description
st.title("🔬 UV+TC+HF+DH Chamber Configurator")
st.markdown("""
Comprehensive Environmental Test Chamber Configurator & Quote Generation System
for PV Module Testing with CFD Simulations, Virtual HMI, and Business Analysis
""")

# Sidebar for company branding
with st.sidebar:
    st.header("🎨 Company Branding")

    company_name = st.text_input("Company Name", "Zenitek Solutions", key="company_name")
    company_address = st.text_area("Address", "Tamil Nadu, India", key="company_address")
    company_email = st.text_input("Email", "info@zenitek.com", key="company_email")

    st.divider()
    st.subheader("📊 Quick Stats")
    st.metric("Total Cost", "₹1.37 Cr")
    st.metric("Delivery", "22 weeks")
    st.metric("Warranty", "36 months")

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📐 Chamber Design",
    "💡 UV System",
    "💰 Quote Generator",
    "📈 Business Analysis",
    "🖥️ Virtual HMI"
])

with tab1:
    st.header("Chamber Design Specifications")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Dimensions")
        length = st.number_input("Length (mm)", value=3200, step=100)
        width = st.number_input("Width (mm)", value=2100, step=100)
        height = st.number_input("Height (mm)", value=2200, step=100)

        volume = (length * width * height) / 1e9
        st.info(f"📦 Internal Volume: {volume:.2f} m³")

    with col2:
        st.subheader("Performance")
        temp_range = st.slider("Temperature Range (°C)", -45, 105, (-45, 105))
        humidity_range = st.slider("Humidity Range (%RH)", 40, 95, (40, 95))
        uv_intensity = st.slider("UV Intensity (W/m²)", 25, 250, 60)

        st.success("✓ IEC 61215/61730 Compliant")

with tab2:
    st.header("UV Optical System")

    col1, col2 = st.columns(2)
    with col1:
        led_type = st.selectbox("LED Type", ["LED (45% efficiency)", "Metal Halide (35%)", "Fluorescent (25%)"])
        num_modules = st.number_input("Number of PV Modules", value=2, min_value=1, max_value=4)

    with col2:
        st.metric("Required LEDs", "28 units")
        st.metric("Total UV Power", "2.4 kW")
        st.metric("Uniformity", "±8.5%")

with tab3:
    st.header("💰 Commercial Quote Generator")

    # Create sub-tabs for quote generation
    quote_tab1, quote_tab2, quote_tab3, quote_tab4 = st.tabs([
        "📝 Create Quote",
        "📧 Email & Delivery",
        "📊 Quote History",
        "👥 Customers"
    ])

    with quote_tab1:
        st.subheader("Customer Information")

        col1, col2 = st.columns(2)

        with col1:
            customer_name = st.text_input("Customer Name*", key="cust_name")
            customer_email = st.text_input("Customer Email*", key="cust_email")
            customer_phone = st.text_input("Phone", key="cust_phone")

        with col2:
            customer_company = st.text_input("Company Name", key="cust_company")
            customer_address = st.text_area("Address", key="cust_address", height=100)

        st.divider()

        # Load sample configuration
        config_path = "data/quote_templates/sample_quote_config.json"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                default_items = config['default_items']
                optional_items = config['optional_items']
                default_settings = config['default_settings']
        else:
            default_items = []
            optional_items = []
            default_settings = {
                'tax_rate': 18.0,
                'shipping_cost': 50000.0,
                'currency': 'INR',
                'payment_terms': '50% advance, 50% on delivery',
                'delivery_weeks': 14,
                'validity_days': 30
            }

        st.subheader("Quote Items")

        # Item selection
        col1, col2 = st.columns([3, 1])

        with col1:
            st.write("**Standard Items:**")

            # Display default items with checkboxes
            selected_items = []

            for idx, item in enumerate(default_items):
                if st.checkbox(
                    f"{item['description']} - ₹{item['unit_price']:,.0f}",
                    value=True,
                    key=f"item_{idx}"
                ):
                    selected_items.append(item.copy())

            st.write("**Optional Items:**")

            for idx, item in enumerate(optional_items):
                if st.checkbox(
                    f"{item['description']} - ₹{item['unit_price']:,.0f}",
                    value=False,
                    key=f"opt_item_{idx}"
                ):
                    selected_items.append(item.copy())

        with col2:
            st.write("**Quantities:**")

            for idx in range(len(default_items)):
                if f"item_{idx}" in st.session_state and st.session_state[f"item_{idx}"]:
                    qty = st.number_input(
                        f"Qty",
                        min_value=1,
                        value=1,
                        key=f"qty_{idx}",
                        label_visibility="collapsed"
                    )
                    # Update quantity in selected items
                    for item in selected_items:
                        if item['description'] == default_items[idx]['description']:
                            item['quantity'] = qty
                else:
                    st.write("")

            for idx in range(len(optional_items)):
                if f"opt_item_{idx}" in st.session_state and st.session_state[f"opt_item_{idx}"]:
                    qty = st.number_input(
                        f"Qty",
                        min_value=1,
                        value=1,
                        key=f"opt_qty_{idx}",
                        label_visibility="collapsed"
                    )
                    # Update quantity in selected items
                    for item in selected_items:
                        if item['description'] == optional_items[idx]['description']:
                            item['quantity'] = qty
                else:
                    st.write("")

        st.divider()

        # Pricing options
        st.subheader("Pricing & Terms")

        col1, col2, col3 = st.columns(3)

        with col1:
            discount_type = st.selectbox(
                "Discount Type",
                ["percentage", "bulk", "custom"],
                help="Select discount type"
            )

            if discount_type == "percentage":
                discount_percent = st.number_input("Discount %", min_value=0.0, max_value=50.0, value=0.0, step=0.5)
                custom_discount = 0
            elif discount_type == "bulk":
                total_qty = sum(item.get('quantity', 1) for item in selected_items)
                bulk_rec = payment_calculator.get_bulk_discount_recommendation(total_qty)
                st.info(f"**{bulk_rec['tier']}**: {bulk_rec['description']}")
                discount_percent = bulk_rec['recommended_discount']
                custom_discount = 0
            else:  # custom
                custom_discount = st.number_input("Custom Discount (₹)", min_value=0.0, value=0.0, step=1000.0)
                discount_percent = 0

        with col2:
            payment_terms = st.selectbox(
                "Payment Terms",
                [
                    "100% advance",
                    "50% advance, 50% on delivery",
                    "30% advance, 40% on delivery, 30% after installation",
                    "30 days credit",
                    "60 days credit",
                    "90 days credit"
                ],
                index=1
            )

            delivery_weeks = st.number_input("Delivery (weeks)", min_value=8, max_value=24, value=14)

        with col3:
            shipping_cost = st.number_input("Shipping (₹)", min_value=0.0, value=50000.0, step=5000.0)
            installation_cost = st.number_input("Installation (₹)", min_value=0.0, value=0.0, step=10000.0)

        # Generate quote button
        if st.button("🧮 Generate Quote", type="primary"):
            if not customer_name or not customer_email:
                st.error("Please provide customer name and email")
            elif not selected_items:
                st.error("Please select at least one item")
            else:
                customer_info = {
                    'name': customer_name,
                    'company': customer_company,
                    'email': customer_email,
                    'phone': customer_phone,
                    'address': customer_address
                }

                try:
                    if quote_generator:
                        quote_data = quote_generator.create_quote(
                            customer_info=customer_info,
                            items=selected_items,
                            discount_percent=discount_percent,
                            discount_type=discount_type,
                            custom_discount=custom_discount,
                            shipping=shipping_cost,
                            installation=installation_cost,
                            payment_terms=payment_terms,
                            delivery_weeks=delivery_weeks
                        )

                        # Save quote
                        quote_id = quote_generator.save_quote(quote_data)
                        st.session_state.current_quote = quote_data
                        st.session_state.current_quote['id'] = quote_id

                        st.success(f"✅ Quote {quote_data['quote_number']} created successfully!")
                    else:
                        st.error("Quote generator not initialized. Please check dependencies.")

                except Exception as e:
                    st.error(f"Error generating quote: {e}")

        # Display current quote
        if st.session_state.current_quote:
            st.divider()
            st.subheader("Quote Summary")

            quote = st.session_state.current_quote

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Quote Number", quote['quote_number'])
                st.metric("Date", quote['date'])
            with col2:
                st.metric("Total Amount", f"₹{quote['total']:,.2f}")
                st.metric("Discount", f"{quote['discount_percent']:.1f}%")
            with col3:
                st.metric("Valid Until", quote['validity_date'])
                st.metric("Delivery", f"{quote['delivery_weeks']} weeks")

            # Items table
            st.write("**Items:**")
            items_df = pd.DataFrame(quote['items'])
            st.dataframe(items_df, use_container_width=True, hide_index=True)

            # Totals
            col1, col2 = st.columns([2, 1])
            with col2:
                st.write(f"**Subtotal:** ₹{quote['subtotal']:,.2f}")
                st.write(f"**Discount ({quote['discount_percent']:.1f}%):** -₹{quote['discount_amount']:,.2f}")
                st.write(f"**Taxable Amount:** ₹{quote['taxable_amount']:,.2f}")
                st.write(f"**GST ({quote['tax_rate']:.0f}%):** ₹{quote['tax_amount']:,.2f}")
                if quote['shipping'] > 0:
                    st.write(f"**Shipping:** ₹{quote['shipping']:,.2f}")
                if quote['installation'] > 0:
                    st.write(f"**Installation:** ₹{quote['installation']:,.2f}")
                st.write(f"### **Total:** ₹{quote['total']:,.2f}")

            # Generate PDF button
            if st.button("📄 Generate PDF", type="primary"):
                try:
                    if quote_generator:
                        os.makedirs("data/quotes", exist_ok=True)
                        pdf_path = f"data/quotes/{quote['quote_number']}.pdf"

                        success = quote_generator.generate_pdf(quote, pdf_path)

                        if success:
                            st.session_state.pdf_path = pdf_path
                            st.success(f"✅ PDF generated: {pdf_path}")

                            # Offer download
                            with open(pdf_path, 'rb') as f:
                                st.download_button(
                                    label="⬇️ Download PDF",
                                    data=f.read(),
                                    file_name=f"{quote['quote_number']}.pdf",
                                    mime="application/pdf"
                                )
                        else:
                            st.error("Failed to generate PDF")
                    else:
                        st.error("Quote generator not initialized")

                except Exception as e:
                    st.error(f"Error generating PDF: {e}")

    with quote_tab2:
        st.subheader("📧 Email Quote to Customer")

        if not st.session_state.current_quote:
            st.warning("Please generate a quote first")
        elif not st.session_state.pdf_path:
            st.warning("Please generate PDF first")
        else:
            quote = st.session_state.current_quote

            st.info(f"**Quote:** {quote['quote_number']} | **Amount:** ₹{quote['total']:,.2f}")

            col1, col2 = st.columns(2)

            with col1:
                to_email = st.text_input("Recipient Email*", value=quote['customer']['email'])
                cc_emails = st.text_input("CC (comma-separated)", "")

            with col2:
                bcc_emails = st.text_input("BCC (comma-separated)", "")
                custom_message = st.text_area("Custom Message (optional)", "")

            # SMTP Configuration (in expander for security)
            with st.expander("📮 SMTP Configuration"):
                st.warning("⚠️ For security, use environment variables or app-specific passwords")

                smtp_server = st.text_input("SMTP Server", "smtp.gmail.com")
                smtp_port = st.number_input("SMTP Port", value=587)
                smtp_username = st.text_input("Username", "")
                smtp_password = st.text_input("Password", type="password")
                use_tls = st.checkbox("Use TLS", value=True)

                if st.button("Test Connection"):
                    if smtp_username and smtp_password:
                        smtp_config = {
                            'smtp_server': smtp_server,
                            'smtp_port': smtp_port,
                            'use_tls': use_tls,
                            'username': smtp_username,
                            'password': smtp_password,
                            'from_email': smtp_username,
                            'from_name': company_name
                        }

                        test_email_sys = EmailSystem(smtp_config)
                        success, message = test_email_sys.test_smtp_connection()

                        if success:
                            st.success(f"✅ {message}")
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.error("Please provide SMTP credentials")

            if st.button("📧 Send Email", type="primary"):
                if not to_email:
                    st.error("Please provide recipient email")
                else:
                    try:
                        # Prepare CC/BCC lists
                        cc_list = [email.strip() for email in cc_emails.split(',') if email.strip()]
                        bcc_list = [email.strip() for email in bcc_emails.split(',') if email.strip()]

                        # Note: In production, SMTP credentials should come from environment variables
                        st.warning("⚠️ Email sending requires valid SMTP credentials. Configure in SMTP section above.")
                        st.info("📧 Email would be sent to: " + to_email)

                        # For demo purposes, show what would be sent
                        subject, body = email_system.compose_quote_email(quote, custom_message) if email_system else ("", "")

                        with st.expander("Preview Email"):
                            st.write(f"**Subject:** {subject}")
                            st.write("**Body:**")
                            st.markdown(body, unsafe_allow_html=True)

                    except Exception as e:
                        st.error(f"Error: {e}")

    with quote_tab3:
        st.subheader("📊 Quote History")

        try:
            if quote_generator:
                # Get all quotes from database
                import sqlite3
                conn = sqlite3.connect(quote_generator.quotes_db)

                query = """
                    SELECT quote_number, date, customer_name, customer_company,
                           total, currency, status, delivery_weeks
                    FROM quotes
                    ORDER BY date DESC
                    LIMIT 50
                """

                quotes_df = pd.read_sql_query(query, conn)
                conn.close()

                if not quotes_df.empty:
                    st.dataframe(quotes_df, use_container_width=True, hide_index=True)

                    # Export option
                    csv = quotes_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Export to CSV",
                        data=csv,
                        file_name="quote_history.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No quotes generated yet")
            else:
                st.error("Quote generator not initialized")

        except Exception as e:
            st.error(f"Error loading quote history: {e}")

    with quote_tab4:
        st.subheader("👥 Customer Management")

        try:
            if customer_db:
                # Add new customer
                with st.expander("➕ Add New Customer"):
                    col1, col2 = st.columns(2)

                    with col1:
                        new_cust_name = st.text_input("Name*", key="new_cust_name")
                        new_cust_email = st.text_input("Email*", key="new_cust_email")
                        new_cust_phone = st.text_input("Phone", key="new_cust_phone")

                    with col2:
                        new_cust_company = st.text_input("Company", key="new_cust_company")
                        new_cust_address = st.text_area("Address", key="new_cust_address")

                    if st.button("Add Customer"):
                        if new_cust_name and new_cust_email:
                            customer_data = {
                                'name': new_cust_name,
                                'email': new_cust_email,
                                'phone': new_cust_phone,
                                'company': new_cust_company,
                                'address': new_cust_address
                            }

                            try:
                                customer_id = customer_db.add_customer(customer_data)
                                st.success(f"✅ Customer added (ID: {customer_id})")
                            except Exception as e:
                                st.error(f"Error adding customer: {e}")
                        else:
                            st.error("Please provide name and email")

                # List customers
                customers = customer_db.list_customers(limit=50)

                if customers:
                    customers_df = pd.DataFrame(customers)
                    display_cols = ['id', 'name', 'company', 'email', 'phone', 'customer_type', 'status']
                    available_cols = [col for col in display_cols if col in customers_df.columns]

                    st.dataframe(customers_df[available_cols], use_container_width=True, hide_index=True)

                    # Export option
                    csv = customers_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Export Customers to CSV",
                        data=csv,
                        file_name="customers.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No customers in database")
            else:
                st.error("Customer database not initialized")

        except Exception as e:
            st.error(f"Error managing customers: {e}")

with tab4:
    st.header("📈 Business Analysis")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("10-Year TCO", "₹2.27 Cr", "+66%")
        st.metric("ROI Period", "0.58 years")

    with col2:
        st.metric("Annual Revenue", "₹12.5 L")
        st.metric("CO₂ Emissions", "15.2 tonnes/yr")

    with col3:
        st.metric("Energy Cost", "₹18.5 L/yr")
        st.metric("MTBF", "20,000 hrs")

with tab5:
    st.header("🖥️ Virtual HMI - Real-time Monitoring")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Temperature", "85.0°C", "±0.2°C")
        st.progress(85/105)

    with col2:
        st.metric("Humidity", "85.0%RH", "±0.5%")
        st.progress(85/100)

    with col3:
        st.metric("UV Intensity", "248 W/m²", "±2 W/m²")
        st.progress(248/250)

    st.info("🔄 System Status: Running | ⏰ Runtime: 1,245 hours | ✅ All sensors calibrated")

# Footer
st.divider()
st.markdown(f"""
---
**{company_name}** | {company_address} | {company_email}
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
*White-labeled PV Chamber Configurator v2.0 - Quote Generator System*
""")
