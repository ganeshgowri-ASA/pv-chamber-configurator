# 🔬 PV Chamber Configurator v1.0.0

**Comprehensive Environmental Test Chamber Design & Quote Generation System**
*For UV+TC+HF+DH PV Module Testing with CFD Simulations, Virtual HMI & Business Analysis*

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28.0+-red.svg)](https://streamlit.io)
[![IEC 61215](https://img.shields.io/badge/IEC-61215%2F61730-green.svg)](https://webstore.iec.ch/)
[![ISO 17025](https://img.shields.io/badge/ISO-17025-green.svg)](https://www.iso.org/)

---

## 🎯 Overview

The **PV Chamber Configurator** is a comprehensive web-based system for designing, quoting, and analyzing environmental test chambers for photovoltaic (PV) module testing. It integrates 10 specialized modules covering engineering calculations, simulations, business analysis, compliance, and quote generation.

### ✨ Key Capabilities

- ⚙️ **Physics-Based Design**: Complete thermodynamic and optical calculations
- 🌀 **CFD Simulation**: 3D temperature, airflow, and humidity analysis
- 💰 **Quote Generation**: Professional PDF quotes with white-label branding
- 📊 **Business Analysis**: ROI, TCO, NPV analysis with Monte Carlo simulation
- 🤖 **Virtual HMI**: Real-time chamber monitoring and robot control
- 📜 **Compliance**: IEC 61215/61730 + ISO 17025 calibration management
- 🌍 **Multi-language**: English + Hindi with full i18n support
- 📄 **Report Generator**: 5 professional report templates (PDF/Excel)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/pv-chamber-configurator.git
cd pv-chamber-configurator

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📦 All 10 Integrated Phases

### Phase 1: PV Chamber Core Calculations ✅
- Chamber dimension configuration (1000-10000mm)
- Temperature range: -70°C to +180°C, Humidity: 10-98% RH
- Heat load calculations (cooling/heating)
- Power consumption estimation
- Component cost modeling

### Phase 2: UV Optical System ✅
- UV LED layout optimization (uniformity ±5%)
- 3D irradiance heat map visualization
- Spectral analysis (UV-A/UV-B)
- LED aging prediction

### Phase 3: CFD Simulation Engine ✅
- 3D temperature/airflow/humidity simulation
- Hot/cold spot detection, dead zone identification
- Pressure drop calculation
- Transient response analysis

### Phase 4: Supplier Database & Quotes ✅
- 24 Indian suppliers pre-loaded
- Automated quote parsing (PDF/Excel/CSV)
- Component price tracking and comparison

### Phase 5: Virtual HMI & Robot Control ✅
- Real-time sensor monitoring
- Alarm management system
- Robot controller for UV measurements
- G-Code path generation

### Phase 6: Quote Generator System ✅
- Professional PDF generation with branding
- Email delivery system (SMTP)
- Customer database (CRM)
- Payment terms calculator, bulk discounts

### Phase 7: Business Analysis Enhanced ✅
- 10-year TCO calculation
- NPV, IRR, payback period
- Sensitivity analysis (tornado charts)
- Monte Carlo simulation (1000 iterations)

### Phase 8: Report Generator ✅
- 5 professional report templates
- Technical specifications, commercial proposals
- Business analysis reports, compliance certificates
- PDF/Excel multi-format export

### Phase 9: Integration, White-label & i18n ✅
- Complete branding customization
- Multi-language support (English + Hindi, 225+ strings)
- IEC configuration templates
- Custom CSS injection

### Phase 10: Compliance & Calibration ✅
- IEC 61215/61730 compliance checking
- ISO 17025 calibration management
- Uncertainty calculation (GUM method)
- Certificate generation with NIST/NPL traceability

---

## 💻 Usage

### Basic Workflow

1. **Configure Chamber**: Set dimensions, temperature, humidity, UV intensity
2. **Run CFD Simulation**: Analyze thermal performance
3. **Review Business Analysis**: Evaluate ROI and TCO
4. **Generate Quote**: Create professional quote
5. **Export Reports**: Generate technical/commercial reports
6. **Track Compliance**: Verify IEC/ISO compliance

---

## 📊 Technical Specifications

| Parameter | Min | Max | IEC Spec |
|-----------|-----|-----|----------|
| Temperature | -70°C | +180°C | ±2°C |
| Humidity | 10% RH | 98% RH | ±3% |
| UV Intensity | 25 W/m² | 250 W/m² | ±5% |
| Chamber Volume | 1 m³ | 100 m³ | - |
| PV Modules | 1 | 4 | - |

### Dependencies

```
streamlit>=1.28.0
pandas>=2.1.0
plotly>=5.17.0
numpy>=1.24.0
scipy>=1.11.0
matplotlib>=3.7.0
openpyxl>=3.1.0
PyPDF2>=3.0.0
pdfplumber>=0.10.0
sqlalchemy>=2.0.0
reportlab>=4.0.0
Pillow>=10.0.0
xlsxwriter>=3.1.0
```

---

## 🛠️ Configuration

### White-label Branding

Edit `config/white_label_config.json`:

```json
{
  "company": {
    "name": "Your Company Name",
    "address": "Your Address",
    "email": "info@yourcompany.com"
  },
  "branding": {
    "logo_path": "assets/logo.png",
    "primary_color": "#1f77b4"
  }
}
```

### Email Configuration

Configure SMTP in Streamlit UI or environment variables.

---

## 📖 Documentation

- **[CHANGELOG.md](CHANGELOG.md)**: Version history
- **[DOCUMENTATION.md](DOCUMENTATION.md)**: Technical architecture
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Development guidelines
- **[IEC_COMPLIANCE_GUIDE.md](docs/IEC_COMPLIANCE_GUIDE.md)**: IEC compliance
- **[ISO17025_CALIBRATION_MANUAL.md](docs/ISO17025_CALIBRATION_MANUAL.md)**: Calibration procedures

---

## 🧪 Testing

```bash
# Install pytest
pip install pytest

# Run all tests
pytest tests/
```

---

## 🔒 Compliance & Standards

- ✅ **IEC 61215-2:2021** - PV Module Design Qualification
- ✅ **IEC 61730-2:2016** - PV Module Safety Qualification
- ✅ **ISO/IEC 17025:2017** - Testing & Calibration Laboratories
- ✅ **GUM (JCGM 100:2008)** - Measurement Uncertainty

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

---

## 📝 License

**Proprietary Software** - All rights reserved by Zenitek Solutions.

---

## 👥 Contact

**Zenitek Solutions**
- Location: Tamil Nadu, India
- Email: info@zenitek.com
- Website: www.zenitek.com

---

**Version**: 1.0.0 | **Release**: 2025-11-17 | *Built with ❤️ using Streamlit*
