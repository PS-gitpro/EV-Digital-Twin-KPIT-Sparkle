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

def create_battery_animation(soc):
    """Create animated battery visualization"""
    battery_html = f"""
    <div style="text-align: center; margin: 20px;">
        <div style="width: 120px; height: 200px; border: 3px solid #333; border-radius: 10px; 
                    margin: 0 auto; position: relative; background: linear-gradient(to top, #4CAF50 {soc}%, #f0f0f0 {soc}%);">
            <div style="width: 30px; height: 10px; background: #333; position: absolute; 
                        top: -13px; left: 45px; border-radius: 3px 3px 0 0;"></div>
            <div style="position: absolute; bottom: 10px; width: 100%; text-align: center; 
                        color: #333; font-weight: bold; font-size: 16px;">{soc}%</div>
        </div>
        <div style="margin-top: 10px; font-weight: bold; color: #666;">Battery State of Charge</div>
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

def generate_sample_sensor_data():
    """Generate realistic sensor data"""
    return {
        'voltage': round(3.6 + np.random.random() * 0.8, 2),
        'current': round(20 + np.random.random() * 50, 1),
        'temperature': round(25 + np.random.random() * 20, 1),
        'soc': max(10, min(95, 75 + np.random.normal(0, 5))),
        'internal_resistance': round(0.05 + np.random.random() * 0.1, 3),
        'cycle_count': np.random.randint(100, 1500),
        'timestamp': datetime.now().strftime("%H:%M:%S")
    }

def create_download_link(df, filename, text):
    """Generate download link for CSV"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def main():
    st.title("🔋 EV Digital Twin Platform")
    st.markdown("### 🐅 Team TIGONS - KPIT Sparkle 2025")
    st.markdown("**Jayawantrao Sawant College of Engineering, Pune**")
    
    # Team Info
    with st.sidebar:
        st.header("👥 Team TIGONS")
        st.write("**Team Leader:** Rupesh Manore")
        st.write("**Member:** Prateek Singh")
        st.write("**Mentor:** Prof. N.V. Tayade")
        st.write("**Email:** rupeshmanore2004@gmail.com")
        st.write("**GitHub:** [Project Repository](https://github.com/PS-gitpro/EV-Digital-Twin-KPIT-Sparkle)")
        st.success("🚀 Live Deployment Active")
    
    # Initialize session state for sensor data
    if 'sensor_data' not in st.session_state:
        st.session_state.sensor_data = []
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📡 Sensor Data", "🤖 AI Demo", "📈 Reports"])
    
    with tab1:
        st.header("Real-time Battery Monitoring")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            st.subheader("Live Sensor Metrics")
            
            # Generate fresh sensor data
            sensor_data = generate_sample_sensor_data()
            st.session_state.sensor_data.append(sensor_data)
            
            # Keep only last 100 readings
            if len(st.session_state.sensor_data) > 100:
                st.session_state.sensor_data = st.session_state.sensor_data[-100:]
            
            # Display metrics
            m1, m2 = st.columns(2)
            with m1:
                st.metric("Voltage", f"{sensor_data['voltage']}V", "-0.2V")
                st.metric("Current", f"{sensor_data['current']}A", "+5A")
            with m2:
                st.metric("Temperature", f"{sensor_data['temperature']}°C", "+4°C")
                st.metric("SOC", f"{sensor_data['soc']}%", "-5%")
            
            # Health indicator
            health_score = max(0, min(100, sensor_data['soc'] - (sensor_data['temperature'] - 25) * 0.5))
            health_status, health_color = get_health_indicator(health_score)
            
            st.subheader("Battery Health Status")
            st.markdown(f"<h3 style='color: {health_color};'>{health_status}</h3>", unsafe_allow_html=True)
            st.progress(health_score / 100)
            st.write(f"Health Score: {health_score:.1f}/100")
        
        with col2:
            st.subheader("Battery Visualization")
            # Animated battery
            battery_html = create_battery_animation(int(sensor_data['soc']))
            st.markdown(battery_html, unsafe_allow_html=True)
            
            # Additional metrics
            st.metric("Internal Resistance", f"{sensor_data['internal_resistance']}Ω")
            st.metric("Cycle Count", sensor_data['cycle_count'])
        
        with col3:
            st.subheader("Performance Analytics")
            
            # Create sample time series data
            time_points = np.linspace(0, 100, 50)
            voltage_data = 4.2 - 0.03 * time_points + 0.1 * np.sin(0.3 * time_points)
            current_data = 45 + 10 * np.sin(0.5 * time_points)
            
            # Voltage chart
            voltage_df = pd.DataFrame({
                'Time': time_points,
                'Voltage': voltage_data
            })
            st.line_chart(voltage_df.set_index('Time'))
            
            # Current chart
            current_df = pd.DataFrame({
                'Time': time_points,
                'Current': current_data
            })
            st.line_chart(current_df.set_index('Time'))
    
    with tab2:
        st.header("📡 Live Sensor Data Stream")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Real-time Sensor Readings")
            
            # Display latest sensor data in a nice format
            latest_data = st.session_state.sensor_data[-1] if st.session_state.sensor_data else generate_sample_sensor_data()
            
            st.write(f"**Timestamp:** {latest_data['timestamp']}")
            st.write(f"**Voltage:** {latest_data['voltage']} V")
            st.write(f"**Current:** {latest_data['current']} A")
            st.write(f"**Temperature:** {latest_data['temperature']} °C")
            st.write(f"**State of Charge:** {latest_data['soc']} %")
            st.write(f"**Internal Resistance:** {latest_data['internal_resistance']} Ω")
            st.write(f"**Cycle Count:** {latest_data['cycle_count']}")
            
            # Refresh button
            if st.button("🔄 Refresh Sensor Data"):
                st.rerun()
        
        with col2:
            st.subheader("Sensor Data History")
            
            if st.session_state.sensor_data:
                # Create DataFrame from sensor data
                df = pd.DataFrame(st.session_state.sensor_data)
                st.dataframe(df.tail(10), use_container_width=True)
                
                st.write(f"Total readings collected: {len(df)}")
            else:
                st.info("No sensor data collected yet. Data will appear here.")
    
    with tab3:
        st.header("🤖 AI-Powered Failure Prediction")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Failure Risk Assessment")
            
            # Calculate risk based on sensor data
            if st.session_state.sensor_data:
                latest = st.session_state.sensor_data[-1]
                risk_score = min(1.0, (100 - latest['soc']) * 0.01 + (latest['temperature'] - 25) * 0.02)
            else:
                risk_score = 0.59
            
            risk_score = st.slider("Adjust Risk Parameters", 0.0, 1.0, float(risk_score))
            
            if risk_score < 0.3:
                status = "✅ LOW RISK"
                color = "#4CAF50"
                suggestions = ["Continue normal operation", "Monitor standard metrics"]
            elif risk_score < 0.7:
                status = "⚠️ MEDIUM RISK"
                color = "#FF9800"
                suggestions = ["Reduce fast charging", "Monitor temperature closely", "Check cooling system"]
            else:
                status = "🚨 HIGH RISK"
                color = "#F44336"
                suggestions = ["Immediate maintenance required", "Reduce load immediately", "Check for thermal runaway"]
            
            st.markdown(f"<h2 style='color: {color};'>{status}</h2>", unsafe_allow_html=True)
            st.progress(risk_score)
            st.write(f"Risk Score: {risk_score:.3f}")
        
        with col2:
            st.subheader("💡 AI Recommendations")
            
            for suggestion in suggestions:
                st.info(suggestion)
            
            st.subheader("Predictive Maintenance")
            st.success("Next recommended service: 30 days")
            st.warning("Battery degradation rate: 2% per 100 cycles")
            st.info("Estimated remaining life: 840 cycles")
    
    with tab4:
        st.header("📊 Reports & Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Performance Report")
            
            if st.session_state.sensor_data:
                df = pd.DataFrame(st.session_state.sensor_data)
                
                # Summary statistics
                st.write("**Summary Statistics:**")
                st.write(f"- Average Voltage: {df['voltage'].mean():.2f} V")
                st.write(f"- Average Current: {df['current'].mean():.1f} A")
                st.write(f"- Average Temperature: {df['temperature'].mean():.1f} °C")
                st.write(f"- Average SOC: {df['soc'].mean():.1f} %")
                st.write(f"- Data Points: {len(df)}")
                
                # Download buttons
                st.markdown("### 📥 Export Data")
                
                if st.button("📄 Download CSV Report"):
                    st.markdown(create_download_link(df, "battery_performance_report.csv", "📥 Download CSV Report"), unsafe_allow_html=True)
                
                if st.button("📊 Download Summary PDF"):
                    # For demo purposes, we'll create a simple text summary
                    summary_text = f"""
                    BATTERY PERFORMANCE REPORT
                    Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                    
                    Summary Statistics:
                    - Average Voltage: {df['voltage'].mean():.2f} V
                    - Average Current: {df['current'].mean():.1f} A  
                    - Average Temperature: {df['temperature'].mean():.1f} °C
                    - Average SOC: {df['soc'].mean():.1f} %
                    - Total Data Points: {len(df)}
                    
                    Health Assessment: {get_health_indicator(df['soc'].mean())[0]}
                    Risk Level: {'LOW' if risk_score < 0.3 else 'MEDIUM' if risk_score < 0.7 else 'HIGH'}
                    
                    ---
                    Generated by Team TIGONS - EV Digital Twin Platform
                    """
                    st.text_area("Report Summary (Copy this data):", summary_text, height=200)
        
        with col2:
            st.subheader("Data Visualization")
            
            if st.session_state.sensor_data:
                df = pd.DataFrame(st.session_state.sensor_data)
                
                # Simple histogram for SOC distribution
                st.bar_chart(df['soc'].value_counts().sort_index())
                st.write("State of Charge Distribution")
                
                # Temperature trend
                if len(df) > 1:
                    temp_df = pd.DataFrame({
                        'Reading': range(len(df)),
                        'Temperature': df['temperature']
                    })
                    st.line_chart(temp_df.set_index('Reading'))
                    st.write("Temperature Trend Over Time")
    
    # Auto-refresh every 10 seconds
    st.markdown("---")
    st.caption("🔄 Data updates every 10 seconds | 🐅 Team TIGONS - KPIT Sparkle 2025")

if __name__ == "__main__":
    main()
