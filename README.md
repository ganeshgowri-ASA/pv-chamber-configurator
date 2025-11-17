# PV Test Chamber Configurator

**Professional White-Labeled Configurator for Photovoltaic Test Equipment**

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)
![Streamlit](https://img.shields.io/badge/streamlit-1.29.0-red)

---

## 🎯 Overview

This is a comprehensive web-based configurator for designing, specifying, and quoting Photovoltaic (PV) module test chambers that comply with IEC 61215 and IEC 61730 international standards. The tool is fully white-labeled, allowing test equipment manufacturers, solar companies, and consultants to customize it with their own branding.

### Key Features

✅ **IEC Standards Compliance**
- IEC 61215-2:2021 (Terrestrial PV modules - Design qualification)
- IEC 61730-2:2016 (PV module safety qualification)
- IEC 60068-2-38 (Temperature/humidity cyclic test)
- IEC 60068-2-14 (Change of temperature)

🔬 **Engineering Calculations**
- Thermal load analysis (conduction, radiation, infiltration)
- Refrigeration system sizing (kW and TR)
- Humidity control requirements
- Airflow and uniformity calculations
- UV LED array design and optimization

💰 **Supplier Database**
- Pre-loaded Indian supplier quotes (UV LEDs, chambers, refrigeration, controls, sensors)
- Custom quote upload (Excel/CSV)
- Multi-supplier comparison
- Automated BOM generation

🎨 **White-Label Customization**
- Company logo upload
- Custom color schemes
- Configurable company information
- Branded report generation

📊 **Professional Outputs**
- Interactive dashboards with Plotly charts
- Downloadable technical reports
- Bill of Materials (BOM) export
- Compliance validation reports

---

## 🏗️ Project Structure

```
pv-chamber-configurator/
├── app.py                      # Main Streamlit application entry point
├── requirements.txt            # Python dependencies
├── config.yaml                 # Branding and configuration settings
├── README.md                   # This file
│
├── .streamlit/
│   └── config.toml            # Streamlit theme configuration
│
├── modules/                    # Core calculation engines
│   ├── engineering_core.py    # Thermal, airflow, UV, IEC validation
│   └── supplier_manager.py    # Supplier database and BOM management
│
├── ui/                         # User interface components
│   └── branding_config.py     # White-label configuration UI
│
├── data/                       # Supplier databases (auto-generated)
│   ├── suppliers_builtin.json # Built-in Indian suppliers
│   └── suppliers_custom.json  # User-uploaded custom quotes
│
├── assets/                     # Logos and images
│   └── company_logo.png       # Uploaded company logo
│
└── utils/                      # Helper utilities (future expansion)
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ganeshgowri-ASA/pv-chamber-configurator.git
cd pv-chamber-configurator
```

2. **Create virtual environment**
```bash
python -m venv venv

# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
streamlit run app.py
```

5. **Access the application**
Open your web browser and navigate to:
```
http://localhost:8501
```

---

## 📖 User Guide

### 1. Home Page

The home page provides an overview of features, supported standards, and quick start instructions.

### 2. Chamber Calculator

**Purpose:** Calculate thermal loads, refrigeration requirements, and airflow specifications.

**Inputs:**
- Chamber dimensions (length, width, height)
- Environmental conditions (ambient temp, test temp range)
- PV module specifications (dimensions, mass, power)
- UV irradiance requirements

**Outputs:**
- Chamber heat transfer analysis
- Product heat load
- UV lighting heat load
- Total refrigeration capacity (kW and TR)
- Airflow requirements (m³/h, velocity)
- UV LED array design (number of LEDs, power)
- IEC compliance validation

**Example Use Case:**
```
Chamber: 3.2m × 2.1m × 2.2m
Modules: 2 × 650W (2.2m × 1.3m, 62kg each)
Temperature: -45°C to +105°C
UV: 250 W/m²

Results:
- Total Heat Load: 8.6 kW
- Refrigeration: 10.3 kW (2.9 TR)
- Airflow: 8137 m³/h at 0.78 m/s
- UV LEDs: 147 units, 4.4 kW
- IEC Compliance: ✅ PASS
```

### 3. Supplier Database

**Browse Suppliers:**
- View pre-loaded quotes from Indian suppliers
- Categories: UV LEDs, Chambers, Refrigeration, Controls, Sensors
- Detailed specifications and contact information

**Upload Custom Quotes:**
- Import your own supplier quotes via Excel/CSV
- Required columns: Supplier Name, Category, Product Model, Price, Lead Time, etc.

**Compare Quotes:**
- Side-by-side comparison of all suppliers in a category
- Identify cheapest option and fastest delivery
- Interactive price comparison charts

**Generate BOM:**
- Select preferred supplier for each category
- Automated Bill of Materials generation
- Total project cost calculation
- CSV export for procurement

### 4. Branding Configuration

**Company Information:**
- Company name, tagline, address
- Contact details (phone, email, website)

**Colors & Theme:**
- Primary, secondary, and accent colors
- Color picker for brand matching
- Real-time theme preview

**Logo & Images:**
- Upload company logo (PNG/JPG)
- Automatic sizing and format conversion
- Preview before saving

**Technical Defaults:**
- Set default chamber dimensions
- Configure default PV module specs
- Currency and units preferences

---

## 🔬 Technical Specifications

### Default Chamber Specifications

| Parameter | Value | Notes |
|-----------|-------|-------|
| Internal Dimensions | 3.2m × 2.1m × 2.2m | Fits 2 large PV modules |
| Volume | 14.8 m³ | - |
| Surface Area | 29.2 m² | - |
| Temperature Range | -45°C to +105°C | Extended range |
| Temperature Uniformity | ±2°C | IEC requirement |
| Humidity Range | 40-95% RH | - |
| Humidity Uniformity | ±3% RH | - |
| UV Spectrum | 280-400 nm | UV-A + UV-B |
| UV Irradiance | 25-250 W/m² | Adjustable |
| UV Uniformity | ±10% | - |

### Default PV Module Specifications

| Parameter | Value |
|-----------|-------|
| Dimensions | 2.2m × 1.3m × 0.04m |
| Mass | 62 kg per module |
| Max Power | 650 W per module |
| Quantity | 2 modules |
| Total Mass | 124 kg |
| Total Area | 5.72 m² |

### Calculated Performance (Example)

| Component | Value | Notes |
|-----------|-------|-------|
| Chamber Heat Transfer | 2.4 kW | At -45°C, 35°C ambient |
| Product Heat Load | 3.3 kW | Under 250 W/m² UV |
| UV LED Heat | 2.9 kW | At 30% efficiency |
| **Total Heat Load** | **8.6 kW** | Base load |
| **Refrigeration Capacity** | **10.3 kW** | With 20% safety factor |
| **Tons of Refrigeration** | **2.9 TR** | - |
| Airflow Rate | 8137 m³/h | For ±2°C uniformity |
| Air Velocity | 0.78 m/s | - |
| Air Changes per Hour | 550 ACH | - |
| Fan Power | 0.86 kW | At 250 Pa static pressure |
| UV LEDs Required | 147 units | At 10W electrical each |
| UV Electrical Power | 4.4 kW | - |

---

## 💰 Supplier Database (India)

### UV LED Systems

| Supplier | Model | Price | Lead Time | Notes |
|----------|-------|-------|-----------|-------|
| **OSRAM India** | OSLON UV 3535 | ₹16L | 12 weeks | Premium, German tech |
| **Excelitas Technologies** | UV LED Array 300 | ₹18L | 14 weeks | High power density |
| **Violumas India** | VioLED UV-365 | ₹14L | 10 weeks | Budget-friendly |

### Environmental Chambers

| Supplier | Model | Price | Lead Time | Notes |
|----------|-------|-------|-----------|-------|
| **HIACC Testing** | HIACC-PV-3200 | ₹35L | 16 weeks | Turnkey solution |
| **Envisys Technologies** | ENV-PV-MASTER-3200 | ₹38L | 18 weeks | Premium, extended range |
| **Testronix Instruments** | TRX-PV-3200-ECO | ₹32L | 14 weeks | Value for money |

### Refrigeration Systems

| Supplier | Model | Price | Lead Time | Notes |
|----------|-------|-------|-----------|-------|
| **Bitzer India** | Ecoline+ 4TES-12Y | ₹8L | 8 weeks | Industry standard |
| **Copeland (Emerson)** | Scroll ZF13K4E | ₹7.5L | 6 weeks | Quieter operation |
| **Danfoss India** | Turbocor TT300 | ₹9.5L | 10 weeks | Oil-free, highest efficiency |

### Control Systems

| Supplier | Model | Price | Lead Time |
|----------|-------|-------|-----------|
| **Siemens India** | SIMATIC S7-1500 + WinCC | ₹4.5L | 6 weeks |
| **Schneider Electric** | Modicon M580 + SCADA | ₹4.2L | 5 weeks |

### Sensors & Instrumentation

| Supplier | Model | Price | Lead Time |
|----------|-------|-------|-----------|
| **Vaisala India** | HMP7 Probes (9x) | ₹2.7L | 4 weeks |
| **Rotronic India** | HC2A-S Probes (9x) | ₹2.4L | 3 weeks |

**Total System Cost:** ₹70-85 Lakhs (approx. $85,000-$105,000 USD)

---

## 🧮 Calculation Methodologies

### Thermal Calculations

**Chamber Heat Transfer:**
```
Q_conduction = (k × A × ΔT) / L

Where:
- k = thermal conductivity of insulation (W/m·K)
- A = surface area (m²)
- ΔT = temperature difference (K)
- L = insulation thickness (m)

Q_total = Q_conduction + Q_thermal_bridge + Q_infiltration
```

**Product Heat Load:**
```
Q_product = (A × E × α) - P_electrical

Where:
- A = module area (m²)
- E = irradiance (W/m²)
- α = absorption coefficient
- P_electrical = electrical output (W)
```

### Refrigeration Sizing

```
Q_design = (Q_chamber + Q_product + Q_lighting) × SF

Where:
- SF = safety factor (typically 1.15-1.25)

Tons_refrigeration = Q_design / 3.517 kW
```

### Airflow Calculations

```
Q_airflow = (m_dot × c_p × ΔT)
m_dot = ρ × V_dot

Where:
- m_dot = mass flow rate (kg/s)
- c_p = specific heat of air (J/kg·K)
- ΔT = temperature rise (K)
- ρ = air density (kg/m³)
- V_dot = volumetric flow rate (m³/s)
```

### UV LED Array Design

```
N_leds = (A × E × (1 + U)) / (P_led × η)

Where:
- A = illumination area (m²)
- E = target irradiance (W/m²)
- U = uniformity margin (typically 0.10 for ±10%)
- P_led = LED electrical power (W)
- η = LED wall-plug efficiency
```

---

## 🎨 White-Label Customization

### Configuration File (config.yaml)

All customization settings are stored in `config.yaml`:

```yaml
company:
  name: "Your Company Name"
  tagline: "Your Tagline"
  address: "Complete Address"
  phone: "+XX-XXX-XXX-XXXX"
  email: "info@yourcompany.com"
  website: "https://www.yourcompany.com"

branding:
  primary_color: "#1E88E5"
  secondary_color: "#FFA726"
  accent_color: "#43A047"
  logo_path: "assets/company_logo.png"
  show_powered_by: true

defaults:
  currency: "INR"
  currency_symbol: "₹"
  units:
    length: "m"
    temperature: "°C"
    power: "kW"
```

### Logo Requirements

- **Format:** PNG (recommended) or JPG
- **Minimum Size:** 200 × 200 pixels
- **Recommended:** Transparent background (PNG)
- **Aspect Ratio:** 1:1 to 3:1 (width:height)
- **File Size:** < 2 MB

---

## 🔌 API & Integration (Future)

### Planned Features

- **CFD Integration:** Export geometry for ANSYS Fluent, COMSOL
- **Virtual HMI:** Embedded Siemens/Schneider HMI simulator
- **REST API:** Programmatic access to calculations
- **Database Export:** Export supplier DB to ERP systems
- **3D Visualization:** WebGL-based chamber visualization

---

## 📚 Standards & References

### IEC Standards

1. **IEC 61215-2:2021** - Terrestrial photovoltaic (PV) modules - Design qualification and type approval - Part 2: Test procedures
2. **IEC 61730-2:2016** - Photovoltaic (PV) module safety qualification - Part 2: Requirements for testing
3. **IEC 60068-2-38:2009** - Environmental testing - Part 2-38: Tests - Test Z/AD: Composite temperature/humidity cyclic test
4. **IEC 60068-2-14:2009** - Environmental testing - Part 2-14: Tests - Test N: Change of temperature

### Additional Resources

- [NREL PV Module Qualification](https://www.nrel.gov/)
- [Fraunhofer ISE Testing Guidelines](https://www.ise.fraunhofer.de/)
- [PVEL Module Reliability Testing](https://www.pvel.com/)

---

## 🛠️ Development

### Technology Stack

- **Frontend:** Streamlit 1.29.0
- **Visualization:** Plotly, Matplotlib
- **Data Processing:** Pandas, NumPy
- **Scientific Computing:** SciPy
- **Document Generation:** ReportLab, FPDF2
- **Image Processing:** Pillow
- **Configuration:** PyYAML

### Module Documentation

#### engineering_core.py

**Classes:**
- `ChamberDimensions`: Chamber geometry
- `PVModuleSpec`: PV module specifications
- `TestConditions`: IEC test parameters
- `ThermalCalculations`: Heat transfer calculations
- `HumidityCalculations`: Psychrometric calculations
- `AirflowCalculations`: Airflow and fan sizing
- `UVCalculations`: UV LED array design
- `IECValidation`: Standards compliance checking
- `UnitConverter`: Unit conversion utilities

#### supplier_manager.py

**Classes:**
- `SupplierQuote`: Quote data structure
- `SupplierDatabase`: Database management

**Functions:**
- `parse_uploaded_quote_excel()`: Parse Excel quotes
- `parse_uploaded_quote_csv()`: Parse CSV quotes

#### branding_config.py

**Functions:**
- `load_config()`: Load YAML configuration
- `save_config()`: Save YAML configuration
- `render_branding_config()`: UI for branding settings
- `display_header_with_branding()`: Branded header component

---

## 📝 Changelog

### Version 1.0.0 (2024-01-15)

**Initial Release**
- ✅ Core thermal, airflow, and UV calculations
- ✅ IEC 61215/61730 compliance validation
- ✅ Indian supplier database (50+ quotes)
- ✅ White-label branding system
- ✅ BOM generation and export
- ✅ Interactive Plotly dashboards
- ✅ Multi-page Streamlit app
- ✅ Comprehensive documentation

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👥 Authors

- **Initial Development** - PV Engineering Team

---

## 🙏 Acknowledgments

- IEC Technical Committee 82 for PV standards
- Indian supplier community for quote data
- Streamlit team for the amazing framework
- Open-source scientific Python community

---

## 📞 Support

For support, please contact:
- **Email:** support@pvconfiguratorproject.com
- **Issues:** [GitHub Issues](https://github.com/ganeshgowri-ASA/pv-chamber-configurator/issues)
- **Documentation:** [Wiki](https://github.com/ganeshgowri-ASA/pv-chamber-configurator/wiki)

---

## 🌟 Star History

If you find this project useful, please consider giving it a star on GitHub!

---

**Built with ❤️ for the Solar Industry**
