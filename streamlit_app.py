import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
import base64

st.set_page_config(
    page_title="Team TIGONS - EV Digital Twin",
    page_icon="🔋",
    layout="wide"
)

def create_live_battery_animation(soc, is_charging=True):
    """Create live animated battery visualization with charging effect"""
    if is_charging:
        pulse_effect = f"""
        <style>
        @keyframes pulse {{
            0% {{ background: linear-gradient(to top, #4CAF50 {soc}%, #f0f0f0 {soc}%); }}
            50% {{ background: linear-gradient(to top, #66BB6A {soc}%, #f0f0f0 {soc}%); }}
            100% {{ background: linear-gradient(to top, #4CAF50 {soc}%, #f0f0f0 {soc}%); }}
        }}
        .battery-animation {{
            animation: pulse 2s infinite;
        }}
        </style>
        """
    else:
        pulse_effect = f"""
        <style>
        @keyframes discharge {{
            0% {{ background: linear-gradient(to top, #FF9800 {soc}%, #f0f0f0 {soc}%); }}
            50% {{ background: linear-gradient(to top, #FF5722 {soc}%, #f0f0f0 {soc}%); }}
            100% {{ background: linear-gradient(to top, #FF9800 {soc}%, #f0f0f0 {soc}%); }}
        }}
        .battery-animation {{
            animation: discharge 3s infinite;
        }}
        </style>
        """
    
    battery_html = f"""
    {pulse_effect}
    <div style="text-align: center; margin: 20px;">
        <div class="battery-animation" style="width: 120px; height: 200px; border: 3px solid #333; border-radius: 10px; 
                    margin: 0 auto; position: relative;">
            <div style="width: 30px; height: 10px; background: #333; position: absolute; 
                        top: -13px; left: 45px; border-radius: 3px 3px 0 0;"></div>
            <div style="position: absolute; bottom: 10px; width: 100%; text-align: center; 
                        color: #333; font-weight: bold; font-size: 16px;">{soc}%</div>
        </div>
        <div style="margin-top: 10px; font-weight: bold; color: #666;">
            {'⚡ CHARGING' if is_charging else '🔋 DISCHARGING'}
        </div>
        <div style="margin-top: 5px; font-size: 12px; color: #888;">
            Last update: {datetime.now().strftime('%H:%M:%S')}
        </div>
    </div>
    """
    return battery_html

def get_health_indicator(health_score):
    """Get health status with colored indicator"""
    if health_score >= 80:
        return "🟢 Healthy", "#4CAF50"
    elif health_score >= 60:
        return "🟡 Moderate", "#FF9800"
    else:
        return "🔴 Critical", "#F44336"

def generate_live_sensor_data(previous_soc=75, is_charging=True):
    """Generate realistic LIVE sensor data that changes over time"""
    # Simulate real charging/discharging
    if is_charging:
        new_soc = min(95, previous_soc + np.random.uniform(0.5, 2.0))
        current = round(30 + np.random.random() * 20, 1)  # Positive current for charging
    else:
        new_soc = max(15, previous_soc - np.random.uniform(0.5, 2.0))
        current = round(-20 - np.random.random() * 30, 1)  # Negative current for discharging
    
    return {
        'voltage': round(3.6 + (new_soc/100) * 0.8 + np.random.random() * 0.1, 2),
        'current': current,
        'temperature': round(25 + abs(current/10) + np.random.random() * 5, 1),
        'soc': round(new_soc, 1),
        'internal_resistance': round(0.05 + (100 - new_soc) * 0.001, 3),
        'cycle_count': np.random.randint(100, 1500),
        'timestamp': datetime.now().strftime("%H:%M:%S"),
        'is_charging': is_charging
    }

def create_download_link(df, filename, text):
    """Generate download link for CSV"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def main():
    st.title("🔋 EV Digital Twin Platform - LIVE")
    st.markdown("### 🐅 Team TIGONS - KPIT Sparkle 2025")
    st.markdown("**Jayawantrao Sawant College of Engineering, Pune**")
    
    # Initialize session state for live data
    if 'sensor_data' not in st.session_state:
        st.session_state.sensor_data = []
        st.session_state.last_soc = 75
        st.session_state.is_charging = True
    
    # Team Info
    with st.sidebar:
        st.header("👥 Team TIGONS")
        st.write("**Team Leader:** Rupesh Manore")
        st.write("**Member:** Prateek Singh")
        st.write("**Mentor:** Prof. N.V. Tayade")
        st.write("**Email:** rupeshmanore2004@gmail.com")
        st.write("**GitHub:** [Project Repository](https://github.com/PS-gitpro/EV-Digital-Twin-KPIT-Sparkle)")
        
        st.markdown("---")
        st.subheader("🔴 LIVE Mode Controls")
        
        # Charging/Discharging toggle
        charging_mode = st.radio(
            "Battery Mode:",
            ["⚡ CHARGING", "🔋 DISCHARGING"],
            index=0 if st.session_state.is_charging else 1
        )
        st.session_state.is_charging = (charging_mode == "⚡ CHARGING")
        
        st.success("🚀 **LIVE DATA STREAMING ACTIVE**")
        st.info("Data updates every 5 seconds")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 LIVE Dashboard", "📡 Sensor Data", "🤖 AI Demo", "📈 Reports"])
    
    with tab1:
        st.header("🔴 LIVE Real-time Battery Monitoring")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            st.subheader("🎯 Live Sensor Metrics")
            
            # Generate FRESH live sensor data
            sensor_data = generate_live_sensor_data(
                st.session_state.last_soc, 
                st.session_state.is_charging
            )
            st.session_state.last_soc = sensor_data['soc']
            st.session_state.sensor_data.append(sensor_data)
            
            # Keep only last 50 readings for performance
            if len(st.session_state.sensor_data) > 50:
                st.session_state.sensor_data = st.session_state.sensor_data[-50:]
            
            # Display LIVE metrics with trends
            m1, m2 = st.columns(2)
            with m1:
                voltage_trend = "📈" if sensor_data['voltage'] > 3.8 else "📉"
                current_trend = "⚡" if sensor_data['current'] > 0 else "🔋"
                st.metric("Voltage", f"{sensor_data['voltage']}V", voltage_trend)
                st.metric("Current", f"{sensor_data['current']}A", current_trend)
            with m2:
                temp_trend = "🔥" if sensor_data['temperature'] > 30 else "❄️"
                soc_trend = "⬆️" if st.session_state.is_charging else "⬇️"
                st.metric("Temperature", f"{sensor_data['temperature']}°C", temp_trend)
                st.metric("SOC", f"{sensor_data['soc']}%", soc_trend)
            
            # Health indicator
            health_score = max(0, min(100, sensor_data['soc'] - (sensor_data['temperature'] - 25) * 0.5))
            health_status, health_color = get_health_indicator(health_score)
            
            st.subheader("🏥 Battery Health Status")
            st.markdown(f"<h3 style='color: {health_color};'>{health_status}</h3>", unsafe_allow_html=True)
            st.progress(health_score / 100)
            st.write(f"Health Score: {health_score:.1f}/100")
        
        with col2:
            st.subheader("🔋 Live Battery Animation")
            # LIVE animated battery with charging/discharging effects
            battery_html = create_live_battery_animation(
                int(sensor_data['soc']), 
                st.session_state.is_charging
            )
            st.markdown(battery_html, unsafe_allow_html=True)
            
            # Additional live metrics
            st.metric("Internal Resistance", f"{sensor_data['internal_resistance']}Ω")
            st.metric("Cycle Count", sensor_data['cycle_count'])
            
            # Live status indicator
            status_color = "#4CAF50" if st.session_state.is_charging else "#FF9800"
            status_text = "⚡ CHARGING" if st.session_state.is_charging else "🔋 DISCHARGING"
            st.markdown(f"<div style='background-color: {status_color}; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold;'>🔄 {status_text}</div>", unsafe_allow_html=True)
        
        with col3:
            st.subheader("📈 Live Performance Analytics")
            
            # Create LIVE time series data from actual sensor readings
            if len(st.session_state.sensor_data) > 1:
                df = pd.DataFrame(st.session_state.sensor_data)
                
                # Voltage trend chart
                voltage_chart_data = pd.DataFrame({
                    'Time': range(len(df)),
                    'Voltage': df['voltage']
                })
                st.line_chart(voltage_chart_data.set_index('Time'), use_container_width=True)
                st.write("📊 Live Voltage Trend")
                
                # SOC trend chart
                soc_chart_data = pd.DataFrame({
                    'Time': range(len(df)),
                    'State of Charge': df['soc']
                })
                st.line_chart(soc_chart_data.set_index('Time'), use_container_width=True)
                st.write("📊 Live SOC Trend")
    
    with tab2:
        st.header("📡 Live Sensor Data Stream")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Real-time Sensor Readings")
            
            # Display latest sensor data
            latest_data = st.session_state.sensor_data[-1] if st.session_state.sensor_data else generate_live_sensor_data()
            
            st.write(f"**🕒 Timestamp:** {latest_data['timestamp']}")
            st.write(f"**⚡ Voltage:** {latest_data['voltage']} V")
            st.write(f"**🔌 Current:** {latest_data['current']} A")
            st.write(f"**🌡️ Temperature:** {latest_data['temperature']} °C")
            st.write(f"**🔋 State of Charge:** {latest_data['soc']} %")
            st.write(f"**📊 Internal Resistance:** {latest_data['internal_resistance']} Ω")
            st.write(f"**🔄 Cycle Count:** {latest_data['cycle_count']}")
            st.write(f"**🔧 Mode:** {'⚡ CHARGING' if latest_data['is_charging'] else '🔋 DISCHARGING'}")
            
            # Auto-refresh
            st.markdown("---")
            st.write("🔄 **Auto-refreshing every 5 seconds**")
            
        with col2:
            st.subheader("📊 Sensor Data History")
            
            if st.session_state.sensor_data:
                df = pd.DataFrame(st.session_state.sensor_data)
                st.dataframe(df.tail(8), use_container_width=True)
                
                st.write(f"**Total readings:** {len(df)}")
                st.write(f"**Current mode:** {'⚡ CHARGING' if st.session_state.is_charging else '🔋 DISCHARGING'}")
            else:
                st.info("No sensor data collected yet. Data will appear here.")
    
    # Other tabs remain similar but with live data...
    with tab3:
        st.header("🤖 AI-Powered Failure Prediction")
        # ... [AI demo content similar to before but using live data]
        
    with tab4:
        st.header("📊 Reports & Analytics")
        # ... [Reports content similar to before but using live data]
    
    # Auto-refresh the entire app every 5 seconds for true live experience
    st.markdown("---")
    st.write("🔄 **LIVE MODE ACTIVE** - Data streaming every 5 seconds")
    time.sleep(5)  # Wait 5 seconds
    st.rerun()  # Refresh the entire app

if __name__ == "__main__":
    main()
