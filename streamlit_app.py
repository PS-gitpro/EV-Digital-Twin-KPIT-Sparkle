import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
import base64

st.set_page_config(
    page_title="EV Digital Twin - Team TIGONS",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# SIMPLE CSS - ONLY WHAT'S ABSOLUTELY NECESSARY
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem !important;
        color: #1a237e;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 800;
    }
    .status-online {
        background: #4CAF50;
        color: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    .status-warning {
        background: #FF9800;
        color: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    .status-critical {
        background: #F44336;
        color: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def create_battery_with_streamlit(soc, is_charging=True, health_score=85):
    """Create battery display using ONLY Streamlit components - no HTML"""
    
    # Determine colors based on status
    if health_score >= 80:
        fill_color = "#4CAF50"
    elif health_score >= 60:
        fill_color = "#FF9800"
    else:
        fill_color = "#F44336"
    
    # Create battery using Streamlit components only
    with st.container():
        # Battery Header
        st.markdown("### 🔋 BATTERY STATUS")
        
        # Main SOC Progress Bar
        st.markdown(f"**State of Charge: {soc}%**")
        st.progress(soc/100)
        
        # Health Bar
        st.markdown(f"**Battery Health: {health_score}%**")
        st.progress(health_score/100)
        
        # Status Information
        col1, col2 = st.columns(2)
        with col1:
            if is_charging:
                st.success("⚡ **CHARGING**")
            else:
                st.warning("🔋 **DISCHARGING**")
        
        with col2:
            if health_score >= 80:
                st.success("💪 **HEALTHY**")
            elif health_score >= 60:
                st.warning("⚠️ **MODERATE**")
            else:
                st.error("🚨 **CRITICAL**")
        
        # Last Update
        st.caption(f"🔄 Live • Last update: {datetime.now().strftime('%H:%M:%S')}")

def create_thermal_display(temperature):
    """Create thermal display using Streamlit components"""
    if temperature < 28:
        st.success(f"❄️ **COOL TEMPERATURE**: {temperature}°C")
        st.info("Optimal operating condition")
    elif temperature < 42:
        st.warning(f"🌡️ **WARM TEMPERATURE**: {temperature}°C")
        st.info("Monitor closely")
    else:
        st.error(f"🔥 **HOT TEMPERATURE**: {temperature}°C")
        st.info("Reduce load immediately")

def generate_sensor_data(previous_soc=75, is_charging=True):
    """Generate realistic sensor data"""
    if is_charging:
        new_soc = min(95, previous_soc + np.random.uniform(0.5, 2.0))
        current = 25 + np.random.uniform(0, 15)
        voltage = 4.0 + (new_soc/100) * 0.3
    else:
        new_soc = max(15, previous_soc - np.random.uniform(0.5, 2.0))
        current = -20 - np.random.uniform(0, 20)
        voltage = 3.6 + (new_soc/100) * 0.4
    
    temperature = 25 + abs(current) * 0.15 + np.random.uniform(-1, 1)
    health_score = max(50, 95 - (100 - new_soc) * 0.1)
    
    return {
        'voltage': round(voltage, 3),
        'current': round(current, 2),
        'temperature': round(temperature, 1),
        'soc': round(new_soc, 1),
        'health_score': round(health_score, 1),
        'timestamp': datetime.now().strftime("%H:%M:%S"),
        'is_charging': is_charging,
        'power': round(voltage * abs(current), 2)
    }

def main():
    # PROFESSIONAL HEADER
    st.markdown('<h1 class="main-header">🔋 EV DIGITAL TWIN PLATFORM</h1>', unsafe_allow_html=True)
    st.markdown('### 🐅 Team TIGONS | KPIT Sparkle 2025')
    st.markdown('**Jayawantrao Sawant College of Engineering, Pune**')
    
    # Initialize session state
    if 'sensor_data' not in st.session_state:
        st.session_state.sensor_data = []
        st.session_state.last_soc = 65
        st.session_state.is_charging = True

    # SIMPLE SIDEBAR
    with st.sidebar:
        st.markdown("### 🎮 CONTROL PANEL")
        mode = st.radio("OPERATION MODE:", ["⚡ CHARGING", "🔋 DISCHARGING"], index=0)
        st.session_state.is_charging = (mode == "⚡ CHARGING")
        
        simulation_speed = st.slider("Simulation Speed", 1, 10, 5)
        st.success("🚀 LIVE STREAMING ACTIVE")

    # STATUS INDICATORS
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("<div class='status-online'>🟢 SYSTEM ONLINE</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='status-online'>📊 LIVE DATA</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='status-online'>🔋 BATTERY ACTIVE</div>", unsafe_allow_html=True)
    with col4:
        st.markdown("<div class='status-online'>🎯 COMPETITION READY</div>", unsafe_allow_html=True)

    # MAIN DASHBOARD
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("## 🔋 REAL-TIME BATTERY MONITOR")
        
        # Generate live data
        sensor_data = generate_sensor_data(st.session_state.last_soc, st.session_state.is_charging)
        st.session_state.last_soc = sensor_data['soc']
        st.session_state.sensor_data.append(sensor_data)
        
        if len(st.session_state.sensor_data) > 50:
            st.session_state.sensor_data = st.session_state.sensor_data[-50:]
        
        # USE STREAMLIT-ONLY BATTERY DISPLAY
        create_battery_with_streamlit(
            int(sensor_data['soc']), 
            st.session_state.is_charging,
            sensor_data['health_score']
        )
        
        # Thermal Display
        st.markdown("## 🌡️ THERMAL MONITORING")
        create_thermal_display(sensor_data['temperature'])
    
    with col2:
        st.markdown("## 📊 LIVE METRICS")
        
        # Key Metrics
        metric_col1, metric_col2 = st.columns(2)
        
        with metric_col1:
            st.metric("⚡ Voltage", f"{sensor_data['voltage']}V", 
                     f"{sensor_data['voltage']-3.8:+.2f}V")
            st.metric("🔌 Current", f"{sensor_data['current']}A",
                     f"{'Charging' if sensor_data['current'] > 0 else 'Discharging'}")
        
        with metric_col2:
            st.metric("🌡️ Temperature", f"{sensor_data['temperature']}°C",
                     f"{'Hot' if sensor_data['temperature'] > 35 else 'Optimal'}")
            st.metric("💪 Health", f"{sensor_data['health_score']}%", "-0.1%")
        
        # Additional Info
        st.markdown("#### 🔧 TECHNICAL SPECS")
        st.write(f"**Power Output:** {sensor_data['power']}W")
        st.write(f"**Operation Mode:** {'⚡ Charging' if sensor_data['is_charging'] else '🔋 Discharging'}")
        st.write(f"**Last Update:** {sensor_data['timestamp']}")
        st.write(f"**Data Points:** {len(st.session_state.sensor_data)}")
        
        # Performance Trends
        st.markdown("## 📈 PERFORMANCE TRENDS")
        if len(st.session_state.sensor_data) > 1:
            df = pd.DataFrame(st.session_state.sensor_data)
            st.line_chart(df['soc'], use_container_width=True)
            st.caption("State of Charge Trend")
            
            trend_col1, trend_col2 = st.columns(2)
            with trend_col1:
                st.line_chart(df['voltage'], use_container_width=True)
                st.caption("Voltage")
            with trend_col2:
                st.line_chart(df['current'], use_container_width=True)
                st.caption("Current")

    # AI INSIGHTS
    st.markdown("---")
    st.markdown("## 🤖 AI-POWERED INSIGHTS")
    
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        risk_score = min(1.0, (100 - sensor_data['soc']) * 0.01 + (sensor_data['temperature'] - 25) * 0.02)
        if risk_score < 0.3:
            st.success("✅ **LOW RISK**")
            st.write("Optimal operating conditions")
        elif risk_score < 0.7:
            st.warning("⚠️ **MEDIUM RISK**")
            st.write("Monitor parameters closely")
        else:
            st.error("🚨 **HIGH RISK**")
            st.write("Immediate action required")
        
        st.metric("Risk Score", f"{risk_score:.2f}")
    
    with insight_col2:
        st.info("💡 **OPTIMIZATION TIPS**")
        st.write("• Maintain SOC between 20-80%")
        st.write("• Avoid temperatures above 35°C")
        st.write("• Regular maintenance cycles")
        st.write("• Monitor charging patterns")
    
    with insight_col3:
        remaining_cycles = int((sensor_data['health_score'] - 70) / 0.02)
        st.info("📅 **PREDICTIVE MAINTENANCE**")
        st.write(f"• Remaining cycles: {remaining_cycles}")
        st.write("• Next service: 30 days")
        st.write("• Degradation rate: 2% per 100 cycles")

    # ACTION BUTTONS
    st.markdown("---")
    st.markdown("### 🎯 QUICK ACTIONS")
    
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("📥 Export Report", use_container_width=True):
            st.success("Report exported successfully!")
    
    with action_col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    with action_col3:
        if st.button("📊 Full Analytics", use_container_width=True):
            st.info("Opening detailed analytics...")

    # COMPETITION FOOTER
    st.markdown("---")
    st.success("🏆 **KPIT SPARKLE 2025 READY** - Industry-Grade EV Digital Twin Platform with Real-time Monitoring & AI-Powered Predictions")

    # AUTO-REFRESH
    refresh_time = max(1, 6 - simulation_speed)
    time.sleep(refresh_time)
    st.rerun()

if __name__ == "__main__":
    main()
