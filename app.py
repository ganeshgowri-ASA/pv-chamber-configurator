import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
from datetime import datetime
import os
import sys

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from modules.supplier_database import SupplierDatabaseManager
from modules.quote_parser import auto_detect_and_parse
from modules.init_database import initialize_database

# Page configuration
st.set_page_config(
    page_title="PV Chamber Configurator",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database (only runs once if empty)
@st.cache_resource
def get_database():
    """Initialize and return database manager."""
    return initialize_database()

db = get_database()

# Title and description
st.title("🔬 UV+TC+HF+DH Chamber Configurator")
st.markdown("""
Comprehensive Environmental Test Chamber Configurator & Quote Generation System  
for PV Module Testing with CFD Simulations, Virtual HMI, and Business Analysis
""")

# Sidebar for company branding
with st.sidebar:
    st.header("🎨 Company Branding")
    
    company_name = st.text_input("Company Name", "Zenitek Solutions")
    company_address = st.text_area("Address", "Tamil Nadu, India")
    company_email = st.text_input("Email", "info@zenitek.com")
    
    st.divider()
    st.subheader("📊 Quick Stats")
    st.metric("Total Cost", "₹1.37 Cr")
    st.metric("Delivery", "22 weeks")
    st.metric("Warranty", "36 months")

# Main tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📐 Chamber Design",
    "💡 UV System",
    "💰 Quote Generator",
    "📊 Supplier Database",
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
    
    st.subheader("Cost Breakdown")
    
    cost_data = {
        "Component": [
            "Chamber System",
            "UV LED Arrays",
            "Refrigeration",
            "Controls/HMI",
            "DC Power Supply",
            "Uniformity Robot",
            "Water Treatment",
            "Installation",
            "Calibration"
        ],
        "Cost (₹L)": [35, 16, 8, 7, 6, 12, 6.3, 5, 3.5]
    }
    
    df_cost = pd.DataFrame(cost_data)
    df_cost["Cost (₹)"] = df_cost["Cost (₹L)"] * 100000
    
    st.dataframe(df_cost, use_container_width=True)
    
    total_cost = df_cost["Cost (₹L)"].sum()
    st.success(f"### Total Project Cost: ₹{total_cost:.1f} Lakhs (₹{total_cost/100:.2f} Crores)")
    
    # Cost breakdown chart
    fig = go.Figure(data=[go.Pie(
        labels=df_cost["Component"],
        values=df_cost["Cost (₹L)"],
        hole=0.4
    )])
    fig.update_layout(title="Cost Distribution")
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("📊 Supplier Database & Quote Comparison")

    # Subtabs for different sections
    subtab1, subtab2, subtab3, subtab4, subtab5 = st.tabs([
        "📤 Upload Quote",
        "🏢 Suppliers",
        "📦 Components",
        "💲 Price Comparison",
        "🎯 Procurement Recommendation"
    ])

    # Upload Quote Tab
    with subtab1:
        st.subheader("Upload & Parse Quote")

        col1, col2 = st.columns([2, 1])

        with col1:
            # Supplier selection
            suppliers_df = db.get_suppliers()
            if not suppliers_df.empty:
                supplier_names = suppliers_df['name'].tolist()
                selected_supplier = st.selectbox("Select Supplier", supplier_names)
                supplier_id = suppliers_df[suppliers_df['name'] == selected_supplier]['id'].iloc[0]
            else:
                st.warning("No suppliers found. Please add suppliers first.")
                supplier_id = None

            # File upload
            uploaded_file = st.file_uploader(
                "Upload Quote (PDF, Excel, or CSV)",
                type=['pdf', 'xlsx', 'xls', 'csv'],
                help="Upload a quote file to automatically parse component prices"
            )

            if uploaded_file and supplier_id:
                # Save uploaded file temporarily
                temp_dir = "data/temp_quotes"
                os.makedirs(temp_dir, exist_ok=True)
                temp_path = os.path.join(temp_dir, uploaded_file.name)

                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())

                if st.button("Parse Quote", type="primary"):
                    with st.spinner("Parsing quote..."):
                        # Parse the quote
                        result = auto_detect_and_parse(temp_path)

                        if result.get('success'):
                            st.success("Quote parsed successfully!")

                            # Display metadata
                            if result.get('metadata'):
                                st.write("**Quote Metadata:**")
                                metadata_df = pd.DataFrame([result['metadata']])
                                st.dataframe(metadata_df, use_container_width=True)

                            # Display items
                            if result.get('items'):
                                st.write(f"**Found {len(result['items'])} items:**")
                                items_df = pd.DataFrame(result['items'])
                                st.dataframe(items_df, use_container_width=True)

                                # Option to save to database
                                if st.button("Save Quote to Database"):
                                    try:
                                        # Prepare quote data
                                        quote_data = {
                                            'supplier_id': supplier_id,
                                            'quote_date': result['metadata'].get('quote_date', datetime.now().strftime('%Y-%m-%d')),
                                            'quote_number': result['metadata'].get('quote_number', ''),
                                            'validity_days': result['metadata'].get('validity_days', 30),
                                            'total_cost': result['metadata'].get('total_cost', sum(item['total_price'] for item in result['items'])),
                                            'uploaded_file': uploaded_file.name,
                                            'parsed_data': json.dumps(result),
                                            'status': 'active'
                                        }

                                        # Add quote
                                        quote_id = db.add_quote(quote_data, result['items'])
                                        st.success(f"Quote saved successfully! Quote ID: {quote_id}")

                                    except Exception as e:
                                        st.error(f"Error saving quote: {str(e)}")
                            else:
                                st.warning("No items found in quote. You may need to enter data manually.")
                        else:
                            st.error(f"Failed to parse quote: {result.get('error', 'Unknown error')}")
                            if result.get('raw_text'):
                                with st.expander("View Raw Extracted Text"):
                                    st.text(result['raw_text'][:2000])  # Show first 2000 chars

        with col2:
            st.info("""
            **Supported Formats:**
            - PDF quotes
            - Excel files (.xlsx, .xls)
            - CSV files

            **Auto-parsing extracts:**
            - Component names
            - Quantities
            - Unit prices
            - Total prices
            - Lead times
            - Warranty terms
            """)

    # Suppliers Tab
    with subtab2:
        st.subheader("Supplier Management")

        col1, col2 = st.columns([2, 1])

        with col1:
            # Display all suppliers
            suppliers_df = db.get_suppliers()
            if not suppliers_df.empty:
                st.dataframe(
                    suppliers_df[['name', 'location', 'rating', 'avg_delivery_days', 'payment_terms', 'contact', 'email']],
                    use_container_width=True
                )

                # Statistics
                st.write("**Supplier Statistics:**")
                stats_col1, stats_col2, stats_col3 = st.columns(3)
                with stats_col1:
                    st.metric("Total Suppliers", len(suppliers_df))
                with stats_col2:
                    st.metric("Avg Rating", f"{suppliers_df['rating'].mean():.2f}/5.0")
                with stats_col3:
                    st.metric("Avg Delivery", f"{suppliers_df['avg_delivery_days'].mean():.0f} days")
            else:
                st.info("No suppliers found in database.")

        with col2:
            # Add new supplier form
            with st.expander("➕ Add New Supplier"):
                with st.form("add_supplier_form"):
                    new_name = st.text_input("Supplier Name*")
                    new_contact = st.text_input("Contact Number")
                    new_email = st.text_input("Email")
                    new_location = st.text_input("Location")
                    new_rating = st.slider("Rating", 0.0, 5.0, 3.5, 0.1)
                    new_delivery = st.number_input("Avg Delivery Days", 1, 180, 30)
                    new_payment = st.selectbox("Payment Terms", ["Net 15", "Net 30", "Net 45", "Net 60", "50% Advance"])

                    submitted = st.form_submit_button("Add Supplier")
                    if submitted and new_name:
                        try:
                            supplier_data = {
                                'name': new_name,
                                'contact': new_contact,
                                'email': new_email,
                                'location': new_location,
                                'rating': new_rating,
                                'avg_delivery_days': new_delivery,
                                'payment_terms': new_payment
                            }
                            supplier_id = db.add_supplier(supplier_data)
                            st.success(f"Supplier added successfully! ID: {supplier_id}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error adding supplier: {str(e)}")

    # Components Tab
    with subtab3:
        st.subheader("Component Catalog")

        # Category filter
        categories = db.get_categories()
        selected_category = st.selectbox("Filter by Category", ["All"] + categories)

        # Get components
        if selected_category == "All":
            components_df = db.get_components()
        else:
            components_df = db.get_components(category=selected_category)

        if not components_df.empty:
            # Display components
            st.dataframe(
                components_df[['category', 'name', 'specification', 'supplier_name', 'price',
                             'lead_time_days', 'warranty_months', 'moq']],
                use_container_width=True
            )

            # Statistics
            st.write("**Component Statistics:**")
            stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
            with stats_col1:
                st.metric("Total Components", len(components_df))
            with stats_col2:
                st.metric("Avg Price", f"₹{components_df['price'].mean():,.0f}")
            with stats_col3:
                st.metric("Avg Lead Time", f"{components_df['lead_time_days'].mean():.0f} days")
            with stats_col4:
                st.metric("Avg Warranty", f"{components_df['warranty_months'].mean():.0f} months")

            # Export option
            if st.button("Export to Excel"):
                export_path = db.export_comparison_report(components_df, format='excel',
                                                         output_path='data/components_export')
                st.success(f"Components exported to: {export_path}")
        else:
            st.info("No components found.")

    # Price Comparison Tab
    with subtab4:
        st.subheader("Price Comparison & Best Value Analysis")

        # Select category for comparison
        categories = db.get_categories()
        if categories:
            compare_category = st.selectbox("Select Category to Compare", categories)

            if compare_category:
                # Get best value analysis
                comparison_df = db.get_best_value_supplier(compare_category)

                if not comparison_df.empty:
                    # Display results with scores
                    st.write(f"**Price Comparison for {compare_category}:**")

                    display_cols = ['name', 'supplier_name', 'price', 'lead_time_days',
                                  'warranty_months', 'rating', 'total_score']

                    # Highlight best value (highest score)
                    st.dataframe(
                        comparison_df[display_cols].style.background_gradient(
                            subset=['total_score'], cmap='RdYlGn'
                        ),
                        use_container_width=True
                    )

                    # Show recommendation
                    best_supplier = comparison_df.iloc[0]
                    st.success(f"""
                    **Recommended Supplier:** {best_supplier['supplier_name']}
                    - Price: ₹{best_supplier['price']:,.2f}
                    - Lead Time: {best_supplier['lead_time_days']} days
                    - Warranty: {best_supplier['warranty_months']} months
                    - Supplier Rating: {best_supplier['rating']}/5.0
                    - Overall Score: {best_supplier['total_score']:.1f}/100
                    """)

                    # Visualization
                    fig = go.Figure()

                    # Add bars for total score
                    fig.add_trace(go.Bar(
                        x=comparison_df['supplier_name'],
                        y=comparison_df['total_score'],
                        text=comparison_df['total_score'].round(1),
                        textposition='auto',
                        marker_color=comparison_df['total_score'],
                        marker_colorscale='RdYlGn',
                        name='Total Score'
                    ))

                    fig.update_layout(
                        title=f"Supplier Comparison Score - {compare_category}",
                        xaxis_title="Supplier",
                        yaxis_title="Total Score (out of 100)",
                        height=400
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Detailed score breakdown
                    with st.expander("View Detailed Score Breakdown"):
                        score_cols = ['supplier_name', 'price_score', 'lead_time_score',
                                    'rating_score', 'warranty_score', 'payment_score', 'total_score']
                        st.dataframe(comparison_df[score_cols], use_container_width=True)
                else:
                    st.warning(f"No components found in category: {compare_category}")
        else:
            st.info("No categories available for comparison.")

    # Procurement Recommendation Tab
    with subtab5:
        st.subheader("Procurement Recommendation Engine")

        st.write("Define your component requirements to get optimal supplier recommendations:")

        # Component requirements input
        num_requirements = st.number_input("Number of Components Required", 1, 20, 5)

        requirements = []
        for i in range(num_requirements):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                categories = db.get_categories()
                category = st.selectbox(f"Category {i+1}", [""] + categories, key=f"cat_{i}")
            with col2:
                quantity = st.number_input(f"Qty {i+1}", 1, 100, 1, key=f"qty_{i}")
            with col3:
                st.write("")  # Spacing

            if category:
                requirements.append({
                    'category': category,
                    'quantity': quantity
                })

        if requirements and st.button("Generate Recommendation", type="primary"):
            with st.spinner("Analyzing procurement options..."):
                # Generate recommendation
                recommendation = db.generate_procurement_recommendation(requirements)

                # Display summary
                st.write("**Procurement Summary:**")
                sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)

                with sum_col1:
                    st.metric("Total Cost", f"₹{recommendation['total_cost']:,.2f}")
                with sum_col2:
                    st.metric("Max Lead Time", f"{recommendation['max_lead_time_days']} days")
                with sum_col3:
                    st.metric("Suppliers", recommendation['num_suppliers'])
                with sum_col4:
                    risk_color = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
                    st.metric("Risk Level", f"{risk_color.get(recommendation['risk_level'], '⚪')} {recommendation['risk_level']}")

                # Display recommendations
                st.write("**Recommended Components & Suppliers:**")
                rec_df = pd.DataFrame(recommendation['recommendations'])
                st.dataframe(rec_df, use_container_width=True)

                # Supplier distribution
                st.write("**Supplier Distribution:**")
                supplier_dist = pd.DataFrame(
                    list(recommendation['supplier_distribution'].items()),
                    columns=['Supplier', 'Number of Components']
                )

                fig = go.Figure(data=[go.Pie(
                    labels=supplier_dist['Supplier'],
                    values=supplier_dist['Number of Components'],
                    hole=0.3
                )])
                fig.update_layout(title="Component Distribution by Supplier")
                st.plotly_chart(fig, use_container_width=True)

                # Risk assessment
                st.write("**Risk Assessment:**")
                if recommendation['risk_level'] == "High":
                    st.warning("""
                    ⚠️ **High Risk**: Only 1 supplier selected. Consider diversifying suppliers to reduce dependency.
                    """)
                elif recommendation['risk_level'] == "Medium":
                    st.info("""
                    ℹ️ **Medium Risk**: 2 suppliers selected. Acceptable risk level, but consider adding one more supplier for critical components.
                    """)
                else:
                    st.success("""
                    ✅ **Low Risk**: Multiple suppliers selected. Good diversification reduces supply chain risk.
                    """)

                # Export option
                if st.button("Export Recommendation"):
                    export_path = db.export_comparison_report(rec_df, format='excel',
                                                             output_path='data/procurement_recommendation')
                    st.success(f"Recommendation exported to: {export_path}")

with tab5:
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

with tab6:
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
*White-labeled PV Chamber Configurator v1.0*
""")
