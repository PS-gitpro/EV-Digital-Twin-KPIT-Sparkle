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
    .mobile-container {
        background: #2c3e50;
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
    }
    .mobile-metric {
        background: rgba(255,255,255,0.1);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 5px;
    }
    .mobile-status {
        background: rgba(255,255,255,0.2);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

class EVDigitalTwin:
    def __init__(self):
        self.event_log = []
        self.fault_injected = False
        self.start_time = datetime.now()
        self.voltage_range = [9.0, 13.0]
        self.fault_limits = {'voltage': 10.5, 'temperature': 85, 'current': 4.0}
        self.load_percentage = 50
        self.pwm_percentage = 75
        self.base_temperature = 25
        self.noise_level = 0.1
        self.simulation_steps = 100
        self.log_event("Digital Twin Initialized", "SUCCESS")
    
    def update_parameters(self, voltage_range, fault_limits, load_pct, pwm_pct, base_temp, noise, steps):
        self.voltage_range = voltage_range
        self.fault_limits = fault_limits
        self.load_percentage = load_pct
        self.pwm_percentage = pwm_pct
        self.base_temperature = base_temp
        self.noise_level = noise
        self.simulation_steps = steps
        self.log_event(f"Parameters updated: Load={load_pct}%, PWM={pwm_pct}%, Temp={base_temp}°C", "INFO")
    
    def log_event(self, event, status="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.event_log.append({
            'timestamp': timestamp,
            'event': event,
            'status': status
        })
        if len(self.event_log) > 20:
            self.event_log = self.event_log[-20:]
    
    def predict_temperature(self, current_temp, current, voltage, is_charging):
        load_factor = self.load_percentage / 100.0
        cooling_factor = self.pwm_percentage / 100.0
        base_change = abs(current) * 0.002 * load_factor + (voltage - 3.7) * 0.5
        if is_charging:
            base_change += 0.8 * load_factor
        base_change *= (1.0 - cooling_factor * 0.3)
        predicted_temp = current_temp + base_change * 5
        return min(80, max(15, predicted_temp))
    
    def predict_discharge_time(self, soc, current):
        if current >= 0:
            return "N/A (Charging)"
        load_factor = self.load_percentage / 100.0
        discharge_rate = abs(current) / 100 * load_factor
        if discharge_rate == 0:
            return "∞"
        minutes_left = (soc / 100) / discharge_rate * 60
        return f"{minutes_left:.1f} mins"
    
    def simulate_fault(self, sensor_data):
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
    if digital_twin is None:
        digital_twin = EVDigitalTwin()
    
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
    
    voltage += np.random.normal(0, noise_level)
    current += np.random.normal(0, noise_level * 0.5)
    
    temp_increase = abs(current) * 0.12 * load_factor + (voltage - base_voltage_range[0]) * 0.8
    temperature = base_temp + temp_increase + np.random.uniform(-1, 1)
    
    health_degradation = (100 - new_soc) * 0.08 + max(0, temperature - 35) * 0.1
    health_score = max(45, 97 - health_degradation)
    
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

def show_mobile_view(sensor_data, digital_twin):
    """Show mobile-optimized view using only Streamlit components"""
    st.markdown("### 📱 MOBILE VIEW - FIELD ENGINEER DASHBOARD")
    
    # Mobile Container
    with st.container():
        st.markdown('<div class="mobile-container">', unsafe_allow_html=True)
        
        # Header
        st.markdown("#### 🔋 FIELD MONITOR")
        
        # SOC Display
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"<h1 style='color: #4CAF50; text-align: center; margin: 0;'>{sensor_data['soc']}%</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; margin: 0;'>State of Charge</p>", unsafe_allow_html=True)
        
        # Metrics Grid using Streamlit columns
        metric_col1, metric_col2 = st.columns(2)
        
        with metric_col1:
            # Voltage
            with st.container():
                st.markdown("⚡ Voltage")
                st.markdown(f"**{sensor_data['voltage']}V**")
            
            # Temperature with color coding
            with st.container():
                st.markdown("🌡️ Temperature")
                temp_color = "#FF6B6B" if sensor_data['temperature'] > 40 else "#4CAF50"
                st.markdown(f"<span style='color: {temp_color}; font-weight: bold;'>{sensor_data['temperature']}°C</span>", unsafe_allow_html=True)
        
        with metric_col2:
            # Current
            with st.container():
                st.markdown("🔌 Current")
                st.markdown(f"**{sensor_data['current']}A**")
            
            # Health
            with st.container():
                st.markdown("💪 Health")
                st.markdown(f"**{sensor_data['health_score']}%**")
        
        # Status Bar
        st.markdown("---")
        mode_text = "⚡ CHARGING" if sensor_data['is_charging'] else "🔋 DISCHARGING"
        mode_color = "#28a745" if sensor_data['is_charging'] else "#fd7e14"
        
        st.markdown(f"<div style='text-align: center; padding: 10px; background: {mode_color}; color: white; border-radius: 8px;'>"
                   f"<strong>{mode_text}</strong><br>"
                   f"<small>Last: {sensor_data['timestamp']}</small>"
                   f"</div>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick Actions for Field Engineers
        st.markdown("#### 🎯 QUICK ACTIONS")
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            if st.button("🔄 Refresh", use_container_width=True, key="mobile_refresh"):
                st.rerun()
        
        with action_col2:
            if st.button("📋 Log Issue", use_container_width=True, key="mobile_log"):
                digital_twin.log_event("Field engineer logged issue", "WARNING")
                st.success("Issue logged!")
        
        with action_col3:
            if st.button("⚙️ Settings", use_container_width=True, key="mobile_settings"):
                st.info("Opening settings...")

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
    
    # SIDEBAR
    with st.sidebar:
        st.markdown("### 🎮 CONTROL PANEL")
        
        mode = st.radio("**OPERATION MODE:**", ["⚡ FAST CHARGE", "🔋 SMART DISCHARGE"], index=0)
        new_charging_state = "CHARGE" in mode
        if new_charging_state != st.session_state.is_charging:
            st.session_state.is_charging = new_charging_state
            event = "Charging Started" if new_charging_state else "Discharging Started"
            st.session_state.digital_twin.log_event(event, "SUCCESS")
        
        st.markdown("---")
        st.markdown("### ⚙️ CONFIGURABLE PARAMETERS")
        
        voltage_min = st.slider("Min Voltage (V)", 8.0, 12.0, 9.0, 0.1)
        voltage_max = st.slider("Max Voltage (V)", 12.0, 15.0, 13.0, 0.1)
        load_percentage = st.slider("Load Percentage (%)", 10, 100, 50, 5)
        pwm_percentage = st.slider("PWM Cooling (%)", 0, 100, 75, 5)
        base_temperature = st.slider("Base Temperature (°C)", 15, 40, 25, 1)
        
        if st.button("🔄 APPLY PARAMETERS", use_container_width=True):
            voltage_range = [voltage_min, voltage_max]
            fault_limits = {'voltage': 10.5, 'temperature': 85, 'current': 4.0}
            st.session_state.digital_twin.update_parameters(
                voltage_range, fault_limits, load_percentage, pwm_percentage, 
                base_temperature, 0.1, 100
            )
            st.success("Parameters updated!")
        
        st.markdown("---")
        st.markdown("### 🎯 VIEW MODES")
        st.session_state.show_mobile = st.checkbox("📱 MOBILE VIEW")
        st.session_state.digital_twin.fault_injected = st.checkbox("⚠️ INJECT FAULT SCENARIOS")

    # GENERATE DATA
    sensor_data = generate_sensor_data(
        st.session_state.last_soc, 
        st.session_state.is_charging,
        st.session_state.digital_twin
    )
    st.session_state.last_soc = sensor_data['soc']
    sensor_data = st.session_state.digital_twin.simulate_fault(sensor_data)
    st.session_state.sensor_data.append(sensor_data)
    
    if len(st.session_state.sensor_data) > st.session_state.digital_twin.simulation_steps:
        st.session_state.sensor_data = st.session_state.sensor_data[-st.session_state.digital_twin.simulation_steps:]

    # MOBILE VIEW
    if st.session_state.show_mobile:
        show_mobile_view(sensor_data, st.session_state.digital_twin)
    else:
        # REGULAR DESKTOP VIEW
        st.markdown('<div class="section-header">🎯 SIMULATION DASHBOARD</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
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
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 📊 LIVE METRICS")
            st.metric("⚡ Voltage", f"{sensor_data['voltage']}V")
            st.metric("🔌 Current", f"{sensor_data['current']}A")
            st.metric("🌡️ Temperature", f"{sensor_data['temperature']}°C")
            st.metric("💪 Health", f"{sensor_data['health_score']}%")
        
        with col3:
            st.markdown("### ⚡ PERFORMANCE")
            st.metric("Power Output", f"{sensor_data['power']}W")
            st.metric("Efficiency", f"{sensor_data['efficiency']}%")
            st.metric("Energy Remaining", f"{sensor_data['energy_remaining']}kWh")
            st.metric("Cycles", f"{sensor_data['cycles_completed']}")

    # AUTO-REFRESH
    refresh_delay = max(1, 6 - st.session_state.digital_twin.load_percentage / 20)
    time.sleep(refresh_delay)
    st.rerun()

if __name__ == "__main__":
    main()
