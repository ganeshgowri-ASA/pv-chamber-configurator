# ISO/IEC 17025:2017 Calibration Manual
## PV Chamber Configurator - Measurement Uncertainty and Calibration Management

**Version:** 1.0.0
**Last Updated:** November 2025
**Applicable Standard:** ISO/IEC 17025:2017

---

## Table of Contents

1. [Introduction](#introduction)
2. [ISO/IEC 17025 Overview](#iso-17025-overview)
3. [Calibration Certificate Generation](#calibration-certificates)
4. [Measurement Uncertainty Budgets](#measurement-uncertainty)
5. [CMC Tables](#cmc-tables)
6. [Traceability Management](#traceability)
7. [Calibration Procedures](#procedures)
8. [Using the Calibration Module](#using-the-module)
9. [Appendices](#appendices)

---

## Introduction

This manual provides comprehensive guidance on calibration and measurement uncertainty analysis compliant with ISO/IEC 17025:2017 requirements. The PV Chamber Configurator includes tools for:

- Generating calibration certificates
- Calculating measurement uncertainty budgets
- Managing traceability chains
- Tracking calibration history
- Validating CMC compliance

### Scope of Calibration

The system supports calibration of:
- RTD temperature sensors
- Thermocouples (Type K, J, T)
- Humidity sensors (capacitive, resistive)
- UV radiometers (280-400nm)
- Pressure sensors
- Airflow sensors

---

## ISO/IEC 17025 Overview

### Key Requirements

ISO/IEC 17025:2017 specifies general requirements for the competence of testing and calibration laboratories.

#### Section 6: Resource Requirements

**6.4 Equipment**
- All equipment shall be capable of achieving required measurement accuracy
- Equipment shall be calibrated before use
- Calibration program shall be established and reviewed

**6.5 Metrological Traceability**
- Measurements shall be traceable to SI units through national/international standards
- Where traceability to SI units is not possible, laboratory shall demonstrate traceability

**6.6 Externally Provided Products and Services**
- Reference standards shall be calibrated by competent bodies
- Calibration certificates shall include measurement uncertainty

#### Section 7: Process Requirements

**7.2 Selection, Verification and Validation of Methods**
- Calibration methods shall be validated
- Measurement uncertainty shall be estimated

**7.6 Evaluation of Measurement Uncertainty**
- Laboratory shall identify sources of uncertainty
- Type A and Type B evaluations shall be performed
- Combined and expanded uncertainty shall be calculated

**7.8 Reporting Results**
- Calibration certificates shall include:
  - Measurement results
  - Measurement uncertainty (with coverage factor and confidence level)
  - Traceability statement
  - Calibration date and next calibration due date

---

## Calibration Certificates

### Certificate Structure

Per ISO/IEC 17025, calibration certificates must contain:

#### 1. Header Information
- Certificate number (unique identifier)
- Laboratory name and address
- Accreditation body and certificate number
- Scope of accreditation
- Issue date

#### 2. Instrument Information
- Instrument type/description
- Manufacturer and model
- Serial number
- Identification/asset number
- Owner/customer
- Location

#### 3. Calibration Information
- Calibration date
- Next calibration due date
- Calibration procedure reference
- Environmental conditions during calibration

#### 4. Reference Standard Information
- Standard description
- Make, model, serial number
- Calibration certificate number
- Calibration date and next calibration date
- Measurement uncertainty
- Traceability (e.g., NIST, NPL)

#### 5. Calibration Results
- Table with:
  - Reference values
  - Instrument readings (typically 3 per point)
  - Mean of readings
  - Error (deviation from reference)
  - Measurement uncertainty (k=2)

#### 6. Environmental Conditions
- Temperature during calibration
- Humidity during calibration
- Pressure during calibration
- Uncertainties for environmental parameters

#### 7. Uncertainty Statement
Example:
> "The reported expanded uncertainty of measurement is stated as the standard uncertainty of measurement multiplied by the coverage factor k=2, which for a normal distribution corresponds to a coverage probability of approximately 95%."

#### 8. Signatures
- Calibrated by (technician name)
- Reviewed by (technical reviewer)
- Approved by (quality manager/lab director)
- Dates

#### 9. Footer
- Statement: "This certificate may not be reproduced except in full"
- Reference to ISO/IEC 17025:2017
- Page numbering

### Certificate Example

```
================================================================================
                        PV Testing Laboratory
            Tamil Nadu, India | +91-XXX-XXX-XXXX | lab@pvtesting.com
        Accredited by NABL | Certificate No: TC-1234 | Scope: Temperature,
                    Humidity, UV Irradiance Calibration

                        CALIBRATION CERTIFICATE
                            CAL-20241117-INST-001
================================================================================

INSTRUMENT INFORMATION
Instrument Type:        RTD Temperature Sensor
Manufacturer:           Omega Engineering
Model:                  RTD-100-PT
Serial Number:          SN-12345
ID Number:              TEMP-001
Owner:                  ABC Company
Location:               PV Test Chamber #1

CALIBRATION INFORMATION
Calibration Date:       2024-11-17
Next Calibration Due:   2025-11-17
Procedure Reference:    CAL-TEMP-001 Rev 3

REFERENCE STANDARD
Standard:               Reference Platinum Resistance Thermometer
Make/Model:             Fluke 5608
Serial Number:          3021234
Certificate Number:     NIST-2024-T-45678
Calibration Date:       2024-06-15
Next Calibration:       2025-06-15
Uncertainty (k=2):      ±0.025°C
Traceability:           NIST

ENVIRONMENTAL CONDITIONS
Temperature:            23.0 ± 0.5°C
Humidity:               50 ± 5% RH
Pressure:               101.3 ± 0.5 kPa

CALIBRATION RESULTS - Temperature
================================================================================
Reference (°C)  Reading 1  Reading 2  Reading 3   Mean     Error   Uncertainty
                   (°C)       (°C)       (°C)     (°C)     (°C)    (k=2) (°C)
--------------------------------------------------------------------------------
  -40.00         -40.05     -40.03     -40.04    -40.04   -0.04      ±0.15
    0.00           0.02       0.01       0.02      0.02    0.02      ±0.15
   25.00          25.08      25.06      25.05     25.06    0.06      ±0.15
   60.00          60.12      60.10      60.08     60.10    0.10      ±0.15
   85.00          85.15      85.12      85.10     85.12    0.12      ±0.15
================================================================================

MEASUREMENT UNCERTAINTY
The reported expanded uncertainty of measurement is stated as the standard
uncertainty of measurement multiplied by the coverage factor k=2, which for a
normal distribution corresponds to a coverage probability of approximately 95%.

The uncertainty budget includes contributions from: reference standard,
resolution, repeatability, and drift.

Calibrated By: __________________    Date: _______
               John Technician

Reviewed By:   __________________    Date: _______
               Jane Supervisor

Approved By:   __________________    Date: _______
               Dr. Lab Director

================================================================================
This certificate is issued in accordance with ISO/IEC 17025:2017.
This certificate may not be reproduced except in full without written approval.
                                                                Page 1 of 1
================================================================================
```

---

## Measurement Uncertainty

### GUM Framework

Measurement uncertainty is calculated per JCGM 100:2008 (GUM - Guide to the Expression of Uncertainty in Measurement).

### Type A Evaluation (Statistical)

Type A uncertainty is evaluated by statistical analysis of repeated observations.

**Standard Uncertainty (Type A):**
```
u_A = s / √n

where:
s = standard deviation of measurements
n = number of measurements
```

**Degrees of Freedom:**
```
ν = n - 1
```

### Type B Evaluation (Non-Statistical)

Type B uncertainty is evaluated by means other than statistical analysis, such as:
- Manufacturer specifications
- Calibration certificates
- Experience/engineering judgment

**Common Distributions:**

1. **Normal Distribution** (calibration certificate uncertainties)
   ```
   u_B = U / k

   where:
   U = expanded uncertainty from certificate
   k = coverage factor (typically 2)
   ```

2. **Rectangular Distribution** (resolution, tolerances)
   ```
   u_B = a / √3

   where:
   a = half-width of distribution
   ```

3. **Triangular Distribution** (manufacturer tolerances)
   ```
   u_B = a / √6
   ```

### Combined Standard Uncertainty

The combined standard uncertainty is calculated by root-sum-of-squares:

```
u_c = √[Σ(c_i × u_i)²]

where:
c_i = sensitivity coefficient
u_i = standard uncertainty of source i
```

### Expanded Uncertainty

```
U = k × u_c

where:
k = coverage factor (typically 2 for ~95% confidence)
```

### Effective Degrees of Freedom

Calculated using Welch-Satterthwaite formula:

```
ν_eff = u_c⁴ / Σ(u_i⁴ / ν_i)

where:
u_c = combined standard uncertainty
u_i = standard uncertainty of component i
ν_i = degrees of freedom for component i
```

---

## Example Uncertainty Budget

### Temperature Sensor Calibration at 85°C

| Source | Value | Type | Distribution | Divisor | u(x_i) | c_i | u_i |
|--------|-------|------|--------------|---------|--------|-----|-----|
| Reference Std | 0.05°C | B | Normal | 2.0 | 0.0250 | 1.0 | 0.0250 |
| Resolution | 0.1°C | B | Rectangular | 1.732 | 0.0289 | 1.0 | 0.0289 |
| Repeatability | 0.08°C | A | Normal | 3.162* | 0.0253 | 1.0 | 0.0253 |
| Drift | 0.03°C | B | Rectangular | 1.732 | 0.0173 | 1.0 | 0.0173 |

*Divisor = √10 (for 10 readings)

**Combined Standard Uncertainty:**
```
u_c = √(0.0250² + 0.0289² + 0.0253² + 0.0173²)
    = √0.002574
    = 0.0507°C
```

**Effective Degrees of Freedom:**
```
ν_eff = 0.0507⁴ / (0.0250⁴/∞ + 0.0289⁴/∞ + 0.0253⁴/9 + 0.0173⁴/∞)
      ≈ 45
```

**Expanded Uncertainty (k=2):**
```
U = 2 × 0.0507 = 0.10°C
```

**Result:**
```
85.12 ± 0.10°C (k=2, ~95% confidence)
```

---

## CMC Tables

### Calibration and Measurement Capability

CMC represents the smallest measurement uncertainty that a laboratory can achieve within its scope of accreditation.

### Temperature CMC Table

| Parameter | Range | CMC (k=2) | Conditions |
|-----------|-------|-----------|------------|
| Temperature | -50°C to +150°C | ±0.15°C | RTD, Thermocouple |
| Temperature | -100°C to -50°C | ±0.30°C | Thermocouple only |
| Temperature | +150°C to +600°C | ±0.50°C | Thermocouple only |

### Humidity CMC Table

| Parameter | Range | CMC (k=2) | Conditions |
|-----------|-------|-----------|------------|
| Relative Humidity | 10% to 95% RH | ±2.0% RH | At 23±5°C |
| Relative Humidity | 5% to 10% RH | ±3.0% RH | At 23±5°C |

### UV Irradiance CMC Table

| Parameter | Range | CMC (k=2) | Conditions |
|-----------|-------|-----------|------------|
| UV Irradiance | 10 to 250 W/m² | ±5.0% | 280-400nm |

### Pressure CMC Table

| Parameter | Range | CMC (k=2) | Conditions |
|-----------|-------|-----------|------------|
| Absolute Pressure | 0 to 200 kPa | ±0.5 kPa | Electronic gauge |

### Air Velocity CMC Table

| Parameter | Range | CMC (k=2) | Conditions |
|-----------|-------|-----------|------------|
| Air Velocity | 0.1 to 10 m/s | ±0.1 m/s | Hot wire anemometer |

---

## Traceability Management

### Traceability Chain

Example for Temperature Calibration:

```
NIST ITS-90 Realization (Primary Standard)
    ↓ (calibrates)
Fluke 5608 Reference RTD (Transfer Standard)
    ↓ Uncertainty: ±0.025°C (k=2)
    ↓ Cert: NIST-2024-T-45678
    ↓ (calibrates)
Chamber RTD Sensors (Working Standards)
    ↓ Uncertainty: ±0.15°C (k=2)
    ↓ (measures)
Test Specimen Temperature
```

### National Metrology Institutes (NMIs)

- **NIST** (USA): National Institute of Standards and Technology
- **NPL** (UK): National Physical Laboratory
- **PTB** (Germany): Physikalisch-Technische Bundesanstalt
- **NMIJ** (Japan): National Metrology Institute of Japan
- **NPLI** (India): National Physical Laboratory of India

### Calibration Intervals

Recommended calibration intervals:

| Instrument Type | Interval | Rationale |
|----------------|----------|-----------|
| Reference RTD | 12 months | High accuracy requirement |
| Working RTD | 12 months | IEC 61215 data quality |
| Humidity Sensors | 12 months | Drift characteristics |
| UV Radiometers | 6-12 months | LED aging effects |
| Pressure Gauges | 24 months | Stable technology |

Intervals may be adjusted based on:
- Drift history
- Usage frequency
- Critical applications
- Manufacturer recommendations

---

## Calibration Procedures

### Procedure CAL-TEMP-001: RTD and Thermocouple Calibration

**Scope:** Calibration of RTD and thermocouple temperature sensors

**Method:** Comparison calibration in temperature bath

**Equipment:**
- Reference RTD (Fluke 5608 or equivalent)
- Temperature bath (Hart Scientific 7040 or equivalent)
- Digital multimeter for resistance/voltage measurement
- Stirrer for bath uniformity

**Calibration Points:**
- RTD: -40°C, 0°C, 25°C, 60°C, 85°C, 120°C
- Thermocouple: -40°C, 0°C, 25°C, 85°C, 150°C, 250°C

**Procedure:**
1. Immerse reference RTD and UUC in temperature bath
2. Set bath to calibration temperature
3. Wait for stabilization (±0.05°C for 10 minutes)
4. Record environmental conditions
5. Take 3 readings from UUC, 30 seconds apart
6. Record reference temperature
7. Calculate mean, error, uncertainty
8. Repeat for each calibration point

**Uncertainty Budget:**
- Reference standard: From calibration certificate
- Resolution: From measurement instrument
- Repeatability: Calculate from 3 readings
- Drift: Estimate based on calibration history
- Bath uniformity: From bath specification

**Acceptance Criteria:**
- Measurement uncertainty ≤ CMC
- Error within specification

---

### Procedure CAL-HUM-001: Humidity Sensor Calibration

**Scope:** Calibration of humidity sensors

**Method:** Comparison against reference hygrometer in humidity chamber

**Equipment:**
- Reference chilled mirror hygrometer (MBW DP3 or equivalent)
- Humidity chamber (Thunder Scientific 2500 or equivalent)
- Temperature measurement equipment

**Calibration Points:**
- 10%, 30%, 50%, 75%, 85%, 95% RH

**Procedure:**
1. Install reference hygrometer and UUC in chamber
2. Set chamber to 25°C
3. Set chamber to calibration humidity point
4. Wait for stabilization (±1% RH for 30 minutes)
5. Take 3 readings from UUC
6. Record reference humidity
7. Calculate results
8. Repeat for each point

**Uncertainty Budget:**
- Reference standard
- Resolution
- Repeatability
- Temperature effect
- Chamber uniformity

---

### Procedure CAL-UV-001: UV Radiometer Calibration

**Scope:** Calibration of UV radiometers (280-400nm)

**Method:** Comparison against reference radiometer under stable UV source

**Equipment:**
- Reference UV radiometer (Kipp & Zonen or equivalent)
- Stable UV source (LED array or lamp)
- Spectroradiometer for wavelength verification

**Calibration Points:**
- 25, 60, 100, 150, 200, 250 W/m²

**Procedure:**
1. Warm up UV source for 30 minutes
2. Position reference radiometer at measurement plane
3. Adjust UV intensity to calibration point
4. Allow 5 minutes stabilization
5. Take 5 readings from UUC
6. Record reference value
7. Calculate results
8. Verify spectral response with spectroradiometer

**Uncertainty Budget:**
- Reference radiometer
- Resolution
- Repeatability
- Spatial uniformity
- Spectral mismatch
- Cosine response

---

## Using the Calibration Module

### Generating a Calibration Certificate

1. **Navigate to "Compliance & Calibration" tab**
2. **Select "ISO 17025 Calibration" sub-tab**
3. **Enter Laboratory Information:**
   - Laboratory name
   - Accreditation body (NABL/A2LA/etc.)
   - Certificate number
   - Contact information

4. **Enter Instrument Information:**
   - Instrument type (RTD, Thermocouple, Humidity, UV)
   - Make, model, serial number
   - Owner/customer
   - Location

5. **Enter Calibration Data:**
   - Select number of calibration points
   - Enter reference values and readings

6. **Click "Generate Example Certificate"**

7. **Review Certificate:**
   - Verify all information is correct
   - Check calibration results table
   - Review uncertainty values

8. **Download Certificate:**
   - HTML format for printing
   - PDF format (if ReportLab installed)

### Calculating Uncertainty Budget

1. **Navigate to "Uncertainty Calculator" sub-tab**
2. **Select Parameter Type:**
   - Temperature Sensor
   - Humidity Sensor
   - UV Intensity Measurement

3. **Enter Measured Value:**
   - The actual measured/calibrated value

4. **Enter Uncertainty Sources:**
   - Reference standard uncertainty
   - Instrument resolution
   - Repeatability (standard deviation)
   - Drift (if applicable)
   - Number of readings

5. **Click "Calculate Uncertainty Budget"**

6. **Review Results:**
   - Combined standard uncertainty (u_c)
   - Expanded uncertainty (U)
   - Coverage factor (k)
   - Detailed uncertainty budget table

7. **Save/Export:**
   - Copy text output for documentation
   - Include in calibration reports

---

## Appendices

### Appendix A: Uncertainty Terminology

| Term | Symbol | Definition |
|------|--------|------------|
| Standard Uncertainty | u | Uncertainty expressed as standard deviation |
| Type A Uncertainty | u_A | Evaluated by statistical methods |
| Type B Uncertainty | u_B | Evaluated by non-statistical methods |
| Combined Standard Uncertainty | u_c | Combined effect of all uncertainty sources |
| Expanded Uncertainty | U | u_c multiplied by coverage factor |
| Coverage Factor | k | Multiplier (typically 2 for 95% confidence) |
| Degrees of Freedom | ν | Statistical parameter for t-distribution |

### Appendix B: Common Distributions

```
Normal (Gaussian):
    u = U / k    (k typically = 2)
    Example: Calibration certificate uncertainties

Rectangular (Uniform):
    u = a / √3
    Example: Resolution, tolerances without stated distribution

Triangular:
    u = a / √6
    Example: Manufacturer tolerances with "most likely" center value

U-shaped:
    u = a / √2
    Example: Uncertainties varying from edge to center
```

### Appendix C: Sensitivity Coefficients

For most direct measurements:
```
c_i = 1.0
```

For measurements with functional relationships:
```
c_i = ∂f/∂x_i

Example: Resistance to temperature conversion
R = R_0(1 + αT)
∂R/∂T = R_0 × α
```

### Appendix D: CMC Statement Examples

**Temperature:**
> "The laboratory's CMC for RTD temperature sensor calibration is ±0.15°C (k=2) in the range -50°C to +150°C."

**Humidity:**
> "The laboratory's CMC for humidity sensor calibration is ±2.0% RH (k=2) in the range 10% to 95% RH at 23±5°C."

**UV Irradiance:**
> "The laboratory's CMC for UV radiometer calibration is ±5% (k=2) in the range 10 to 250 W/m² for the wavelength range 280-400 nm."

### Appendix E: ISO/IEC 17025 Clause 7.6 Checklist

- [ ] All uncertainty sources identified
- [ ] Type A evaluations performed (where applicable)
- [ ] Type B evaluations performed
- [ ] Sensitivity coefficients determined
- [ ] Combined standard uncertainty calculated
- [ ] Effective degrees of freedom calculated
- [ ] Coverage factor justified
- [ ] Expanded uncertainty calculated
- [ ] Uncertainty statement included in certificate
- [ ] Uncertainty budget documented

---

## References

1. ISO/IEC 17025:2017 - General requirements for the competence of testing and calibration laboratories
2. JCGM 100:2008 - Evaluation of measurement data - Guide to the expression of uncertainty in measurement (GUM)
3. JCGM 200:2012 - International vocabulary of metrology - Basic and general concepts and associated terms (VIM)
4. ILAC P14:09/2020 - ILAC Policy for Measurement Uncertainty in Calibration
5. NABL 141 - Guidelines for Estimation and Use of Uncertainty of Measurement by Testing and Calibration Laboratories

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11 | Initial release |

---

**For technical support or questions, contact:**
PV Chamber Configurator Support
Email: support@pvconfigurator.com
