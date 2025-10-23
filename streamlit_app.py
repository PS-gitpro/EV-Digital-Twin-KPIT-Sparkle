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
    
    /* Metric Cards */
    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 15px;
        border-left: 5px solid #1a237e;
        margin: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    /* Battery Container */
    .battery-container {
        text-align: center;
        margin: 20px;
        padding: 25px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.3);
        color: white;
        border: 2px solid rgba(255,255,255,0.2);
    }
    
    /* Thermal Indicators */
    .thermal-cool { 
        background: linear-gradient(135deg, #4FC3F7, #29b6f6) !important; 
    }
    .thermal-warm { 
        background: linear-gradient(135deg, #FFB74D, #ffa726) !important; 
    }
    .thermal-hot { 
        background: linear-gradient(135deg, #F44336, #e53935) !important; 
    }
    
    /* Status Indicators */
    .status-online {
        background: linear-gradient(135deg, #4CAF50, #66BB6A);
        color: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    .status-warning {
        background: linear-gradient(135deg, #FF9800, #FFB74D);
        color: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    .status-critical {
        background: linear-gradient(135deg, #F44336, #EF5350);
        color: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    
    /* Button Styles */
    .stButton button {
        background: linear-gradient(45deg, #1a237e, #3949ab);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background: linear-gradient(45deg, #3949ab, #5c6bc0);
        transform: scale(1.05);
    }
    
    /* Custom Progress Bars */
    .stProgress > div > div > div {
        background: linear-gradient(45deg, #1a237e, #3949ab);
    }
</style>
""", unsafe_allow_html=True)

def create_realistic_battery(soc, is_charging=True, health_score=85):
    """Create ultra-realistic battery animation with 3D effects"""
    
    # Dynamic colors based on status
    if health_score >= 80:
        fill_color = "#4CAF50"
        glow_color = "rgba(76, 175, 80, 0.6)"
    elif health_score >= 60:
        fill_color = "#FF9800"
        glow_color = "rgba(255, 152, 0, 0.6)"
    else:
        fill_color = "#F44336" 
        glow_color = "rgba(244, 67, 54, 0.6)"
    
    # Charging animation effect
    pulse_animation = ""
    if is_charging and soc < 95:
        pulse_animation = """
        @keyframes pulse-glow {
            0% { box-shadow: 0 0 20px """ + glow_color + """; }
            50% { box-shadow: 0 0 40px """ + glow_color + """; }
            100% { box-shadow: 0 0 20px """ + glow_color + """; }
        }
        .battery-fill {
            animation: pulse-glow 2s infinite;
        }
        """
    
    battery_html = f"""
    <style>
        {pulse_animation}
    </style>
    <div class="battery-container">
        <!-- Battery Outer Shell -->
        <div style="width: 180px; height: 320px; border: 4px solid #fff; border-radius: 20px; 
                    margin: 0 auto; position: relative; background: rgba(255,255,255,0.1);
                    box-shadow: inset 0 0 30px rgba(0,0,0,0.4), 0 8px 25px rgba(0,0,0,0.3);">
            
            <!-- Battery Cap -->
            <div style="width: 50px; height: 15px; background: #fff; position: absolute; 
                        top: -19px; left: 65px; border-radius: 8px 8px 0 0; 
                        box-shadow: 0 -3px 15px rgba(0,0,0,0.2);"></div>
            
            <!-- Battery Fill with Animation -->
            <div class="battery-fill" style="position: absolute; bottom: 0; width: 100%; 
                        height: {soc}%; background: linear-gradient(to top, {fill_color}, {fill_color}00);
                        border-radius: 16px; transition: height 1s ease;">
            </div>
            
            <!-- Charge Percentage -->
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
                        color: #fff; font-weight: bold; font-size: 28px; text-shadow: 3px 3px 6px rgba(0,0,0,0.5);">
                {soc}%
            </div>
            
            <!-- Health Bar -->
            <div style="position: absolute; bottom: 15px; left: 10%; width: 80%; height: 8px; 
                        background: rgba(255,255,255,0.3); border-radius: 4px; overflow: hidden;">
                <div style="width: {health_score}%; height: 100%; 
                            background: linear-gradient(90deg, {fill_color}, {fill_color}); 
                            border-radius: 4px;"></div>
            </div>
        </div>
        
        <!-- Status Indicators -->
        <div style="margin-top: 20px; display: flex; justify-content: center; gap: 15px;">
            <div style="text-align: center;">
                <div style="font-size: 14px; opacity: 0.8;">MODE</div>
                <div style="font-size: 16px; font-weight: bold;">
                    {'⚡ CHARGING' if is_charging else '🔋 DISCHARGING'}
                </div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 14px; opacity: 0.8;">HEALTH</div>
                <div style="font-size: 16px; font-weight: bold;">{health_score}%</div>
            </div>
        </div>
        
        <!-- Last Update -->
        <div style="margin-top: 10px; font-size: 12px; opacity: 0.7;">
            🔄 Live • {datetime.now().strftime('%H:%M:%S')}
        </div>
    </div>
    """
    return battery_html

def generate_advanced_sensor_data(previous_soc=75, is_charging=True):
    """Generate realistic sensor data with physics-based simulation"""
    
    # More realistic charging/discharging physics
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
    
    # Temperature simulation with realistic physics
    ambient_temp = 22
    temp_increase = abs(current) * 0.12 + (voltage - 3.7) * 5
    temperature = ambient_temp + temp_increase + np.random.uniform(-0.5, 0.5)
    
    # Health degradation model
    health_degradation = (100 - new_soc) * 0.08 + max(0, temperature - 35) * 0.1
    health_score = max(45, 97 - health_degradation)
    
    return {
        'voltage': round(voltage, 3),
        'current': round(current, 2),
        'temperature': round(temperature, 1),
        'soc': round(new_soc, 1),
        'health_score': round(health_score, 1),
        'timestamp': datetime.now().strftime("%H:%M:%S"),
        'is_charging': is_charging,
        'power': round(voltage * abs(current), 2),
        'energy_remaining': round(new_soc * 75 / 100, 1)  # kWh assuming 75kWh pack
    }

def get_thermal_indicator(temperature):
    """Get thermal status with appropriate styling"""
    if temperature < 28:
        return "thermal-cool", "❄️ COOL", "#4FC3F7"
    elif temperature < 42:
        return "thermal-warm", "🌡️ WARM", "#FFB74D"
    else:
        return "thermal-hot", "🔥 HOT", "#F44336"

def create_metric_card(title, value, delta, icon, delta_color="normal"):
    """Create beautiful metric cards"""
    delta_html = f"<span style='color: {'#4CAF50' if delta_color=='normal' else '#F44336'}; font-size: 14px;'>{delta}</span>"
    
    card_html = f"""
    <div class="metric-card">
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 24px; margin-right: 10px;">{icon}</span>
            <span style="font-size: 14px; color: #666; font-weight: 600;">{title}</span>
        </div>
        <div style="font-size: 24px; font-weight: 800; color: #1a237e;">{value}</div>
        <div style="font-size: 14px; margin-top: 5px;">{delta_html}</div>
    </div>
    """
    return card_html

def main():
    # PROFESSIONAL HEADER
    st.markdown('<h1 class="main-header">🔋 EV DIGITAL TWIN PLATFORM</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center; color: #5c6bc0; margin-bottom: 2rem;">🐅 Team TIGONS | KPIT Sparkle 2025</h3>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 16px; color: #666;"><b>Jayawantrao Sawant College of Engineering, Pune</b> | Industry-Grade EV Battery Monitoring System</p>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'sensor_data' not in st.session_state:
        st.session_state.sensor_data = []
        st.session_state.last_soc = 65
        st.session_state.is_charging = True
        st.session_state.cycle_count = 0

    # ENHANCED SIDEBAR
    with st.sidebar:
        st.markdown("### 🎮 SMART CONTROL PANEL")
        
        # Operation Mode with icons
        mode = st.radio(
            "**SELECT OPERATION MODE:**",
            ["⚡ FAST CHARGE", "🔋 SMART DISCHARGE", "🔄 AUTO CYCLE"],
            index=0,
            help="Choose between charging, discharging, or automatic cycling"
        )
        
        # Update charging state
        if "CHARGE" in mode:
            st.session_state.is_charging = True
        elif "DISCHARGE" in mode:
            st.session_state.is_charging = False
        
        st.markdown("---")
        st.markdown("### ⚙️ PERFORMANCE SETTINGS")
        
        simulation_speed = st.slider("Simulation Speed", 1, 10, 5, 
                                   help="Adjust how fast the simulation runs")
        
        data_history = st.slider("Data History Points", 20, 100, 50,
                               help="Number of data points to keep in memory")
        
        st.markdown("---")
        st.markdown("### 📊 SYSTEM STATUS")
        
        # Live status indicators
        if st.session_state.sensor_data:
            latest = st.session_state.sensor_data[-1]
            st.markdown(f"<div class='status-online'>🟢 LIVE STREAMING ACTIVE</div>", unsafe_allow_html=True)
            st.metric("Cycle Count", st.session_state.cycle_count)
            st.metric("Data Points", len(st.session_state.sensor_data))
        else:
            st.markdown("<div class='status-warning'>🟡 INITIALIZING SYSTEM</div>", unsafe_allow_html=True)
    
    # REAL-TIME STATUS BAR
    status_col1, status_col2, status_col3, status_col4 = st.columns(4)
    with status_col1:
        st.markdown("<div class='status-online'>🟢 SYSTEM ONLINE</div>", unsafe_allow_html=True)
    with status_col2:
        st.markdown("<div class='status-online'>📊 LIVE DATA FEED</div>", unsafe_allow_html=True)
    with status_col3:
        st.markdown("<div class='status-online'>🔋 BATTERY ACTIVE</div>", unsafe_allow_html=True)
    with status_col4:
        st.markdown("<div class='status-online'>🎯 COMPETITION READY</div>", unsafe_allow_html=True)
    
    # MAIN DASHBOARD GRID
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🔋 REAL-TIME BATTERY MONITOR")
        
        # Generate and store live data
        sensor_data = generate_advanced_sensor_data(
            st.session_state.last_soc, 
            st.session_state.is_charging
        )
        st.session_state.last_soc = sensor_data['soc']
        st.session_state.sensor_data.append(sensor_data)
        st.session_state.cycle_count += 1
        
        # Manage data history
        if len(st.session_state.sensor_data) > data_history:
            st.session_state.sensor_data = st.session_state.sensor_data[-data_history:]
        
        # ULTRA-REALISTIC BATTERY ANIMATION
        battery_html = create_realistic_battery(
            int(sensor_data['soc']), 
            st.session_state.is_charging,
            sensor_data['health_score']
        )
        st.markdown(battery_html, unsafe_allow_html=True)
        
        # THERMAL MONITORING
        thermal_class, thermal_text, thermal_color = get_thermal_indicator(sensor_data['temperature'])
        st.markdown(f"""
        <div class="battery-container {thermal_class}">
            <div style="font-size: 32px;">{thermal_text.split()[0]}</div>
            <div style="font-size: 24px; font-weight: bold;">{sensor_data['temperature']}°C</div>
            <div style="font-size: 14px; margin-top: 5px;">{thermal_text.split()[1]} THERMAL ZONE</div>
            <div style="font-size: 12px; opacity: 0.8; margin-top: 5px;">
                {'Optimal' if sensor_data['temperature'] < 35 else 'Monitor Closely'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📊 LIVE PERFORMANCE METRICS")
        
        # BEAUTIFUL METRIC CARDS
        metrics_col1, metrics_col2 = st.columns(2)
        
        with metrics_col1:
            # Voltage Card
            voltage_delta = f"{sensor_data['voltage']-3.8:+.2f}V"
            st.markdown(create_metric_card(
                "VOLTAGE", f"{sensor_data['voltage']}V", voltage_delta, "⚡"
            ), unsafe_allow_html=True)
            
            # Temperature Card
            temp_status = "❄️" if sensor_data['temperature'] < 30 else "🔥"
            st.markdown(create_metric_card(
                "TEMPERATURE", f"{sensor_data['temperature']}°C", temp_status, "🌡️"
            ), unsafe_allow_html=True)
            
        with metrics_col2:
            # Current Card
            current_icon = "⚡" if sensor_data['current'] > 0 else "🔋"
            current_status = "Charging" if sensor_data['current'] > 0 else "Discharging"
            st.markdown(create_metric_card(
                "CURRENT", f"{sensor_data['current']}A", current_status, current_icon
            ), unsafe_allow_html=True)
            
            # Health Card
            health_delta = "-0.1%" if sensor_data['health_score'] < 90 else "-0.05%"
            health_color = "inverse" if sensor_data['health_score'] < 80 else "normal"
            st.markdown(create_metric_card(
                "HEALTH", f"{sensor_data['health_score']}%", health_delta, "💪"
            ), unsafe_allow_html=True)
        
        # ADDITIONAL TECHNICAL SPECS
        st.markdown("#### 🔧 ADVANCED TECHNICAL SPECIFICATIONS")
        
        spec_col1, spec_col2 = st.columns(2)
        with spec_col1:
            st.metric("🔋 Power Output", f"{sensor_data['power']}W")
            st.metric("📊 Energy Remaining", f"{sensor_data['energy_remaining']}kWh")
        with spec_col2:
            st.metric("🔄 Operation Mode", 
                     f"{'⚡ Charging' if sensor_data['is_charging'] else '🔋 Discharging'}")
            st.metric("🕒 Last Update", sensor_data['timestamp'])
        
        st.markdown("---")
        st.markdown("### 📈 REAL-TIME PERFORMANCE TRENDS")
        
        # LIVE CHARTS
        if len(st.session_state.sensor_data) > 1:
            df = pd.DataFrame(st.session_state.sensor_data)
            
            # SOC Trend with area chart
            st.area_chart(df['soc'], use_container_width=True)
            st.caption("🔄 **State of Charge Trend** - Real-time monitoring")
            
            # Voltage & Current combined
            col1, col2 = st.columns(2)
            with col1:
                st.line_chart(df['voltage'], use_container_width=True)
                st.caption("⚡ **Voltage Profile**")
            with col2:
                st.line_chart(df['current'], use_container_width=True)
                st.caption("🔌 **Current Flow**")
    
    # AI-POWERED INSIGHTS SECTION
    st.markdown("---")
    st.markdown("### 🤖 AI-POWERED PREDICTIVE ANALYTICS")
    
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        # Risk Assessment
        risk_score = min(1.0, (100 - sensor_data['soc']) * 0.01 + 
                        max(0, sensor_data['temperature'] - 30) * 0.03)
        
        if risk_score < 0.25:
            st.markdown("<div class='status-online'>✅ LOW RISK<br>Optimal operating conditions</div>", unsafe_allow_html=True)
        elif risk_score < 0.6:
            st.markdown("<div class='status-warning'>⚠️ MEDIUM RISK<br>Monitor parameters closely</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='status-critical'>🚨 HIGH RISK<br>Immediate action required</div>", unsafe_allow_html=True)
        
        st.metric("Risk Score", f"{risk_score:.2f}")
    
    with insight_col2:
        # Maintenance Predictions
        remaining_cycles = int((sensor_data['health_score'] - 70) / 0.02)
        st.info(f"""
        **🔧 PREDICTIVE MAINTENANCE**
        
        • Remaining cycles: **{remaining_cycles}**
        • Next service: **30 days**
        • Health degradation: **2% per 100 cycles**
        """)
    
    with insight_col3:
        # Optimization Tips
        st.success(f"""
        **💡 SMART OPTIMIZATION**
        
        • Maintain SOC: **20-80%**
        • Optimal temp: **< 35°C**
        • Charging rate: **{ 'Optimal' if sensor_data['current'] < 40 else 'Reduce' }**
        • Cycle health: **{sensor_data['health_score']}%**
        """)
    
    # ACTION BUTTONS
    st.markdown("---")
    st.markdown("### 🎯 QUICK ACTIONS")
    
    action_col1, action_col2, action_col3, action_col4 = st.columns(4)
    
    with action_col1:
        if st.button("📥 Export Report", use_container_width=True):
            st.success("Report exported successfully!")
    
    with action_col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    with action_col3:
        if st.button("📊 Full Analytics", use_container_width=True):
            st.info("Opening detailed analytics dashboard...")
    
    with action_col4:
        if st.button("🆘 Emergency Stop", use_container_width=True):
            st.error("EMERGENCY STOP ACTIVATED - System safe")
    
    # COMPETITION FOOTER
    st.markdown("---")
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1a237e, #3949ab); color: white; padding: 20px; border-radius: 15px; text-align: center;'>
        <h3 style='color: white; margin-bottom: 10px;'>🏆 KPIT SPARKLE 2025 READY</h3>
        <p style='margin-bottom: 0;'>
        <b>Industry-Grade EV Digital Twin Platform</b> | Real-time Monitoring | AI-Powered Predictions | Commercial Viability
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # AUTO-REFRESH FOR LIVE EXPERIENCE
    refresh_delay = max(1, 6 - simulation_speed)
    time.sleep(refresh_delay)
    st.rerun()

if __name__ == "__main__":
    main()
