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

# PROFESSIONAL CSS WITH MODERN DESIGN
st.markdown("""
<style>
    /* Main Header */
    .main-header {
        font-size: 2.8rem !important;
        color: #1a237e;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 800;
        background: linear-gradient(45deg, #1a237e, #5c6bc0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Battery Container */
    .battery-outer {
        width: 180px;
        height: 320px;
        border: 4px solid #fff;
        border-radius: 20px;
        margin: 0 auto;
        position: relative;
        background: rgba(255,255,255,0.1);
        box-shadow: inset 0 0 30px rgba(0,0,0,0.4), 0 8px 25px rgba(0,0,0,0.3);
    }
    
    .battery-cap {
        width: 50px;
        height: 15px;
        background: #fff;
        position: absolute;
        top: -19px;
        left: 65px;
        border-radius: 8px 8px 0 0;
        box-shadow: 0 -3px 15px rgba(0,0,0,0.2);
    }
    
    .battery-fill {
        position: absolute;
        bottom: 0;
        width: 100%;
        border-radius: 16px;
        transition: height 1s ease;
    }
    
    .battery-percentage {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: #fff;
        font-weight: bold;
        font-size: 28px;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.5);
    }
    
    .battery-health-bar {
        position: absolute;
        bottom: 15px;
        left: 10%;
        width: 80%;
        height: 8px;
        background: rgba(255,255,255,0.3);
        border-radius: 4px;
        overflow: hidden;
    }
    
    .battery-health-fill {
        height: 100%;
        border-radius: 4px;
    }
    
    @keyframes pulse-glow {
        0% { box-shadow: 0 0 20px rgba(76, 175, 80, 0.6); }
        50% { box-shadow: 0 0 40px rgba(76, 175, 80, 0.6); }
        100% { box-shadow: 0 0 20px rgba(76, 175, 80, 0.6); }
    }
    
    .pulse-animation {
        animation: pulse-glow 2s infinite;
    }
</style>
""", unsafe_allow_html=True)

def create_battery_display(soc, is_charging=True, health_score=85):
    """Create battery display using Streamlit components instead of raw HTML"""
    
    # Determine colors based on status
    if health_score >= 80:
        fill_color = "#4CAF50"
    elif health_score >= 60:
        fill_color = "#FF9800"
    else:
        fill_color = "#F44336"
    
    # Create battery using Streamlit columns and metrics
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Battery visualization using progress bars and metrics
            st.markdown(f"""
            <div style="text-align: center; margin: 20px; padding: 25px; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 20px; color: white; border: 2px solid rgba(255,255,255,0.2);">
                <div style="font-size: 24px; margin-bottom: 15px;">🔋 BATTERY STATUS</div>
                
                <!-- SOC Progress Bar -->
                <div style="background: rgba(255,255,255,0.2); border-radius: 10px; padding: 5px; margin: 10px 0;">
                    <div style="background: {fill_color}; width: {soc}%; height: 30px; border-radius: 8px; 
                                display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                        {soc}%
                    </div>
                </div>
                
                <!-- Health Bar -->
                <div style="background: rgba(255,255,255,0.2); border-radius: 5px; padding: 3px; margin: 10px 0;">
                    <div style="background: {fill_color}; width: {health_score}%; height: 8px; border-radius: 4px;"></div>
                </div>
                
                <div style="display: flex; justify-content: space-around; margin-top: 15px;">
                    <div>
                        <div style="font-size: 12px; opacity: 0.8;">MODE</div>
                        <div style="font-size: 16px; font-weight: bold;">
                            {'⚡ CHARGING' if is_charging else '🔋 DISCHARGING'}
                        </div>
                    </div>
                    <div>
                        <div style="font-size: 12px; opacity: 0.8;">HEALTH</div>
                        <div style="font-size: 16px; font-weight: bold;">{health_score}%</div>
                    </div>
                </div>
                
                <div style="margin-top: 10px; font-size: 12px; opacity: 0.7;">
                    🔄 Live • {datetime.now().strftime('%H:%M:%S')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add pulse effect for charging
            if is_charging and soc < 95:
                st.markdown("""
                <style>
                    @keyframes pulse {
                        0% { transform: scale(1); }
                        50% { transform: scale(1.02); }
                        100% { transform: scale(1); }
                    }
                    .charging-pulse {
                        animation: pulse 2s infinite;
                    }
                </style>
                <div class="charging-pulse"></div>
                """, unsafe_allow_html=True)

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
    st.markdown('<h3 style="text-align: center; color: #5c6bc0; margin-bottom: 2rem;">🐅 Team TIGONS | KPIT Sparkle 2025</h3>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'sensor_data' not in st.session_state:
        st.session_state.sensor_data = []
        st.session_state.last_soc = 65
        st.session_state.is_charging = True

    # SIDEBAR CONTROLS
    with st.sidebar:
        st.markdown("### 🎮 CONTROL PANEL")
        mode = st.radio("OPERATION MODE:", ["⚡ CHARGING", "🔋 DISCHARGING"], index=0)
        st.session_state.is_charging = (mode == "⚡ CHARGING")
        
        simulation_speed = st.slider("Simulation Speed", 1, 10, 5)
        st.success("🚀 LIVE STREAMING ACTIVE")

    # MAIN DASHBOARD
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🔋 REAL-TIME BATTERY MONITOR")
        
        # Generate live data
        sensor_data = generate_sensor_data(st.session_state.last_soc, st.session_state.is_charging)
        st.session_state.last_soc = sensor_data['soc']
        st.session_state.sensor_data.append(sensor_data)
        
        if len(st.session_state.sensor_data) > 50:
            st.session_state.sensor_data = st.session_state.sensor_data[-50:]
        
        # Use the fixed battery display
        create_battery_display(
            int(sensor_data['soc']), 
            st.session_state.is_charging,
            sensor_data['health_score']
        )
        
        # Thermal indicator
        thermal_color = "#4FC3F7" if sensor_data['temperature'] < 30 else "#FFB74D" if sensor_data['temperature'] < 45 else "#F44336"
        st.markdown(f"""
        <div style="text-align: center; margin: 15px; padding: 15px; background: {thermal_color}; 
                    border-radius: 10px; color: white; font-weight: bold;">
            <div style="font-size: 24px;">🌡️</div>
            <div>{sensor_data['temperature']}°C</div>
            <div style="font-size: 12px;">THERMAL STATUS</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📊 LIVE METRICS")
        
        # Metrics in columns
        m1, m2 = st.columns(2)
        with m1:
            st.metric("⚡ Voltage", f"{sensor_data['voltage']}V", f"{sensor_data['voltage']-3.8:+.2f}V")
            st.metric("🌡️ Temperature", f"{sensor_data['temperature']}°C", 
                     f"{'Hot' if sensor_data['temperature'] > 35 else 'Optimal'}")
        with m2:
            st.metric("🔌 Current", f"{sensor_data['current']}A",
                     f"{'Charging' if sensor_data['current'] > 0 else 'Discharging'}")
            st.metric("💪 Health", f"{sensor_data['health_score']}%", "-0.1%", delta_color="inverse")
        
        # Performance trends
        st.markdown("### 📈 PERFORMANCE TRENDS")
        if len(st.session_state.sensor_data) > 1:
            df = pd.DataFrame(st.session_state.sensor_data)
            st.line_chart(df['soc'], use_container_width=True)
            st.caption("State of Charge Trend")
            
            col1, col2 = st.columns(2)
            with col1:
                st.line_chart(df['voltage'], use_container_width=True)
                st.caption("Voltage")
            with col2:
                st.line_chart(df['current'], use_container_width=True)
                st.caption("Current")
    
    # AI INSIGHTS
    st.markdown("---")
    st.markdown("### 🤖 AI-POWERED INSIGHTS")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        risk_score = min(1.0, (100 - sensor_data['soc']) * 0.01 + (sensor_data['temperature'] - 25) * 0.02)
        if risk_score < 0.3:
            st.success("✅ **LOW RISK**\n\nOptimal conditions")
        elif risk_score < 0.7:
            st.warning("⚠️ **MEDIUM RISK**\n\nMonitor closely")
        else:
            st.error("🚨 **HIGH RISK**\n\nTake action")
    
    with col2:
        st.info("💡 **OPTIMIZATION**\n\n• Maintain 20-80% SOC\n• Optimal temperature\n• Regular maintenance")
    
    with col3:
        remaining = int((sensor_data['health_score'] - 70) / 0.02)
        st.info(f"📅 **MAINTENANCE**\n\n• Cycles left: {remaining}\n• Next service: 30 days")
    
    # Auto-refresh
    refresh_time = max(1, 6 - simulation_speed)
    time.sleep(refresh_time)
    st.rerun()

if __name__ == "__main__":
    main()
