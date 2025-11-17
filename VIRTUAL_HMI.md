# Virtual HMI & Uniformity Robot - User Guide

**Version:** 2.0
**Phase:** 5 - Virtual HMI + Robot Integration
**Date:** November 2025

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Virtual HMI User Guide](#virtual-hmi-user-guide)
4. [Robot Control Manual](#robot-control-manual)
5. [Alarm Codes & Troubleshooting](#alarm-codes--troubleshooting)
6. [Test Recipes](#test-recipes)
7. [Data Logging & Export](#data-logging--export)
8. [Maintenance](#maintenance)

---

## Overview

The PV Chamber Configurator Phase 5 introduces a comprehensive Virtual HMI (Human-Machine Interface) for real-time chamber monitoring and control, integrated with a 3-axis uniformity measurement robot system.

### Key Features

- **Real-time Monitoring**: Temperature, Humidity, UV intensity with 9-point grid visualization
- **Chamber Control**: Setpoint adjustment, ramp rate control, start/stop/pause operations
- **Alarm Management**: Three-level alarm system (CRITICAL/WARNING/INFO) with acknowledgment
- **Uniformity Robot**: Automated 9-point grid measurements with 3D visualization
- **Data Logging**: Automatic data logging at configurable intervals with export to CSV/Excel/JSON
- **Test Recipes**: Pre-configured IEC 61215/61730 test profiles with automated execution

---

## System Architecture

### Components

```
pv-chamber-configurator/
├── modules/
│   ├── virtual_hmi.py              # HMI controller
│   ├── robot_controller.py         # Robot controller
│   └── visualizations/
│       └── hmi_components.py       # Streamlit UI components
├── data/
│   ├── alarm_rules.json            # Alarm configuration
│   └── sample_recipes.json         # Test recipes
├── logs/
│   └── chamber_data.db             # SQLite database
├── tests/
│   ├── test_virtual_hmi.py         # HMI test suite
│   └── test_robot_controller.py   # Robot test suite
└── app.py                          # Main application
```

### Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Data Visualization**: Plotly (interactive charts and gauges)
- **Data Storage**: SQLite (time-series data logging)
- **Data Processing**: Pandas, NumPy
- **Control Logic**: Python 3.9+

---

## Virtual HMI User Guide

### Dashboard Tab

The dashboard provides real-time visualization of chamber parameters.

#### Parameter Cards

Each parameter displays:
- Current value
- Setpoint
- Deviation from setpoint
- Status indicator (✅ good, ⚡ warning, ⚠️ critical)

**Parameters:**
- **Temperature**: Range -45°C to +105°C
- **Humidity**: Range 40% to 95% RH
- **UV Intensity**: Range 0 to 250 W/m²

#### Gauges

Animated gauges show real-time values with color-coded zones:
- **Green**: Normal operation
- **Yellow**: Warning threshold
- **Red**: Critical threshold

#### Trend Charts

24-hour historical trends for:
- Temperature (with setpoint overlay)
- Humidity (with setpoint overlay)
- UV Intensity (with setpoint overlay)
- Power Consumption

#### Uniformity Heatmaps

9-point grid heatmaps showing spatial distribution:
- Temperature uniformity across chamber
- Humidity uniformity
- UV intensity uniformity

**Interpreting Heatmaps:**
- Darker red = Higher values
- Darker green = Lower values
- Uniformity % shown in title (lower is better)

### Control Panel Tab

#### Setpoint Adjustments

**Temperature Setpoint:**
- Range: -45°C to +105°C
- Adjust using slider
- Click "Set Temperature" to apply
- Chamber will ramp at configured ramp rate

**Humidity Setpoint:**
- Range: 40% to 95% RH
- Adjust using slider
- Click "Set Humidity" to apply

**UV Intensity:**
- Range: 0 to 250 W/m²
- Adjust using slider
- Click "Set UV Intensity" to apply
- UV LEDs respond quickly (< 5 seconds)

**Ramp Rate:**
- Range: 0.5 to 5.0 °C/min
- Controls how fast temperature changes
- Lower rates = gentler thermal cycling
- Higher rates = faster test execution

#### Operation Modes

- **Manual**: Direct setpoint control
- **Auto**: Automatic setpoint tracking (future feature)
- **Recipe**: Execute pre-programmed test sequences

#### Chamber Operations

**START (▶️):**
- Starts chamber operation
- Begins ramping to setpoints
- Enables data logging
- Only available when chamber is Idle or Paused

**PAUSE (⏸️):**
- Pauses chamber operation
- Maintains current conditions
- Data logging continues
- Can resume from paused state

**STOP (⏹️):**
- Stops chamber operation
- Returns to ambient conditions
- Stops active recipe (if running)
- Data logging continues until fully stopped

**EMERGENCY STOP (🛑):**
- **USE ONLY IN EMERGENCIES**
- Immediately halts all chamber operations
- Triggers critical alarm
- Disables UV system
- Stops refrigeration
- Requires manual reset

### Alarms Tab

#### Active Alarms Panel

Displays all currently active alarms with:
- Alarm level icon (🔴 CRITICAL, 🟡 WARNING, 🔵 INFO)
- Alarm message
- Timestamp
- Alarm ID
- Acknowledge button

**To Acknowledge an Alarm:**
1. Review alarm message
2. Address underlying cause
3. Click "Acknowledge" button
4. Alarm moves to history

#### Alarm History

Scrollable table showing:
- All alarms (up to last 50)
- Timestamp
- Level
- Message
- Acknowledgment status (✓/✗)

---

## Robot Control Manual

### Robot Specifications

- **Workspace**: 3000mm (X) × 2000mm (Y) × 1500mm (Z)
- **Speed**: 100-500 mm/s (configurable)
- **Acceleration**: 1000 mm/s²
- **Positioning Accuracy**: ±1mm
- **Measurement Sensors**:
  - RTD temperature sensor (±0.1°C)
  - Capacitive humidity sensor (±2% RH)
  - UV radiometer (±5% accuracy)

### Manual Control Tab

#### Homing

**ALWAYS HOME THE ROBOT FIRST!**

1. Click "🏠 Home All Axes"
2. Robot moves to origin (0, 0, 0)
3. Wait for "Robot homed successfully" message
4. Position indicator updates to (0, 0, 0)

#### Jog Controls

**Jog Distance:**
- Set desired increment (1-500mm)
- Default: 100mm

**X Axis:**
- ⬅️ X- : Move left
- ➡️ X+ : Move right

**Y Axis:**
- ⬇️ Y- : Move backward
- ⬆️ Y+ : Move forward

**Z Axis:**
- 🔽 Z- : Move down
- 🔼 Z+ : Move up

**Safety Notes:**
- Robot will not move beyond workspace limits
- Emergency stop available at all times
- Current position displayed in real-time

#### 3D Visualization

The 3D view shows:
- Gray wireframe: Workspace boundaries
- Red diamond: Current robot position
- Green circles: Planned measurement points
- Interactive: Rotate, zoom, pan

### Auto Measurement Tab

#### 9-Point Grid Measurement

**Purpose:** Automated uniformity verification at 9 equally-spaced points

**Procedure:**
1. Ensure chamber is at stable conditions
2. Set measurement height (Z): Typically 750mm (chamber center)
3. Review estimated completion time
4. Click "▶️ Start 9-Point Measurement"
5. Robot executes snake pattern through grid
6. Results automatically displayed when complete

**Grid Pattern:**
```
1  →  2  →  3
          ↓
6  ←  5  ←  4
↓
7  →  8  →  9
```

**Measurement Sequence:**
1. Move to Point 1
2. Wait 2 seconds (sensor stabilization)
3. Record temperature, humidity, UV
4. Move to Point 2
5. Repeat through Point 9
6. Calculate uniformity statistics
7. Return to home or last position

#### G-Code Custom Paths

**Supported Commands:**
- `G28` - Home all axes
- `G0`/`G1` - Linear move (e.g., `G0 X1500 Y1000 Z750 F500`)
  - `X`: X position (mm)
  - `Y`: Y position (mm)
  - `Z`: Z position (mm)
  - `F`: Feed rate (mm/s)
- `M3` - Start measurement mode
- `M5` - Stop measurement mode
- `;` - Comment (ignored)

**Example G-Code:**
```gcode
; Custom 5-point measurement
G28                          ; Home
G0 X1500 Y1000 Z750 F300    ; Move to center
M3                          ; Start measuring
G1 X500 Y500 Z750           ; Point 1
G1 X1500 Y500 Z750          ; Point 2
G1 X2500 Y500 Z750          ; Point 3
G1 X1500 Y1000 Z750         ; Point 4 (center)
G1 X1500 Y1500 Z750         ; Point 5
M5                          ; Stop measuring
G28                         ; Return home
```

**To Execute:**
1. Create G-code file (.gcode, .nc, .txt)
2. Click "Upload G-Code File"
3. Review parsed commands
4. Click "Execute G-Code"
5. Monitor progress

### Results Tab

Displays last completed measurement with:

#### Summary Metrics
- Measurement duration
- Grid size (3×3)
- Average temperature & uniformity %
- Average UV intensity & uniformity %

#### Heatmaps
- Visual representation of 9-point grid
- Color-coded by parameter value
- Uniformity % in title

#### Detailed Table
- All 9 measurements
- X, Y, Z coordinates
- Temperature, Humidity, UV readings

#### Export
- Click "💾 Export Results to CSV"
- Saved to `logs/robot_measurement_YYYYMMDD_HHMMSS.csv`

---

## Alarm Codes & Troubleshooting

### Critical Alarms (🔴)

#### TEMP_DEVIATION_HIGH
**Code:** TEMP_DEVIATION_HIGH
**Message:** Temperature deviation >5°C from setpoint
**Cause:** Control system unable to maintain setpoint
**Action:**
1. Check refrigeration system
2. Verify heater operation
3. Check for door seal leaks
4. Review ramp rate setting

#### OVER_TEMPERATURE
**Code:** OVER_TEMPERATURE
**Message:** Over-temperature alarm - Chamber >110°C
**Cause:** Safety limit exceeded
**Action:**
1. **IMMEDIATE**: Activate emergency stop
2. Check temperature sensor calibration
3. Verify heater relay not stuck closed
4. Inspect control system

#### UNDER_TEMPERATURE
**Code:** UNDER_TEMPERATURE
**Message:** Under-temperature alarm - Chamber <-50°C
**Cause:** Safety limit exceeded
**Action:**
1. Check refrigeration system
2. Verify temperature sensor
3. Inspect refrigerant levels

#### EMERGENCY_STOP
**Code:** EMERGENCY_STOP
**Message:** Emergency stop activated
**Cause:** Manual e-stop pressed
**Action:**
1. Identify reason for e-stop
2. Resolve safety issue
3. Reset e-stop button
4. Restart chamber

### Warning Alarms (🟡)

#### TEMP_UNIFORMITY_DEVIATION
**Code:** TEMP_UNIFORMITY_DEVIATION
**Message:** Temperature uniformity deviation >10%
**Cause:** Poor air circulation or sensor issue
**Action:**
1. Run robot uniformity measurement
2. Check circulation fan operation
3. Verify all sensors calibrated
4. Inspect for obstructions in chamber

#### UV_OUT_OF_RANGE
**Code:** UV_OUT_OF_RANGE
**Message:** UV intensity deviation >15 W/m² from setpoint
**Cause:** LED aging or power supply issue
**Action:**
1. Check LED array operation
2. Verify DC power supply output
3. Clean UV sensor window
4. Inspect LED connections

#### HUMIDITY_DEVIATION
**Code:** HUMIDITY_DEVIATION
**Message:** Humidity deviation >5% from setpoint
**Cause:** Steam generator or dehumidification issue
**Action:**
1. Check water supply to steam generator
2. Verify dehumidification system
3. Check door seals
4. Inspect humidity sensor

### Info Alarms (🔵)

#### SETPOINT_REACHED
**Code:** SETPOINT_REACHED
**Message:** Temperature setpoint reached
**Cause:** Normal operation - informational
**Action:** None required - acknowledge when ready

#### TEST_COMPLETE
**Code:** TEST_COMPLETE
**Message:** Test sequence complete
**Cause:** Recipe finished successfully
**Action:** Review results, export data, acknowledge

---

## Test Recipes

### Available Recipes

#### 1. IEC 61215 TC200 - Thermal Cycling

**Standard:** IEC 61215-2:2016
**Duration:** 267 hours (11.1 days)
**Cycles:** 200

**Profile:**
- Cold soak: -40°C for 30 min
- Hot soak: +85°C for 30 min
- Return to ambient: 25°C
- Repeat 200 times

**Purpose:** Stress testing for solder joints, interconnects, and encapsulation

#### 2. IEC 61215 HF10 - Humidity Freeze

**Standard:** IEC 61215-2:2016
**Duration:** 240 hours (10 days)
**Cycles:** 10

**Profile:**
- Humidity soak: 85°C / 85% RH for 20 hours
- Freeze: -40°C for 1 hour
- Recovery: 25°C / 50% RH for 1 hour
- Repeat 10 times

**Purpose:** Test moisture ingress and freeze-thaw cycling

#### 3. IEC 61215 DH1000 - Damp Heat

**Standard:** IEC 61215-2:2016
**Duration:** 1000 hours (41.7 days)
**Cycles:** 1

**Profile:**
- Constant: 85°C / 85% RH for 1000 hours

**Purpose:** Accelerated aging for moisture and temperature resistance

#### 4. IEC 61215 UV Preconditioning

**Standard:** IEC 61215-2:2016
**Duration:** 250 hours (10.4 days)
**Total UV Dose:** 15 kWh/m²

**Profile:**
- 60°C with 60 W/m² UV (300-400nm)
- Until 15 kWh/m² accumulated

**Purpose:** UV degradation testing for encapsulants and backsheet

#### 5. Quick Uniformity Test

**Standard:** Custom
**Duration:** 2 hours

**Profile:**
- Temperature uniformity at 85°C
- Humidity uniformity at 85% RH
- UV uniformity at 60 W/m²
- Robot measurements at each step

**Purpose:** Quick verification of chamber uniformity

### Executing a Recipe

1. Navigate to "📋 Test Recipes" tab
2. Select recipe from dropdown
3. Review recipe details and steps
4. Click "▶️ Execute Recipe"
5. Monitor progress in Virtual HMI
6. Recipe runs automatically through all steps
7. Alarm raised on completion

---

## Data Logging & Export

### Automatic Logging

**Default Interval:** 60 seconds (configurable)

**Logged Parameters:**
- Temperature (average & 9-point grid)
- Humidity (average & 9-point grid)
- UV Intensity (average & 9-point grid)
- Power consumption (kW)
- Ramp rate (°C/min)
- Chamber status
- Alarm events
- User actions

**Storage:**
- Location: `logs/chamber_data.db` (SQLite)
- Retention: 90 days (configurable)
- Automatic cleanup of old data

### Manual Data Export

1. Navigate to "📊 Data Logs" tab
2. Select date range (Start Date, End Date)
3. Choose export format:
   - **CSV**: For Excel, data analysis
   - **Excel**: Native .xlsx format
   - **JSON**: For programmatic access
4. Click "Export Data"
5. Download exported file

**Export Includes:**
- All logged parameters
- Timestamp for each record
- Alarm events during period
- User actions during period

### Log Statistics

7-day summary shows:
- Total records logged
- Average temperature
- Min/max temperature
- Average humidity
- Average power consumption

---

## Maintenance

### Daily Checks

- [ ] Review active alarms
- [ ] Check chamber status
- [ ] Verify auto-refresh is working
- [ ] Review power consumption trends

### Weekly Checks

- [ ] Run Quick Uniformity Test
- [ ] Export and backup data logs
- [ ] Review alarm history
- [ ] Check robot homing accuracy

### Monthly Checks

- [ ] Clean UV sensor windows
- [ ] Calibrate temperature sensors (RTD)
- [ ] Calibrate humidity sensors
- [ ] Calibrate UV radiometer
- [ ] Inspect robot cables and connections
- [ ] Lubricate robot axes if needed

### Quarterly Checks

- [ ] Full 9-point uniformity verification
- [ ] Compare to acceptance criteria
- [ ] Update alarm thresholds if needed
- [ ] Review and optimize recipes
- [ ] Database optimization (vacuum)

### Calibration Schedule

**Temperature Sensors:**
- Frequency: Every 90 days
- Method: Ice bath (0°C) and boiling water (100°C)
- Acceptance: ±0.5°C

**Humidity Sensors:**
- Frequency: Every 90 days
- Method: Saturated salt solutions
- Acceptance: ±3% RH

**UV Radiometer:**
- Frequency: Every 180 days
- Method: Certified reference source
- Acceptance: ±5% of reading

### Troubleshooting

#### HMI Not Responding

1. Check browser console for errors
2. Refresh page (Ctrl+F5)
3. Verify network connection
4. Restart Streamlit server: `streamlit run app.py`

#### Robot Not Homing

1. Check emergency stop not active
2. Verify limit switches operational
3. Inspect robot cables
4. Restart robot controller

#### Data Not Logging

1. Check disk space in `logs/` directory
2. Verify database not corrupted: `sqlite3 logs/chamber_data.db "PRAGMA integrity_check;"`
3. Check logging interval setting
4. Review system logs

#### Alarms Not Triggering

1. Verify `data/alarm_rules.json` exists
2. Check alarm threshold values
3. Test with manual alarm: `hmi.raise_alarm('INFO', 'Test')`
4. Review alarm configuration in Settings tab

---

## Safety Warnings

⚠️ **ELECTRICAL HAZARD**
- Do not open chamber during operation
- Ensure proper grounding
- Qualified personnel only for maintenance

⚠️ **THERMAL HAZARD**
- Chamber surfaces may be extremely hot or cold
- Wait for chamber to return to ambient before opening
- Wear appropriate PPE

⚠️ **UV RADIATION HAZARD**
- Do not look directly at UV LEDs
- UV safety glasses required when chamber door open
- UV automatically disabled when door opened

⚠️ **MECHANICAL HAZARD**
- Robot in motion - keep clear
- Do not enter workspace during operation
- Emergency stop readily accessible

---

## Support

For technical support:
- Email: info@zenitek.com
- Documentation: See project README.md
- Issue Tracker: GitHub repository

---

**Document Version:** 1.0
**Last Updated:** November 2025
**Author:** Zenitek Solutions Engineering Team

---
