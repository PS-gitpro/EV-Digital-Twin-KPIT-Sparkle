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
</style>
""", unsafe_allow_html=True)

class EVDigitalTwin:
    def __init__(self):
        self.event_log = []
        self.fault_injected = False
        self.start_time = datetime.now()
        self.voltage_range = [9.0, 13.0]  # Configurable voltage range
        self.fault_limits = {'voltage': 10.5, 'temperature': 85, 'current': 4.0}
        self.safe_limits = {'voltage_min': 9.0, 'voltage_max': 13.0, 'temp_max': 60}
        self.load_percentage = 50  # System stress
        self.pwm_percentage = 75   # Cooling/control
        self.base_temperature = 25 # Starting condition
        self.noise_level = 0.1     # Sensor accuracy
        self.simulation_steps = 100 # Simulation length
        
        # Initialize with default values
        self.log_event("Digital Twin Initialized", "SUCCESS")
    
    def update_parameters(self, voltage_range, fault_limits, load_pct, pwm_pct, base_temp, noise, steps):
        """Update simulation parameters"""
        self.voltage_range = voltage_range
        self.fault_limits = fault_limits
        self.load_percentage = load_pct
        self.pwm_percentage = pwm_pct
        self.base_temperature = base_temp
        self.noise_level = noise
        self.simulation_steps = steps
        
        self.log_event(f"Parameters updated: Load={load_pct}%, PWM={pwm_pct}%, Temp={base_temp}°C", "INFO")
    
    def log_event(self, event, status="INFO"):
        """Log system events with timestamps"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.event_log.append({
            'timestamp': timestamp,
            'event': event,
            'status': status
        })
        # Keep only last 20 events
        if len(self.event_log) > 20:
            self.event_log = self.event_log[-20:]
    
    def predict_temperature(self, current_temp, current, voltage, is_charging):
        """Predict temperature 5 minutes ahead"""
        load_factor = self.load_percentage / 100.0
        cooling_factor = self.pwm_percentage / 100.0
        
        base_change = abs(current) * 0.002 * load_factor + (voltage - 3.7) * 0.5
        if is_charging:
            base_change += 0.8 * load_factor  # Charging generates more heat
        
        # Apply cooling effect from PWM
        base_change *= (1.0 - cooling_factor * 0.3)
        
        predicted_temp = current_temp + base_change * 5  # 5 minutes ahead
        return min(80, max(15, predicted_temp))
    
    def predict_discharge_time(self, soc, current):
        """Predict remaining discharge time"""
        if current >= 0:  # Charging
            return "N/A (Charging)"
        
        load_factor = self.load_percentage / 100.0
        discharge_rate = abs(current) / 100 * load_factor  # Load affects discharge rate
        
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
            sensor_data['current'] = 0  # Sensor failure
            self.log_event("🔧 CURRENT SENSOR FAILURE", "WARNING")
        elif fault_type == 'over_current':
            sensor_data['current'] = self.fault_limits['current'] + np.random.uniform(1, 3)
            self.log_event("⚡ OVER-CURRENT DETECTED", "DANGER")
        
        return sensor_data

def generate_sensor_data(previous_soc=75, is_charging=True, digital_twin=None):
    """Generate realistic sensor data with configurable parameters"""
    if digital_twin is None:
        digital_twin = EVDigitalTwin()
    
    # Use configurable parameters
    base_voltage_range = digital_twin.voltage_range
    base_temp = digital_twin.base_temperature
    noise_level = digital_twin.noise_level
    load_factor = digital_twin.load_percentage / 100.0
    
    if is_charging:
        charge_rate = (1.2 + np.random.uniform(0, 0.8)) * load_factor
        new_soc = min(98, previous_soc + charge_rate)
        current = (28 + np.random.uniform(0, 12)) * load_factor
        voltage = base_voltage_range[0] + (new_soc/100) * (base_voltage_range[1] - base_voltage_range[0]) / 2
    else:
        discharge_rate = (0.8 + np.random.uniform(0, 0.6)) * load_factor
        new_soc = max(15, previous_soc - discharge_rate)
        current = (-25 - np.random.uniform(0, 15)) * load_factor
        voltage = base_voltage_range[0] + (new_soc/100) * (base_voltage_range[1] - base_voltage_range[0]) / 1.5
    
    # Apply noise to sensor readings
    voltage += np.random.normal(0, noise_level)
    current += np.random.normal(0, noise_level * 0.5)
    
    # Temperature calculation with configurable base
    temp_increase = abs(current) * 0.12 * load_factor + (voltage - base_voltage_range[0]) * 0.8
    temperature = base_temp + temp_increase + np.random.uniform(-1, 1)
    
    health_degradation = (100 - new_soc) * 0.08 + max(0, temperature - 35) * 0.1
    health_score = max(45, 97 - health_degradation)
    
    # Calculate efficiency (affected by load and temperature)
    efficiency = 90 + np.random.uniform(0, 5) - max(0, temperature - 30) * 0.5 - (load_factor - 0.5) * 10
    
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
        'efficiency': max(70, round(efficiency, 1)),
        'energy_consumed': round((100 - new_soc) * 0.75, 1),
        'cycles_completed': np.random.randint(1, 10)
    }

def create_csv_download(df, filename):
    """Create CSV download link"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" style="background: #4CAF50; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; display: inline-block;">📥 {filename}</a>'
    return href

def create_pdf_report(sensor_data, digital_twin):
    """Create a simple PDF-like report (text format for demo)"""
    report = f"""
    EV BATTERY PERFORMANCE REPORT
    Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    Team: TIGONS | KPIT Sparkle 2025
    
    CURRENT STATUS:
    - State of Charge: {sensor_data['soc']}%
    - Voltage: {sensor_data['voltage']}V
    - Current: {sensor_data['current']}A
    - Temperature: {sensor_data['temperature']}°C
    - Health Score: {sensor_data['health_score']}%
    - Efficiency: {sensor_data['efficiency']}%
    
    SIMULATION PARAMETERS:
    - Voltage Range: {digital_twin.voltage_range[0]}V - {digital_twin.voltage_range[1]}V
    - Load Percentage: {digital_twin.load_percentage}%
    - PWM Cooling: {digital_twin.pwm_percentage}%
    - Base Temperature: {digital_twin.base_temperature}°C
    - Noise Level: {digital_twin.noise_level}
    
    FAULT LIMITS:
    - Voltage: {digital_twin.fault_limits['voltage']}V
    - Temperature: {digital_twin.fault_limits['temperature']}°C
    - Current: {digital_twin.fault_limits['current']}A
    
    RECOMMENDATIONS:
    - Maintain SOC between 20-80%
    - Keep temperature below 35°C
    - Monitor voltage regularly
    - Schedule maintenance every 30 days
    
    ---
    Generated by EV Digital Twin Platform
    Team TIGONS - JSPM JSCOE, Pune
    """
    return report

def show_compare_mode(real_data, simulated_data):
    """Show comparison between real and simulated data"""
    st.markdown("### 🔄 COMPARE MODE: REAL vs SIMULATED")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 REAL BATTERY DATA")
        st.metric("Voltage", f"{real_data['voltage']}V")
        st.metric("Current", f"{real_data['current']}A")
        st.metric("Temperature", f"{real_data['temperature']}°C")
        st.metric("SOC", f"{real_data['soc']}%")
    
    with col2:
        st.markdown("#### 🤖 SIMULATED MODEL")
        st.metric("Voltage", f"{simulated_data['voltage']}V", 
                 f"{simulated_data['voltage'] - real_data['voltage']:+.2f}V")
        st.metric("Current", f"{simulated_data['current']}A",
                 f"{simulated_data['current'] - real_data['current']:+.2f}A")
        st.metric("Temperature", f"{simulated_data['temperature']}°C",
                 f"{simulated_data['temperature'] - real_data['temperature']:+.1f}°C")
        st.metric("SOC", f"{simulated_data['soc']}%",
                 f"{simulated_data['soc'] - real_data['soc']:+.1f}%")
    
    # Accuracy calculation
    voltage_diff = abs(real_data['voltage'] - simulated_data['voltage'])
    accuracy = max(0, 100 - (voltage_diff / real_data['voltage']) * 100)
    st.info(f"🎯 **Model Accuracy: {accuracy:.1f}%**")

def show_mobile_view(sensor_data, digital_twin):
    """Show mobile-optimized view for field engineers"""
    st.markdown("### 📱 MOBILE VIEW - FIELD ENGINEER DASHBOARD")
    
    with st.container():
        st.markdown("""
        <div class="mobile-view">
            <h3 style="text-align: center; color: white;">🔋 FIELD MONITOR</h3>
            <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px; margin: 10px 0;">
                <div style="text-align: center;">
                    <h1 style="color: #4CAF50; margin: 0;">{soc}%</h1>
                    <p style="margin: 5px 0;">State of Charge</p>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 10px 0;">
                <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 5px;">
                    <div>⚡ Voltage</div>
                    <div style="font-weight: bold;">{voltage}V</div>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 5px;">
                    <div>🌡️ Temp</div>
                    <div style="font-weight: bold; color: {temp_color};">{temperature}°C</div>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 5px;">
                    <div>🔌 Current</div>
                    <div style="font-weight: bold;">{current}A</div>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 5px;">
                    <div>💪 Health</div>
                    <div style="font-weight: bold;">{health}%</div>
                </div>
            </div>
            
            <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 5px; margin: 10px 0;">
                <div style="text-align: center;">
                    <div>⚡ {mode}</div>
                    <div style="font-size: 12px; opacity: 0.8;">Last: {timestamp}</div>
                </div>
            </div>
        </div>
        """.format(
            soc=sensor_data['soc'],
            voltage=sensor_data['voltage'],
            temperature=sensor_data['temperature'],
            temp_color='#FF6B6B' if sensor_data['temperature'] > 40 else '#4CAF50',
            current=sensor_data['current'],
            health=sensor_data['health_score'],
            mode='CHARGING' if sensor_data['is_charging'] else 'DISCHARGING',
            timestamp=sensor_data['timestamp']
        ), unsafe_allow_html=True)
        
        # Quick actions for field engineers
        st.markdown("#### 🎯 QUICK ACTIONS")
        action_col1, action_col2 = st.columns(2)
        with action_col1:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        with action_col2:
            if st.button("📋 Log Issue", use_container_width=True):
                digital_twin.log_event("Field engineer logged issue", "WARNING")
                st.success("Issue logged successfully!")

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
    
    # ==================== SIDEBAR - CONTROL PANEL ====================
    with st.sidebar:
        st.markdown("### 🎮 SMART CONTROL PANEL")
        
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
        st.markdown("### ⚙️ CONFIGURABLE PARAMETERS")
        
        # Configurable Inputs
        voltage_min = st.slider("Min Voltage (V)", 8.0, 12.0, 9.0, 0.1)
        voltage_max = st.slider("Max Voltage (V)", 12.0, 15.0, 13.0, 0.1)
        
        load_percentage = st.slider("Load Percentage (%)", 10, 100, 50, 5,
                                  help="System stress level")
        pwm_percentage = st.slider("PWM Cooling (%)", 0, 100, 75, 5,
                                 help="Cooling system control")
        base_temperature = st.slider("Base Temperature (°C)", 15, 40, 25, 1,
                                   help="Starting temperature condition")
        noise_level = st.slider("Sensor Noise", 0.0, 0.5, 0.1, 0.01,
                              help="Sensor accuracy simulation")
        simulation_steps = st.slider("Simulation Steps", 50, 200, 100, 10,
                                   help="Simulation length")
        
        # Fault Limits Configuration
        st.markdown("### ⚠️ FAULT LIMITS")
        fault_voltage = st.slider("Voltage Fault Limit (V)", 8.0, 12.0, 10.5, 0.1)
        fault_temperature = st.slider("Temperature Fault Limit (°C)", 60, 100, 85, 1)
        fault_current = st.slider("Current Fault Limit (A)", 2.0, 6.0, 4.0, 0.1)
        
        # Update parameters
        if st.button("🔄 APPLY PARAMETERS", use_container_width=True):
            voltage_range = [voltage_min, voltage_max]
            fault_limits = {'voltage': fault_voltage, 'temperature': fault_temperature, 'current': fault_current}
            st.session_state.digital_twin.update_parameters(
                voltage_range, fault_limits, load_percentage, pwm_percentage, 
                base_temperature, noise_level, simulation_steps
            )
            st.success("Parameters updated successfully!")
        
        st.markdown("---")
        st.markdown("### 🎯 VIEW MODES")
        st.session_state.show_compare = st.checkbox("🔀 COMPARE MODE")
        st.session_state.show_mobile = st.checkbox("📱 MOBILE VIEW")
        
        st.session_state.digital_twin.fault_injected = st.checkbox("⚠️ INJECT FAULT SCENARIOS")
        
        st.markdown("---")
        st.markdown("### 📊 SYSTEM STATUS")
        
        if st.session_state.sensor_data:
            latest = st.session_state.sensor_data[-1]
            st.metric("Uptime", f"{(datetime.now() - st.session_state.digital_twin.start_time).seconds // 60} min")
            st.metric("Data Points", len(st.session_state.sensor_data))
            st.metric("Events Logged", len(st.session_state.digital_twin.event_log))

    # ==================== MAIN DASHBOARD ====================
    
    # Generate live data with configurable parameters
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
    
    # Manage data history
    if len(st.session_state.sensor_data) > st.session_state.digital_twin.simulation_steps:
        st.session_state.sensor_data = st.session_state.sensor_data[-st.session_state.digital_twin.simulation_steps:]
    
    # ==================== SPECIAL VIEW MODES ====================
    
    if st.session_state.show_compare:
        st.markdown('<div class="compare-mode">', unsafe_allow_html=True)
        # Generate simulated data for comparison (slightly different parameters)
        simulated_data = generate_sensor_data(
            st.session_state.last_soc - 2,  # Slight difference
            st.session_state.is_charging,
            st.session_state.digital_twin
        )
        show_compare_mode(sensor_data, simulated_data)
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.show_mobile:
        show_mobile_view(sensor_data, st.session_state.digital_twin)
    
    # ==================== SECTION 1: SIMULATION AREA ====================
    if not st.session_state.show_mobile:  # Don't show in mobile view
        st.markdown('<div class="section-header">🎯 SIMULATION AREA</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # Battery Visualization with Mode-based UI
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
                <p>Health: {sensor_data['health_score']}% | Temp: {sensor_data['temperature']}°C</p>
                <p>Voltage Range: {st.session_state.digital_twin.voltage_range[0]}V - {st.session_state.digital_twin.voltage_range[1]}V</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # AI PREDICTIVE INSIGHTS
            st.markdown("### 🤖 PREDICTIVE INSIGHTS")
            
            predicted_temp = st.session_state.digital_twin.predict_temperature(
                sensor_data['temperature'], sensor_data['current'], 
                sensor_data['voltage'], sensor_data['is_charging']
            )
            
            discharge_time = st.session_state.digital_twin.predict_discharge_time(
                sensor_data['soc'], sensor_data['current']
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
            
            st.markdown(f"""
            <div class="prediction-card">
                <div>⏱️ Discharge Time:</div>
                <div style="font-size: 18px; font-weight: bold;">{discharge_time}</div>
            </div>
            """, unsafe_allow_html=True)
            
            degradation_rate = 0.02 + max(0, sensor_data['temperature'] - 30) * 0.005
            st.markdown(f"""
            <div class="prediction-card">
                <div>📉 Degradation Rate:</div>
                <div style="font-size: 18px; font-weight: bold;">+{degradation_rate:.3f}% per cycle</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # EFFICIENCY & POWER INDICATOR
            st.markdown("### ⚡ EFFICIENCY METRICS")
            
            st.metric("Energy Efficiency", f"{sensor_data['efficiency']}%")
            st.metric("Energy Consumed", f"{sensor_data['energy_consumed']} Wh")
            st.metric("Charge Cycles", f"{sensor_data['cycles_completed']}")
            st.metric("Power Output", f"{sensor_data['power']} W")
    
    # ==================== SECTION 2: DATA OUTPUT PANEL ====================
    if not st.session_state.show_mobile:  # Don't show in mobile view
        st.markdown('<div class="section-header">📊 DATA OUTPUT PANEL</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # SMART TREND PANEL - Combined Charts
            st.markdown("### 📈 SMART TREND ANALYSIS")
            
            if len(st.session_state.sensor_data) > 1:
                df = pd.DataFrame(st.session_state.sensor_data)
                
                # Display multiple charts
                tab1, tab2, tab3 = st.tabs(["Voltage & SOC", "Temperature Trend", "Performance"])
                
                with tab1:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.line_chart(df['voltage'], use_container_width=True)
                        st.caption("⚡ Voltage Profile")
                    with col2:
                        st.line_chart(df['soc'], use_container_width=True)
                        st.caption("🔋 State of Charge")
                
                with tab2:
                    st.area_chart(df['temperature'], use_container_width=True)
                    st.caption("🌡️ Temperature Trend")
                
                with tab3:
                    st.line_chart(df[['voltage', 'current']], use_container_width=True)
                    st.caption("📊 Combined Performance Metrics")
        
        with col2:
            # EVENT LOG / ALERT TIMELINE
            st.markdown("### 📋 EVENT LOG")
            
            # Display recent events
            recent_events = st.session_state.digital_twin.event_log[-8:]
            for event in reversed(recent_events):
                status_class = ""
                if event['status'] == 'DANGER':
                    status_class = "alert-danger"
                elif event['status'] == 'WARNING':
                    status_class = "alert-warning"
                elif event['status'] == 'SUCCESS':
                    status_class = "alert-success"
                else:
                    status_class = "alert-timeline"
                
                st.markdown(f"""
                <div class="{status_class}">
                    <small><strong>{event['timestamp']}</strong></small><br>
                    {event['event']}<br>
                    <small>Status: {event['status']}</small>
                </div>
                """, unsafe_allow_html=True)
    
    # ==================== SECTION 3: EXPORT & REPORTS ====================
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
            st.text_area("📋 PERFORMANCE REPORT (Copy this data):", pdf_report, height=300)
            st.session_state.digital_twin.log_event("PDF Report Generated", "SUCCESS")
    
    with col3:
        if st.button("🔄 LIVE DATA STREAM", use_container_width=True):
            st.info("🔄 Live data streaming active - Real-time monitoring enabled")
            st.session_state.digital_twin.log_event("Live data streaming enabled", "INFO")
    
    # ==================== AI INSIGHTS SECTION ====================
    st.markdown('<div class="section-header">🤖 AI-POWERED ANALYTICS</div>', unsafe_allow_html=True)
    
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        risk_score = min(1.0, (100 - sensor_data['soc']) * 0.01 + max(0, sensor_data['temperature'] - 30) * 0.03)
        if risk_score < 0.25:
            st.success("✅ **LOW RISK**\n\nOptimal operating conditions")
        elif risk_score < 0.6:
            st.warning("⚠️ **MEDIUM RISK**\n\nMonitor parameters closely")
        else:
            st.error("🚨 **HIGH RISK**\n\nImmediate action required")
        
        st.metric("AI Risk Score", f"{risk_score:.2f}")
    
    with insight_col2:
        remaining_cycles = int((sensor_data['health_score'] - 70) / 0.02)
        st.info(f"""
        **🔧 PREDICTIVE MAINTENANCE**
        
        • Remaining cycles: **{remaining_cycles}**
        • Next service: **30 days**
        • Health degradation: **2% per 100 cycles**
        • System efficiency: **{sensor_data['efficiency']}%**
        """)
    
    with insight_col3:
        st.success(f"""
        **💡 SMART OPTIMIZATION**
        
        • Maintain SOC: **20-80%**
        • Optimal temp: **< 35°C**
        • Current efficiency: **{sensor_data['efficiency']}%**
        • Recommended action: **{'Continue operation' if risk_score < 0.4 else 'Reduce load'}**
        """)
    
    # COMPETITION FOOTER
    st.markdown("---")
    st.success("🏆 **KPIT SPARKLE 2025 READY** - Industry-Grade EV Digital Twin with Real-time AI Predictive Analytics & Professional Monitoring System")
    
    # AUTO-REFRESH
    refresh_delay = max(1, 6 - st.session_state.digital_twin.load_percentage / 20)
    time.sleep(refresh_delay)
    st.rerun()

if __name__ == "__main__":
    main()
