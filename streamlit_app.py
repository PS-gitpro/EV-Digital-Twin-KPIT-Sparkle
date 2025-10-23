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

# Custom CSS for professional look - NO EXTERNAL DEPENDENCIES
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem !important;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 5px;
    }
    .battery-container {
        text-align: center;
        margin: 20px;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        color: white;
    }
    .thermal-cool { background: #4FC3F7 !important; }
    .thermal-warm { background: #FFB74D !important; }
    .thermal-hot { background: #F44336 !important; }
</style>
""", unsafe_allow_html=True)

def create_battery_animation(soc, is_charging=True, health_score=85):
    """Create battery visualization using pure HTML/CSS"""
    
    # Determine colors based on health
    if health_score >= 80:
        primary_color = "#4CAF50"
    elif health_score >= 60:
        primary_color = "#FF9800" 
    else:
        primary_color = "#F44336"
    
    battery_html = f"""
    <div class="battery-container">
        <div style="width: 120px; height: 200px; border: 4px solid #fff; border-radius: 12px; 
                    margin: 0 auto; position: relative; background: linear-gradient(to top, {primary_color} {soc}%, transparent {soc}%); 
                    box-shadow: inset 0 0 20px rgba(0,0,0,0.3);">
            
            <!-- Battery Cap -->
            <div style="width: 30px; height: 12px; background: #fff; position: absolute; 
                        top: -16px; left: 45px; border-radius: 4px 4px 0 0;"></div>
            
            <!-- Charge Level -->
            <div style="position: absolute; bottom: 15px; width: 100%; text-align: center; 
                        color: #fff; font-weight: bold; font-size: 18px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">
                {soc}%
            </div>
        </div>
        
        <div style="margin-top: 15px; font-weight: bold; font-size: 16px;">
            {'⚡ CHARGING' if is_charging else '🔋 DISCHARGING'}
        </div>
        <div style="margin-top: 5px; font-size: 12px; opacity: 0.8;">
            Health: {health_score}% | Updated: {datetime.now().strftime('%H:%M:%S')}
        </div>
    </div>
    """
    return battery_html

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

def get_thermal_class(temperature):
    """Get CSS class for thermal indicator"""
    if temperature < 30:
        return "thermal-cool"
    elif temperature < 45:
        return "thermal-warm"
    else:
        return "thermal-hot"

def main():
    # Professional Header
    st.markdown('<h1 class="main-header">🔋 EV DIGITAL TWIN PLATFORM</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center; color: #ff6b6b;">🐅 Team TIGONS | KPIT Sparkle 2025</h3>', unsafe_allow_html=True)
    st.markdown("**Jayawantrao Sawant College of Engineering, Pune** | **Real-time EV Battery Monitoring**")
    
    # Initialize session state
    if 'sensor_data' not in st.session_state:
        st.session_state.sensor_data = []
        st.session_state.last_soc = 65
        st.session_state.is_charging = True

    # Enhanced Sidebar
    with st.sidebar:
        st.markdown("### 🎮 CONTROL PANEL")
        
        # Mode Selection
        mode = st.radio(
            "**OPERATION MODE:**",
            ["⚡ FAST CHARGE", "🔋 NORMAL DISCHARGE"],
            index=0
        )
        st.session_state.is_charging = (mode == "⚡ FAST CHARGE")
        
        st.markdown("### ⚙️ SETTINGS")
        simulation_speed = st.slider("Simulation Speed", 1, 10, 5)
        
        st.markdown("---")
        st.success("🚀 **LIVE STREAMING ACTIVE**")
        st.info("No external dependencies - Pure Streamlit Power!")
    
    # Status Header
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("<div class='metric-card'>🟢 SYSTEM ONLINE</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='metric-card'>📊 LIVE DATA</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='metric-card'>🔋 BATTERY ACTIVE</div>", unsafe_allow_html=True)
    with col4:
        st.markdown("<div class='metric-card'>🎯 COMPETITION READY</div>", unsafe_allow_html=True)
    
    # Main Dashboard
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🔋 LIVE BATTERY MONITOR")
        
        # Generate live data
        sensor_data = generate_sensor_data(
            st.session_state.last_soc, 
            st.session_state.is_charging
        )
        st.session_state.last_soc = sensor_data['soc']
        st.session_state.sensor_data.append(sensor_data)
        
        # Keep data history manageable
        if len(st.session_state.sensor_data) > 50:
            st.session_state.sensor_data = st.session_state.sensor_data[-50:]
        
        # Battery Animation
        battery_html = create_battery_animation(
            int(sensor_data['soc']), 
            st.session_state.is_charging,
            sensor_data['health_score']
        )
        st.markdown(battery_html, unsafe_allow_html=True)
        
        # Thermal Indicator
        thermal_class = get_thermal_class(sensor_data['temperature'])
        st.markdown(f"""
        <div class="battery-container {thermal_class}">
            <div style="font-size: 24px;">🌡️</div>
            <div style="font-size: 20px; font-weight: bold;">{sensor_data['temperature']}°C</div>
            <div style="font-size: 12px;">THERMAL STATUS</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📊 REAL-TIME METRICS")
        
        # Metrics in a nice grid
        m1, m2 = st.columns(2)
        with m1:
            st.metric("⚡ Voltage", f"{sensor_data['voltage']}V", 
                     delta=f"{sensor_data['voltage']-3.8:+.2f}V")
            st.metric("🌡️ Temperature", f"{sensor_data['temperature']}°C",
                     delta=f"{'Hot' if sensor_data['temperature'] > 35 else 'Optimal'}")
            
        with m2:
            st.metric("🔌 Current", f"{sensor_data['current']}A",
                     delta=f"{'Charging' if sensor_data['current'] > 0 else 'Discharging'}")
            st.metric("💪 Health", f"{sensor_data['health_score']}%",
                     delta="-0.1%", delta_color="inverse")
        
        # Additional specs
        st.markdown("#### 🔧 TECHNICAL SPECIFICATIONS")
        spec_col1, spec_col2 = st.columns(2)
        with spec_col1:
            st.write(f"**Power Output:** {sensor_data['power']}W")
            st.write(f"**Cycle Mode:** {'⚡ Charging' if sensor_data['is_charging'] else '🔋 Discharging'}")
        with spec_col2:
            st.write(f"**Last Update:** {sensor_data['timestamp']}")
            st.write(f"**Data Points:** {len(st.session_state.sensor_data)}")
        
        st.markdown("---")
        st.markdown("### 📈 PERFORMANCE TRENDS")
        
        # Real-time charts using Streamlit's built-in charts
        if len(st.session_state.sensor_data) > 1:
            df = pd.DataFrame(st.session_state.sensor_data)
            
            # SOC Trend
            st.line_chart(df['soc'], use_container_width=True)
            st.caption("State of Charge Trend")
            
            # Voltage Trend
            st.line_chart(df['voltage'], use_container_width=True)
            st.caption("Voltage Profile")
    
    # AI Insights Section
    st.markdown("---")
    st.markdown("### 🤖 AI-POWERED INSIGHTS")
    
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        risk_score = min(1.0, (100 - sensor_data['soc']) * 0.01 + (sensor_data['temperature'] - 25) * 0.02)
        if risk_score < 0.3:
            st.success("✅ **LOW RISK**\n\nOptimal operating conditions")
        elif risk_score < 0.7:
            st.warning("⚠️ **MEDIUM RISK**\n\nMonitor temperature closely")
        else:
            st.error("🚨 **HIGH RISK**\n\nReduce load immediately")
    
    with insight_col2:
        st.info("💡 **OPTIMIZATION TIPS**\n\n• Maintain 20-80% SOC\n• Avoid fast charging when hot\n• Regular maintenance cycles")
    
    with insight_col3:
        remaining_cycles = int((sensor_data['health_score'] - 70) / 0.02)
        st.info(f"📅 **PREDICTIVE MAINTENANCE**\n\n• Remaining cycles: {remaining_cycles}\n• Next service: 30 days\n• Degradation rate: 2%/100cyc")
    
    # Competition Ready Footer
    st.markdown("---")
    st.success("🎯 **KPIT SPARKLE 2025 READY** - This project demonstrates real-time EV battery monitoring with AI insights using only Streamlit's built-in capabilities!")
    
    # Auto-refresh
    refresh_time = max(1, 6 - simulation_speed)
    time.sleep(refresh_time)
    st.rerun()

if __name__ == "__main__":
    main()
