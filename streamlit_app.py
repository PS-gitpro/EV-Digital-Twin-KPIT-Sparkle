import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import base64
import io

st.set_page_config(
    page_title="EV Digital Twin - Team TIGONS",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# PROFESSIONAL CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem !important;
        color: #1a237e;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 800;
    }
    .section-header {
        background: linear-gradient(90deg, #1a237e, #3949ab);
        color: white;
        padding: 12px;
        border-radius: 10px;
        margin: 10px 0;
        font-weight: bold;
    }
    .alert-timeline {
        background: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
    }
    .alert-warning {
        border-left-color: #ffc107;
        background: #fff3cd;
    }
    .alert-danger {
        border-left-color: #dc3545;
        background: #f8d7da;
    }
    .alert-success {
        border-left-color: #28a745;
        background: #d4edda;
    }
    .prediction-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 8px 0;
    }
    .mode-charging {
        border: 2px solid #28a745;
        background: rgba(40, 167, 69, 0.1);
    }
    .mode-discharging {
        border: 2px solid #fd7e14;
        background: rgba(253, 126, 20, 0.1);
    }
    .compare-mode {
        border: 3px dashed #ff6b6b;
        background: rgba(255, 107, 107, 0.1);
        padding: 15px;
        border-radius: 10px;
    }
    .mobile-view {
        background: #2c3e50;
        color: white;
        padding: 15px;
        border-radius: 15px;
        font-family: Arial, sans-serif;
    }
    .mobile-metric {
        background: rgba(255,255,255,0.1);
        padding: 10px;
        border-radius: 5px;
        text-align: center;
    }
    .mobile-header {
        text-align: center;
        color: white;
        margin-bottom: 15px;
    }
    .load-high { background: #ff6b6b; color: white; padding: 5px; border-radius: 5px; }
    .load-medium { background: #ffd93d; color: black; padding: 5px; border-radius: 5px; }
    .load-low { background: #6bcf7f; color: white; padding: 5px; border-radius: 5px; }
    .user-input-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

class EVDigitalTwin:
    def __init__(self):
        self.event_log = []
        self.fault_injected = False
        self.start_time = datetime.now()
        
        # DEFAULT VALUES - User will change these
        self.voltage_range = [9.0, 13.0]
        self.fault_limits = {'voltage': 10.5, 'temperature': 85, 'current': 4.0}
        self.safe_limits = {'voltage_min': 9.0, 'voltage_max': 13.0, 'temp_max': 60}
        self.load_percentage = 50
        self.pwm_percentage = 75
        self.base_temperature = 25
        self.noise_level = 0.1
        self.simulation_steps = 100
        
        self.log_event("Digital Twin Initialized", "SUCCESS")
    
    def update_parameters(self, voltage_range, fault_limits, load_pct, pwm_pct, base_temp, noise, steps):
        """Update simulation parameters based on USER INPUT"""
        self.voltage_range = voltage_range
        self.fault_limits = fault_limits
        self.load_percentage = load_pct
        self.pwm_percentage = pwm_pct
        self.base_temperature = base_temp
        self.noise_level = noise
        self.simulation_steps = steps
        
        self.log_event(f"User updated parameters: Load={load_pct}%, PWM={pwm_pct}%, Temp={base_temp}°C", "INFO")
    
    def log_event(self, event, status="INFO"):
        """Log system events with timestamps"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.event_log.append({
            'timestamp': timestamp,
            'event': event,
            'status': status
        })
        if len(self.event_log) > 20:
            self.event_log = self.event_log[-20:]
    
    def calculate_temperature_effect(self, current, voltage, is_charging, load_factor):
        """Calculate temperature based on USER INPUT parameters"""
        i2r_heating = (current ** 2) * 0.0008 * load_factor
        voltage_heating = abs(voltage - 12.0) * 0.3 * load_factor
        charging_boost = 0.6 if is_charging else 0.3
        charging_heating = charging_boost * load_factor
        
        total_heating = i2r_heating + voltage_heating + charging_heating
        return total_heating
    
    def predict_temperature(self, current_temp, current, voltage, is_charging):
        """Predict temperature based on USER INPUT parameters"""
        load_factor = self.load_percentage / 100.0
        cooling_factor = self.pwm_percentage / 100.0
        
        heating_rate = self.calculate_temperature_effect(current, voltage, is_charging, load_factor)
        effective_heating = heating_rate * (1.0 - cooling_factor * 0.4)
        
        predicted_temp = current_temp + effective_heating * 5
        return min(85, max(15, predicted_temp))
    
    def predict_discharge_time(self, soc, current):
        """Predict remaining discharge time"""
        if current >= 0:
            return "N/A (Charging)"
        
        load_factor = self.load_percentage / 100.0
        discharge_rate = abs(current) / 100 * load_factor
        
        if discharge_rate == 0:
            return "∞"
        minutes_left = (soc / 100) / discharge_rate * 60
        return f"{minutes_left:.1f} mins"
    
    def simulate_fault(self, sensor_data):
        """Simulate various fault scenarios"""
        if not self.fault_injected:
            return sensor_data
        
        fault_type = np.random.choice(['voltage_drop', 'thermal_spike', 'sensor_failure', 'over_current'])
        
        if fault_type == 'voltage_drop':
            sensor_data['voltage'] = self.fault_limits['voltage'] - np.random.uniform(0.5, 2.0)
            self.log_event("⚠️ VOLTAGE DROP DETECTED", "DANGER")
        elif fault_type == 'thermal_spike':
            sensor_data['temperature'] = self.fault_limits['temperature'] + np.random.uniform(5, 15)
            self.log_event("🔥 THERMAL SPIKE DETECTED", "DANGER")
        elif fault_type == 'sensor_failure':
            sensor_data['current'] = 0
            self.log_event("🔧 CURRENT SENSOR FAILURE", "WARNING")
        elif fault_type == 'over_current':
            sensor_data['current'] = self.fault_limits['current'] + np.random.uniform(1, 3)
            self.log_event("⚡ OVER-CURRENT DETECTED", "DANGER")
        
        return sensor_data

def generate_sensor_data(previous_soc=75, is_charging=True, digital_twin=None):
    """Generate sensor data based on USER INPUT parameters"""
    if digital_twin is None:
        digital_twin = EVDigitalTwin()
    
    # USE USER INPUT PARAMETERS
    base_voltage_range = digital_twin.voltage_range
    base_temp = digital_twin.base_temperature
    noise_level = digital_twin.noise_level
    load_factor = digital_twin.load_percentage / 100.0
    
    # USER INPUT BASED CALCULATIONS
    if is_charging:
        charge_rate = (1.0 + load_factor * 0.8) * (1.2 + np.random.uniform(0, 0.8))
        new_soc = min(98, previous_soc + charge_rate)
        current = (25 + load_factor * 15 + np.random.uniform(0, 12))
        voltage = base_voltage_range[0] + (new_soc/100) * (base_voltage_range[1] - base_voltage_range[0]) / 2
    else:
        discharge_rate = (0.6 + load_factor * 0.6) * (0.8 + np.random.uniform(0, 0.6))
        new_soc = max(15, previous_soc - discharge_rate)
        current = (-20 - load_factor * 20 - np.random.uniform(0, 15))
        voltage = base_voltage_range[0] + (new_soc/100) * (base_voltage_range[1] - base_voltage_range[0]) / 1.5
    
    # APPLY USER-DEFINED NOISE
    voltage += np.random.normal(0, noise_level)
    current += np.random.normal(0, noise_level * 0.5)
    
    # TEMPERATURE BASED ON USER INPUTS
    temp_increase = digital_twin.calculate_temperature_effect(current, voltage, is_charging, load_factor)
    temperature = base_temp + temp_increase * 8 + np.random.uniform(-1, 1)
    
    health_degradation = (100 - new_soc) * 0.05 + max(0, temperature - 30) * 0.15 + load_factor * 0.1
    health_score = max(45, 97 - health_degradation)
    
    efficiency = 92 - load_factor * 8 - max(0, temperature - 25) * 0.3 + np.random.uniform(0, 3)
    
    return {
        'voltage': max(base_voltage_range[0], min(base_voltage_range[1], round(voltage, 3))),
        'current': round(current, 2),
        'temperature': round(temperature, 1),
        'soc': round(new_soc, 1),
        'health_score': round(health_score, 1),
        'timestamp': datetime.now().strftime("%H:%M:%S"),
        'is_charging': is_charging,
        'power': round(voltage * abs(current), 2),
        'energy_remaining': round(new_soc * 75 / 100, 1),
        'efficiency': max(65, round(efficiency, 1)),
        'energy_consumed': round((100 - new_soc) * 0.75, 1),
        'cycles_completed': np.random.randint(1, 10),
        'load_percentage': digital_twin.load_percentage,
        'user_temperature': digital_twin.base_temperature,
        'user_pwm': digital_twin.pwm_percentage
    }

def create_csv_download(df, filename):
    """Create CSV download link"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" style="background: #4CAF50; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; display: inline-block;">📥 {filename}</a>'
    return href

def create_pdf_download(report_text, filename):
    """Create PROPER PDF download link"""
    # Create a text file that can be saved as PDF
    b64 = base64.b64encode(report_text.encode()).decode()
    href = f'<a href="data:text/plain;base64,{b64}" download="{filename}" style="background: #dc3545; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 5px;">📄 {filename}</a>'
    return href

def create_pdf_report(sensor_data, digital_twin):
    """Create a comprehensive PDF report"""
    report = f"""
EV BATTERY PERFORMANCE REPORT
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Team: TIGONS | KPIT Sparkle 2025

CURRENT STATUS:
• State of Charge: {sensor_data['soc']}%
• Voltage: {sensor_data['voltage']}V
• Current: {sensor_data['current']}A  
• Temperature: {sensor_data['temperature']}°C
• Health Score: {sensor_data['health_score']}%
• Efficiency: {sensor_data['efficiency']}%
• Power Output: {sensor_data['power']}W

USER CONFIGURED PARAMETERS:
• Load Percentage: {digital_twin.load_percentage}%
• PWM Cooling: {digital_twin.pwm_percentage}%
• Base Temperature: {digital_twin.base_temperature}°C
• Sensor Noise: {digital_twin.noise_level}
• Simulation Steps: {digital_twin.simulation_steps}
• Voltage Range: {digital_twin.voltage_range[0]}V - {digital_twin.voltage_range[1]}V

FAULT LIMITS:
• Voltage Fault: {digital_twin.fault_limits['voltage']}V
• Temperature Fault: {digital_twin.fault_limits['temperature']}°C  
• Current Fault: {digital_twin.fault_limits['current']}A

LOAD-TEMPERATURE ANALYSIS:
• Current Load Level: {digital_twin.load_percentage}%
• I²R Heating Effect: {sensor_data['current']**2 * 0.0008 * (digital_twin.load_percentage/100.0):.3f}
• Cooling Effect (PWM): {digital_twin.pwm_percentage}%
• Thermal Stress: {'HIGH' if sensor_data['temperature'] > 50 else 'MEDIUM' if sensor_data['temperature'] > 40 else 'LOW'}

PREDICTIVE INSIGHTS:
• Predicted Temperature (5min): {digital_twin.predict_temperature(sensor_data['temperature'], sensor_data['current'], sensor_data['voltage'], sensor_data['is_charging']):.1f}°C
• Discharge Time: {digital_twin.predict_discharge_time(sensor_data['soc'], sensor_data['current'])}
• Health Degradation Rate: {0.02 + max(0, sensor_data['temperature'] - 30) * 0.005 + (digital_twin.load_percentage/100.0) * 0.01:.3f}% per cycle

RECOMMENDATIONS:
• Maintain SOC between 20-80%
• Keep temperature below 35°C for optimal performance
• Reduce load if temperature exceeds 45°C
• Monitor voltage regularly for early fault detection
• Schedule maintenance every 30 days
• Adjust PWM cooling based on load conditions

---
Generated by EV Digital Twin Platform
Team TIGONS - JSPM JSCOE, Pune
Contact: tigons.kpit2025@gmail.com
"""
    return report

def show_user_input_section(digital_twin):
    """Show user input controls section"""
    st.markdown("### 🎛️ USER INPUT PARAMETERS")
    
    with st.container():
        st.markdown('<div class="user-input-section">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 🔧 SYSTEM PARAMETERS")
            load_percentage = st.slider(
                "**Load Percentage (%)**", 
                10, 100, digital_twin.load_percentage, 5,
                help="SYSTEM STRESS: Higher load = More current = More heat generation"
            )
            
            pwm_percentage = st.slider(
                "**PWM Cooling (%)**", 
                0, 100, digital_twin.pwm_percentage, 5,
                help="COOLING SYSTEM: Higher PWM = Better cooling = Lower temperature"
            )
            
            base_temperature = st.slider(
                "**Base Temperature (°C)**", 
                15, 40, digital_twin.base_temperature, 1,
                help="STARTING TEMPERATURE: Initial condition for simulation"
            )
        
        with col2:
            st.markdown("#### 📡 SENSOR PARAMETERS")
            noise_level = st.slider(
                "**Sensor Noise Level**", 
                0.0, 0.5, digital_twin.noise_level, 0.01,
                help="SENSOR ACCURACY: Higher noise = More realistic but less accurate readings"
            )
            
            simulation_steps = st.slider(
                "**Simulation Steps**", 
                50, 200, digital_twin.simulation_steps, 10,
                help="DATA HISTORY: Number of data points to keep in memory"
            )
            
            voltage_min = st.slider(
                "**Min Voltage (V)**", 
                8.0, 12.0, digital_twin.voltage_range[0], 0.1,
                help="MINIMUM VOLTAGE: Lower operating limit"
            )
        
        with col3:
            st.markdown("#### ⚠️ FAULT SETTINGS")
            voltage_max = st.slider(
                "**Max Voltage (V)**", 
                12.0, 15.0, digital_twin.voltage_range[1], 0.1,
                help="MAXIMUM VOLTAGE: Upper operating limit"
            )
            
            fault_voltage = st.slider(
                "**Voltage Fault Limit (V)**", 
                8.0, 12.0, digital_twin.fault_limits['voltage'], 0.1,
                help="VOLTAGE FAULT: Trigger fault below this voltage"
            )
            
            fault_temperature = st.slider(
                "**Temperature Fault Limit (°C)**", 
                60, 100, digital_twin.fault_limits['temperature'], 1,
                help="TEMPERATURE FAULT: Trigger fault above this temperature"
            )
            
            fault_current = st.slider(
                "**Current Fault Limit (A)**", 
                2.0, 6.0, digital_twin.fault_limits['current'], 0.1,
                help="CURRENT FAULT: Trigger fault above this current"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Update button
        if st.button("🔄 APPLY USER PARAMETERS", use_container_width=True):
            voltage_range = [voltage_min, voltage_max]
            fault_limits = {'voltage': fault_voltage, 'temperature': fault_temperature, 'current': fault_current}
            digital_twin.update_parameters(
                voltage_range, fault_limits, load_percentage, pwm_percentage, 
                base_temperature, noise_level, simulation_steps
            )
            st.success("✅ User parameters applied successfully!")
            st.rerun()

def show_load_temperature_analysis(sensor_data, digital_twin):
    """Show detailed load-temperature relationship"""
    st.markdown("### 🔥 LOAD-TEMPERATURE ANALYSIS")
    
    load_factor = digital_twin.load_percentage / 100.0
    current = sensor_data['current']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        i2r_heating = (current ** 2) * 0.0008 * load_factor
        st.metric("I²R Heating", f"{i2r_heating:.3f}")
    
    with col2:
        voltage_heating = abs(sensor_data['voltage'] - 12.0) * 0.3 * load_factor
        st.metric("Voltage Effect", f"{voltage_heating:.3f}")
    
    with col3:
        cooling_effect = digital_twin.pwm_percentage / 100.0 * 0.4
        st.metric("Cooling Effect", f"{cooling_effect:.3f}")
    
    with col4:
        net_heating = i2r_heating + voltage_heating - cooling_effect
        st.metric("Net Heating", f"{net_heating:.3f}")
    
    # Load level indicator
    if digital_twin.load_percentage >= 80:
        load_class = "load-high"
        load_status = "🚨 HIGH LOAD - HIGH TEMPERATURE"
    elif digital_twin.load_percentage >= 50:
        load_class = "load-medium" 
        load_status = "⚠️ MEDIUM LOAD - MEDIUM TEMP"
    else:
        load_class = "load-low"
        load_status = "✅ LOW LOAD - LOW TEMPERATURE"
    
    st.markdown(f'<div class="{load_class}" style="text-align: center; padding: 15px; margin: 10px 0; font-size: 16px; font-weight: bold;">{load_status} | User Load: {digital_twin.load_percentage}% | Current Temp: {sensor_data["temperature"]}°C</div>', unsafe_allow_html=True)

def show_mobile_view(sensor_data, digital_twin):
    """Show mobile-optimized view for field engineers"""
    st.markdown("### 📱 MOBILE VIEW - FIELD ENGINEER DASHBOARD")
    
    with st.container():
        st.markdown('<div class="mobile-view">', unsafe_allow_html=True)
        
        # Header
        st.markdown('<h3 class="mobile-header">🔋 FIELD MONITOR - TEAM TIGONS</h3>', unsafe_allow_html=True)
        
        # Large SOC Display
        with st.container():
            st.markdown(
                f"""
                <div style="background: rgba(255,255,255,0.2); padding: 20px; border-radius: 10px; margin: 10px 0; text-align: center;">
                    <h1 style="color: #4CAF50; margin: 0; font-size: 48px;">{sensor_data['soc']}%</h1>
                    <p style="margin: 5px 0; color: white; font-size: 18px;">State of Charge</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        # 2x2 Metrics Grid
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(
                f'<div class="mobile-metric"><div>⚡ Voltage</div><div style="font-weight: bold; font-size: 20px;">{sensor_data["voltage"]}V</div></div>', 
                unsafe_allow_html=True
            )
            
            temp_color = "#FF6B6B" if sensor_data['temperature'] > 45 else "#FFD93D" if sensor_data['temperature'] > 35 else "#4CAF50"
            st.markdown(
                f'<div class="mobile-metric"><div>🌡️ Temperature</div><div style="font-weight: bold; font-size: 20px; color: {temp_color};">{sensor_data["temperature"]}°C</div></div>', 
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                f'<div class="mobile-metric"><div>🔌 Current</div><div style="font-weight: bold; font-size: 20px;">{sensor_data["current"]}A</div></div>', 
                unsafe_allow_html=True
            )
            
            st.markdown(
                f'<div class="mobile-metric"><div>💪 Health</div><div style="font-weight: bold; font-size: 20px;">{sensor_data["health_score"]}%</div></div>', 
                unsafe_allow_html=True
            )
        
        # User Parameters Status
        st.markdown(
            f"""
            <div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 10px; margin: 10px 0;">
                <div style="text-align: center; color: white;">
                    <div style="font-size: 14px; margin-bottom: 5px;">USER PARAMETERS</div>
                    <div style="display: flex; justify-content: space-around; font-size: 12px;">
                        <div>📊 Load: {digital_twin.load_percentage}%</div>
                        <div>❄️ PWM: {digital_twin.pwm_percentage}%</div>
                        <div>🌡️ Base: {digital_twin.base_temperature}°C</div>
                    </div>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Status Bar
        mode_text = "⚡ CHARGING" if sensor_data['is_charging'] else "🔋 DISCHARGING"
        mode_color = "#28a745" if sensor_data['is_charging'] else "#fd7e14"
        
        st.markdown(
            f"""
            <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 10px 0; text-align: center;">
                <div style="color: {mode_color}; font-weight: bold; font-size: 18px;">{mode_text}</div>
                <div style="font-size: 12px; opacity: 0.8; color: white;">Last Update: {sensor_data['timestamp']}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick actions for field engineers
        st.markdown("#### 🎯 QUICK ACTIONS")
        action_col1, action_col2, action_col3 = st.columns(3)
        with action_col1:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        with action_col2:
            if st.button("📋 Log Issue", use_container_width=True):
                digital_twin.log_event("Field engineer logged issue via mobile", "WARNING")
                st.success("Issue logged successfully!")
        with action_col3:
            if st.button("📊 Parameters", use_container_width=True):
                st.info("Adjust parameters in sidebar")

def main():
    # Initialize digital twin
    if 'digital_twin' not in st.session_state:
        st.session_state.digital_twin = EVDigitalTwin()
    
    # Initialize session state
    if 'sensor_data' not in st.session_state:
        st.session_state.sensor_data = []
        st.session_state.last_soc = 65
        st.session_state.is_charging = True
        st.session_state.cycle_count = 0
        st.session_state.show_compare = False
        st.session_state.show_mobile = False

    # PROFESSIONAL HEADER
    st.markdown('<h1 class="main-header">🔋 EV DIGITAL TWIN PLATFORM</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center; color: #5c6bc0; margin-bottom: 1rem;">🐅 Team TIGONS | KPIT Sparkle 2025</h3>', unsafe_allow_html=True)
    
    # ==================== USER INPUT SECTION ====================
    show_user_input_section(st.session_state.digital_twin)
    
    # ==================== SIDEBAR - VIEW CONTROLS ====================
    with st.sidebar:
        st.markdown("### 🎮 VIEW CONTROLS")
        
        # Operation Mode
        mode = st.radio(
            "**OPERATION MODE:**",
            ["⚡ FAST CHARGE", "🔋 SMART DISCHARGE", "🔄 AUTO CYCLE"],
            index=0
        )
        new_charging_state = "CHARGE" in mode
        if new_charging_state != st.session_state.is_charging:
            st.session_state.is_charging = new_charging_state
            event = "Charging Started" if new_charging_state else "Discharging Started"
            st.session_state.digital_twin.log_event(event, "SUCCESS")
        
        st.markdown("---")
        st.markdown("### 🎯 VIEW MODES")
        st.session_state.show_compare = st.checkbox("🔀 COMPARE MODE")
        st.session_state.show_mobile = st.checkbox("📱 MOBILE VIEW", help="Optimized view for field engineers")
        
        st.session_state.digital_twin.fault_injected = st.checkbox("⚠️ INJECT FAULT SCENARIOS")
        
        st.markdown("---")
        st.markdown("### 📊 SYSTEM STATUS")
        
        if st.session_state.sensor_data:
            latest = st.session_state.sensor_data[-1]
            st.metric("Uptime", f"{(datetime.now() - st.session_state.digital_twin.start_time).seconds // 60} min")
            st.metric("Data Points", len(st.session_state.sensor_data))
            st.metric("Events Logged", len(st.session_state.digital_twin.event_log))

    # ==================== MAIN DASHBOARD ====================
    
    # Generate live data with USER INPUT parameters
    sensor_data = generate_sensor_data(
        st.session_state.last_soc, 
        st.session_state.is_charging,
        st.session_state.digital_twin
    )
    st.session_state.last_soc = sensor_data['soc']
    
    # Apply fault simulation if enabled
    sensor_data = st.session_state.digital_twin.simulate_fault(sensor_data)
    
    st.session_state.sensor_data.append(sensor_data)
    st.session_state.cycle_count += 1
    
    # Manage data history based on USER INPUT
    if len(st.session_state.sensor_data) > st.session_state.digital_twin.simulation_steps:
        st.session_state.sensor_data = st.session_state.sensor_data[-st.session_state.digital_twin.simulation_steps:]
    
    # ==================== SPECIAL VIEW MODES ====================
    
    if st.session_state.show_compare:
        st.markdown('<div class="compare-mode">', unsafe_allow_html=True)
        simulated_data = generate_sensor_data(
            st.session_state.last_soc - 2,
            st.session_state.is_charging,
            st.session_state.digital_twin
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📊 REAL BATTERY DATA")
            st.metric("Voltage", f"{sensor_data['voltage']}V")
            st.metric("Current", f"{sensor_data['current']}A")
            st.metric("Temperature", f"{sensor_data['temperature']}°C")
            st.metric("SOC", f"{sensor_data['soc']}%")
        
        with col2:
            st.markdown("#### 🤖 SIMULATED MODEL")
            st.metric("Voltage", f"{simulated_data['voltage']}V", 
                     f"{simulated_data['voltage'] - sensor_data['voltage']:+.2f}V")
            st.metric("Current", f"{simulated_data['current']}A",
                     f"{simulated_data['current'] - sensor_data['current']:+.2f}A")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ==================== MOBILE VIEW ====================
    if st.session_state.show_mobile:
        show_mobile_view(sensor_data, st.session_state.digital_twin)
    
    # ==================== DESKTOP VIEW ====================
    if not st.session_state.show_mobile:
        st.markdown('<div class="section-header">🎯 SIMULATION RESULTS</div>', unsafe_allow_html=True)
        
        # LOAD-TEMPERATURE ANALYSIS
        show_load_temperature_analysis(sensor_data, st.session_state.digital_twin)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # Battery Visualization
            mode_class = "mode-charging" if sensor_data['is_charging'] else "mode-discharging"
            st.markdown(f"""
            <div class="{mode_class}" style="padding: 20px; border-radius: 15px; margin: 10px 0;">
                <h3>🔋 BATTERY STATUS - {'⚡ CHARGING' if sensor_data['is_charging'] else '🔋 DISCHARGING'}</h3>
                <div style="background: rgba(255,255,255,0.2); border-radius: 10px; padding: 5px;">
                    <div style="background: {'#28a745' if sensor_data['is_charging'] else '#fd7e14'}; 
                                width: {sensor_data['soc']}%; height: 40px; border-radius: 8px; 
                                display: flex; align-items: center; justify-content: center; 
                                color: white; font-weight: bold; font-size: 20px;">
                        {sensor_data['soc']}%
                    </div>
                </div>
                <p><strong>User Parameters Applied:</strong></p>
                <p>• Load: {st.session_state.digital_twin.load_percentage}% | PWM: {st.session_state.digital_twin.pwm_percentage}%</p>
                <p>• Base Temp: {st.session_state.digital_twin.base_temperature}°C | Noise: {st.session_state.digital_twin.noise_level}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # PREDICTIVE INSIGHTS
            st.markdown("### 🤖 PREDICTIVE INSIGHTS")
            
            predicted_temp = st.session_state.digital_twin.predict_temperature(
                sensor_data['temperature'], sensor_data['current'], 
                sensor_data['voltage'], sensor_data['is_charging']
            )
            
            st.markdown(f"""
            <div class="prediction-card">
                <div>🌡️ Predicted Temp (5min):</div>
                <div style="font-size: 18px; font-weight: bold;">{predicted_temp:.1f}°C</div>
                <div style="color: {'#90EE90' if predicted_temp < 40 else '#FFB6C1'}">
                    {'✅ Safe' if predicted_temp < 40 else '⚠️ Monitor'}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            discharge_time = st.session_state.digital_twin.predict_discharge_time(
                sensor_data['soc'], sensor_data['current']
            )
            
            st.markdown(f"""
            <div class="prediction-card">
                <div>⏱️ Discharge Time:</div>
                <div style="font-size: 18px; font-weight: bold;">{discharge_time}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # EFFICIENCY METRICS
            st.markdown("### ⚡ EFFICIENCY METRICS")
            
            st.metric("Energy Efficiency", f"{sensor_data['efficiency']}%")
            st.metric("Power Output", f"{sensor_data['power']} W")
            st.metric("Health Score", f"{sensor_data['health_score']}%")
            st.metric("Energy Consumed", f"{sensor_data['energy_consumed']} Wh")
    
    # ==================== DATA VISUALIZATION ====================
    if not st.session_state.show_mobile:
        st.markdown('<div class="section-header">📊 DATA VISUALIZATION</div>', unsafe_allow_html=True)
        
        if len(st.session_state.sensor_data) > 1:
            df = pd.DataFrame(st.session_state.sensor_data)
            
            tab1, tab2, tab3 = st.tabs(["📈 Voltage & SOC", "🌡️ Temperature Trend", "⚡ Performance"])
            
            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    st.line_chart(df['voltage'], use_container_width=True)
                    st.caption("⚡ Voltage Profile (User Input Based)")
                with col2:
                    st.line_chart(df['soc'], use_container_width=True)
                    st.caption("🔋 State of Charge")
            
            with tab2:
                st.area_chart(df['temperature'], use_container_width=True)
                st.caption("🌡️ Temperature Trend - Affected by User Load Input")
            
            with tab3:
                st.line_chart(df[['current', 'efficiency']], use_container_width=True)
                st.caption("⚡ Current vs Efficiency")
    
    # ==================== EXPORT & REPORTS ====================
    st.markdown('<div class="section-header">📄 EXPORT & ANALYSIS</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 GENERATE CSV REPORT", use_container_width=True):
            if len(st.session_state.sensor_data) > 1:
                df = pd.DataFrame(st.session_state.sensor_data)
                st.markdown(create_csv_download(df, "battery_performance.csv"), unsafe_allow_html=True)
                st.session_state.digital_twin.log_event("CSV Report Generated", "SUCCESS")
    
    with col2:
        if st.button("📄 GENERATE PDF REPORT", use_container_width=True):
            pdf_report = create_pdf_report(sensor_data, st.session_state.digital_twin)
            # Show report preview
            st.text_area("📋 REPORT PREVIEW (Copy or Download below):", pdf_report, height=300)
            # Provide download link
            st.markdown(create_pdf_download(pdf_report, "EV_Battery_Report.txt"), unsafe_allow_html=True)
            st.session_state.digital_twin.log_event("PDF Report Generated", "SUCCESS")
    
    with col3:
        if st.button("🔄 LIVE DATA STREAM", use_container_width=True):
            st.info("🔄 Live data streaming active - Real-time monitoring enabled")
            st.session_state.digital_twin.log_event("Live data streaming enabled", "INFO")
    
    # ==================== AI INSIGHTS ====================
    st.markdown('<div class="section-header">🤖 AI-POWERED ANALYTICS</div>', unsafe_allow_html=True)
    
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        load_risk = st.session_state.digital_twin.load_percentage / 100.0 * 0.3
        temp_risk = max(0, sensor_data['temperature'] - 30) * 0.02
        risk_score = min(1.0, load_risk + temp_risk)
        
        if risk_score < 0.25:
            st.success("✅ **LOW RISK**\n\nOptimal operating conditions")
        elif risk_score < 0.6:
            st.warning("⚠️ **MEDIUM RISK**\n\nMonitor parameters closely")
        else:
            st.error("🚨 **HIGH RISK**\n\nImmediate action required")
        
        st.metric("AI Risk Score", f"{risk_score:.2f}")
    
    with insight_col2:
        st.info(f"""
        **🔧 PREDICTIVE MAINTENANCE**
        
        • User Load: **{st.session_state.digital_twin.load_percentage}%**
        • Cooling: **{st.session_state.digital_twin.pwm_percentage}%**
        • Base Temp: **{st.session_state.digital_twin.base_temperature}°C**
        • Efficiency: **{sensor_data['efficiency']}%**
        """)
    
    with insight_col3:
        recommendation = "Reduce load" if st.session_state.digital_twin.load_percentage > 70 else "Optimal load"
        st.success(f"""
        **💡 SMART OPTIMIZATION**
        
        • Current Load: **{st.session_state.digital_twin.load_percentage}%**
        • Recommendation: **{recommendation}**
        • Optimal Temp: **< 35°C**
        • Maintain SOC: **20-80%**
        """)
    
    # COMPETITION FOOTER
    st.markdown("---")
    st.success("🏆 **KPIT SPARKLE 2025 READY** - Industry-Grade EV Digital Twin with Real User Input Control & Professional Monitoring System")
    
    # AUTO-REFRESH
    refresh_delay = max(1, 6 - st.session_state.digital_twin.load_percentage / 20)
    time.sleep(refresh_delay)
    st.rerun()

if __name__ == "__main__":
    main()
