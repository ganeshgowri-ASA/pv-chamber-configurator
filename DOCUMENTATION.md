# PV Chamber Configurator - Technical Documentation

## Architecture Overview

The PV Chamber Configurator follows a modular architecture with 10 integrated feature phases. Each phase provides specialized functionality accessible through a unified Streamlit interface.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Streamlit Web Interface (app.py)           │
├─────────────────────────────────────────────────────────┤
│                 Integration Layer (Phase 9)             │
├──────────┬──────────┬──────────┬──────────┬────────────┤
│ Phase 1  │ Phase 2  │ Phase 3  │ Phase 4  │  Phase 5   │
│   Core   │    UV    │   CFD    │ Supplier │ Virtual    │
│  Calcs   │ Optical  │   Sim    │ Database │    HMI     │
├──────────┼──────────┼──────────┼──────────┼────────────┤
│ Phase 6  │ Phase 7  │ Phase 8  │ Phase 9  │  Phase 10  │
│  Quote   │ Business │  Report  │ White-   │ Compliance │
│  Gen     │ Analysis │   Gen    │  label   │& Calib     │
└──────────┴──────────┴──────────┴──────────┴────────────┘
         ↓           ↓            ↓           ↓
    ┌────────┐  ┌────────┐  ┌─────────┐  ┌────────┐
    │ SQLite │  │  JSON  │  │   PDF   │  │  Excel │
    │   DB   │  │ Config │  │ Reports │  │ Reports│
    └────────┘  └────────┘  └─────────┘  └────────┘
```

## Module Reference

### Phase 1: Core Calculations (`modules/core_calculations.py`)

**Classes:**
- `ChamberDimensions(length, width, height)` - Chamber physical dimensions
- `PerformanceSpec(temp_min, temp_max, humidity_range, uv_intensity)` - Performance specifications
- `ComponentCosts()` - Cost modeling for all chamber components
- `ChamberVolumeCalculator` - Volume and thermal mass calculations
- `HeatLoadCalculator` - Heating and cooling load analysis
- `AirflowCalculator` - Air circulation requirements
- `PowerConsumptionCalculator` - Electrical power demand

**Key Methods:**
```python
# Example usage
dims = ChamberDimensions(length=3200, width=2100, height=2200)
volume = ChamberVolumeCalculator.calculate_internal_volume(dims)

heat_load = HeatLoadCalculator.calculate_total_cooling_load(
    dims, max_temp=105, num_modules=2
)

power = PowerConsumptionCalculator.calculate_total_power_consumption(
    cooling_kw=15, heating_kw=10
)
```

### Phase 2: UV Optical System (`modules/uv_optical_system.py`)

**Classes:**
- `LEDSpecification` - LED technical specifications
- `UVLEDLayoutCalculator` - Optimal LED placement
- `UniformityGridMapper` - 3D uniformity analysis
- `SpectrumAnalyzer` - UV spectrum analysis
- `LEDAgingModel` - Long-term degradation prediction

### Phase 3: CFD Simulation (`modules/cfd_simulation.py`)

**Classes:**
- `CFDSimulator(chamber_dims, temp_range, humidity_range, grid_resolution)`

**Methods:**
- `calculate_temperature_field()` - 3D temperature distribution
- `calculate_velocity_field()` - Airflow analysis
- `calculate_humidity_field()` - Moisture distribution
- `validate_temperature_uniformity()` - IEC compliance check
- `detect_dead_zones()` - Airflow problem areas

### Phase 6: Quote Generator (`modules/quote_generator.py`)

**Classes:**
- `QuoteGenerator(white_label_config)` - Main quote generation engine

**Methods:**
```python
quote_generator = QuoteGenerator(white_label_config)

quote_data = quote_generator.create_quote(
    customer_info={'name': 'ABC Corp', 'email': 'abc@example.com'},
    items=[...],
    discount_percent=10
)

quote_generator.generate_pdf(quote_data, output_path='quote.pdf')
```

### Phase 7: Business Analysis (`modules/business_analysis_enhanced.py`)

**Classes:**
- `BusinessAnalysisEnhanced(chamber_config, operating_costs, revenue_params)`

**Key Methods:**
```python
analysis = BusinessAnalysisEnhanced(...)

# Calculate TCO
tco_df = analysis.calculate_tco_detailed(years=10)

# ROI metrics
roi = analysis.calculate_roi_metrics(years=10)
# Returns: {'npv': float, 'irr': float, 'payback_period': float}

# Scenario analysis
scenarios = analysis.scenario_analysis()

# Monte Carlo simulation
mc_results = analysis.monte_carlo_simulation(iterations=1000)
```

### Phase 10: Compliance (`modules/iec_compliance.py`, `modules/iso17025_calibration.py`)

**IEC Compliance:**
```python
from modules.iec_compliance import IECComplianceChecker

checker = IECComplianceChecker()
result = checker.validate_test_sequence(['TC200', 'HF10', 'DH1000'])
compliance = checker.check_chamber_compliance(chamber_specs)
```

**ISO 17025 Calibration:**
```python
from modules.iso17025_calibration import ISO17025CalibrationManager

cal_mgr = ISO17025CalibrationManager()
schedule = cal_mgr.generate_calibration_schedule(equipment_list)
certificate = cal_mgr.generate_calibration_certificate(calibration_data)
```

## Database Schema

### SQLite Tables

**suppliers:**
```sql
CREATE TABLE suppliers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT,
    contact_person TEXT,
    email TEXT,
    phone TEXT,
    rating REAL,
    delivery_time_days INTEGER,
    payment_terms TEXT
);
```

**quotes:**
```sql
CREATE TABLE quotes (
    id INTEGER PRIMARY KEY,
    quote_number TEXT UNIQUE,
    customer_name TEXT,
    customer_email TEXT,
    total REAL,
    date TEXT,
    status TEXT
);
```

## API Integration

The `IntegrationLayer` class (Phase 9) provides unified access to all modules:

```python
# Access through session state
integration = st.session_state.integration_layer

# Get chamber configuration
config = integration.get_chamber_config()

# Run full analysis
results = integration.run_full_analysis(chamber_config)

# Generate comprehensive report
report = integration.generate_comprehensive_report()
```

## Configuration Files

### White-label Config (`config/white_label_config.json`)

```json
{
  "company": {
    "name": "Company Name",
    "address": "Address",
    "email": "email@company.com",
    "phone": "+91-XXX-XXX-XXXX",
    "website": "www.company.com"
  },
  "branding": {
    "logo_path": "assets/logo.png",
    "watermark_path": "assets/watermark.png",
    "primary_color": "#1f77b4",
    "secondary_color": "#ff7f0e",
    "font_family": "Arial"
  }
}
```

### i18n Locale Files (`locales/*.json`)

```json
{
  "app_title": "PV Chamber Configurator",
  "labels": {
    "temperature": "Temperature",
    "humidity": "Humidity"
  },
  "units": {
    "celsius": "°C",
    "rh": "%RH"
  }
}
```

## Performance Considerations

- **CFD Grid Resolution**: Higher resolution = more accurate but slower (70×70×70 max recommended)
- **Monte Carlo Iterations**: 1000 iterations typical, use 5000+ for critical decisions
- **Database Queries**: Use indexes on frequently queried columns
- **Report Generation**: PDF generation can take 5-10 seconds for complex reports

## Deployment

### Streamlit Cloud

```toml
# .streamlit/config.toml
[server]
maxUploadSize = 200

[theme]
primaryColor = "#1f77b4"
```

### Environment Variables

```bash
# Required for email functionality
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## Testing

Run comprehensive test suite:

```bash
# All tests
pytest tests/

# Specific module
pytest tests/test_core_calculations.py

# With coverage
pytest --cov=modules --cov-report=html tests/
```

## Error Handling

All modules implement try-except blocks for graceful error handling. Check Streamlit UI for error messages and consult logs.

## Version Control

- **Semantic Versioning**: MAJOR.MINOR.PATCH (currently 1.0.0)
- **Git Tags**: Use `git tag v1.0.0` for releases
- **Branch Strategy**: Feature branches merged to main

---

For additional help, see:
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [README.md](README.md) - Getting started guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
