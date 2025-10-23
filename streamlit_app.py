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
</style>
""", unsafe_allow_html=True)

class EVDigitalTwin:
    def __init__(self):
        self.event_log = []
        self.fault_injected = False
        self.start_time = datetime.now()
    
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
        base_change = abs(current) * 0.002 + (voltage - 3.7) * 0.5
        if is_charging:
            base_change += 0.8  # Charging generates more heat
        predicted_temp = current_temp + base_change * 5  # 5 minutes ahead
        return min(60, max(20, predicted_temp))
    
    def predict_discharge_time(self, soc, current):
        """Predict remaining discharge time"""
        if current >= 0:  # Charging
            return "N/A (Charging)"
        discharge_rate = abs(current) / 100  # Simplified model
        if discharge_rate == 0:
            return "∞"
        minutes_left = (soc / 100) / discharge_rate * 60
        return f"{minutes_left:.1f} mins"
    
    def simulate_fault(self, sensor_data):
        """Simulate various fault scenarios"""
        if not self.fault_injected:
            return sensor_data
        
        fault_type = np.random.choice(['voltage_drop', 'thermal_spike', 'sensor_failure'])
        
        if fault_type == 'voltage_drop':
            sensor_data['voltage'] *= 0.7  # 30% voltage drop
            self.log_event("⚠️ VOLTAGE DROP DETECTED", "DANGER")
        elif fault_type == 'thermal_spike':
            sensor_data['temperature'] += 15  # Sudden temperature spike
            self.log_event("🔥 THERMAL SPIKE DETECTED", "DANGER")
        elif fault_type == 'sensor_failure':
            sensor_data['current'] = 0  # Sensor failure
            self.log_event("🔧 CURRENT SENSOR FAILURE", "WARNING")
        
        return sensor_data

def generate_sensor_data(previous_soc=75, is_charging=True):
    """Generate realistic sensor data"""
    if is_charging:
        charge_rate = 1.2 + np.random.uniform(0, 0.8)
        new_soc = min(98, previous_soc + charge_rate)
        current = 28 + np.random.uniform(0, 12)
        voltage = 4.1 + (new_soc/100) * 0.2 + np.random.uniform(-0.05, 0.05)
    else:
        discharge_rate = 0.8 + np.random.uniform(0, 0.6)
        new_soc = max(15, previous_soc - discharge_rate)
        current = -25 - np.random.uniform(0, 15)
        voltage = 3.7 + (new_soc/100) * 0.3 + np.random.uniform(-0.05, 0.05)
    
    ambient_temp = 22
    temp_increase = abs(current) * 0.12 + (voltage - 3.7) * 5
    temperature = ambient_temp + temp_increase + np.random.uniform(-0.5, 0.5)
    
    health_degradation = (100 - new_soc) * 0.08 + max(0, temperature - 35) * 0.1
    health_score = max(45, 97 - health_degradation)
    
    # Calculate efficiency (simplified)
    efficiency = 90 + np.random.uniform(0, 5) - max(0, temperature - 30) * 0.5
    
    return {
        'voltage': round(voltage, 3),
        'current': round(current, 2),
        'temperature': round(temperature, 1),
        'soc': round(new_soc, 1),
        'health_score': round(health_score, 1),
        'timestamp': datetime.now().strftime("%H:%M:%S"),
        'is_charging': is_charging,
        'power': round(voltage * abs(current), 2),
        'energy_remaining': round(new_soc * 75 / 100, 1),
        'efficiency': round(efficiency, 1),
        'energy_consumed': round((100 - new_soc) * 0.75, 1),  # Simplified
        'cycles_completed': np.random.randint(1, 10)
    }

def create_csv_download(df, filename):
    """Create CSV download link"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Download CSV Report</a>'
    return href

def main():
    # Initialize digital twin
    if 'digital_twin' not in st.session_state:
        st.session_state.digital_twin = EVDigitalTwin()
        st.session_state.digital_twin.log_event("System Initialized", "SUCCESS")
    
    # Initialize session state
    if 'sensor_data' not in st.session_state:
        st.session_state.sensor_data = []
        st.session_state.last_soc = 65
        st.session_state.is_charging = True
        st.session_state.cycle_count = 0

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
        st.markdown("### ⚙️ ADVANCED SETTINGS")
        
        simulation_speed = st.slider("Simulation Speed", 1, 10, 5)
        data_history = st.slider("Data History Points", 20, 200, 100)
        
        # Fault Injection
        st.session_state.digital_twin.fault_injected = st.checkbox("⚠️ INJECT FAULT SCENARIOS", 
                                                                 help="Simulate real-world fault conditions")
        
        st.markdown("---")
        st.markdown("### 📊 SYSTEM STATUS")
        
        if st.session_state.sensor_data:
            latest = st.session_state.sensor_data[-1]
            st.metric("Uptime", f"{(datetime.now() - st.session_state.digital_twin.start_time).seconds // 60} min")
            st.metric("Data Points", len(st.session_state.sensor_data))
            st.metric("Events Logged", len(st.session_state.digital_twin.event_log))
        
        # System Communication Delay Simulation
        st.markdown("---")
        st.markdown("### 📡 COMMUNICATION")
        latency = np.random.randint(50, 300)
        st.info(f"📶 Telemetry Delay: {latency} ms")

    # ==================== MAIN DASHBOARD ====================
    
    # Generate live data
    sensor_data = generate_sensor_data(st.session_state.last_soc, st.session_state.is_charging)
    st.session_state.last_soc = sensor_data['soc']
    
    # Apply fault simulation if enabled
    sensor_data = st.session_state.digital_twin.simulate_fault(sensor_data)
    
    st.session_state.sensor_data.append(sensor_data)
    st.session_state.cycle_count += 1
    
    # Manage data history
    if len(st.session_state.sensor_data) > data_history:
        st.session_state.sensor_data = st.session_state.sensor_data[-data_history:]
    
    # ==================== SECTION 1: SIMULATION AREA ====================
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
    st.markdown('<div class="section-header">📊 DATA OUTPUT PANEL</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # SMART TREND PANEL - Combined Charts
        st.markdown("### 📈 SMART TREND ANALYSIS")
        
        if len(st.session_state.sensor_data) > 1:
            df = pd.DataFrame(st.session_state.sensor_data)
            
            # Create combined dataframe for dual axis chart
            trend_df = pd.DataFrame({
                'Time': range(len(df)),
                'Voltage': df['voltage'],
                'State of Charge': df['soc'],
                'Temperature': df['temperature']
            })
            
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
                st.caption("🌡️ Temperature Trend with Prediction Zone")
                
                # Add prediction curve
                future_points = 5
                if len(df) > 10:
                    last_temp = df['temperature'].iloc[-1]
                    predicted_temps = [last_temp + i * 0.5 for i in range(1, future_points + 1)]
                    st.line_chart(pd.DataFrame({'Predicted Temperature': predicted_temps}))
                    st.caption("🔮 Predicted Temperature (Next 5 cycles)")
            
            with tab3:
                st.line_chart(df[['voltage', 'current']], use_container_width=True)
                st.caption("📊 Combined Performance Metrics")
    
    with col2:
        # EVENT LOG / ALERT TIMELINE
        st.markdown("### 📋 EVENT LOG")
        
        # Display recent events
        recent_events = st.session_state.digital_twin.event_log[-8:]  # Last 8 events
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
        if st.button("📊 GENERATE PERFORMANCE REPORT", use_container_width=True):
            if len(st.session_state.sensor_data) > 1:
                df = pd.DataFrame(st.session_state.sensor_data)
                st.markdown(create_csv_download(df, "battery_performance_report.csv"), unsafe_allow_html=True)
                st.session_state.digital_twin.log_event("Performance Report Generated", "SUCCESS")
    
    with col2:
        if st.button("🔄 COMPARE MODE", use_container_width=True):
            st.info("🔄 Comparison Mode: Real vs Simulated Data")
            # This would show side-by-side comparison in a real implementation
    
    with col3:
        if st.button("📱 MOBILE VIEW", use_container_width=True):
            st.info("📱 Mobile-optimized view for field engineers")
    
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
    refresh_delay = max(1, 6 - simulation_speed)
    time.sleep(refresh_delay)
    st.rerun()

if __name__ == "__main__":
    main()
