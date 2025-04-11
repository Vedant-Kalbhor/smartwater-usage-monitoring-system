import streamlit as st
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def display_wifi_status(firebase_manager=None):
    """
    Display WiFi connection status and history for the ESP8266 sensor.
    If firebase_manager is provided, it will fetch real data from Firebase.
    Otherwise, it will use demo data.
    """
    st.title("📶 WiFi Connection Status")
    
    # Create columns for status indicators
    col1, col2, col3 = st.columns(3)
    
    # Get the status data (either real or demo)
    status_data = get_status_data(firebase_manager)
    
    # Connection Status indicator
    with col1:
        st.subheader("Connection Status")
        if status_data["connected"]:
            st.success("✅ Connected")
        else:
            st.error("❌ Disconnected")
        
        # Show additional details if connected
        if status_data["connected"]:
            st.write(f"IP: {status_data['ip_address']}")
            st.write(f"SSID: {status_data['ssid']}")
            st.write(f"Last Update: {status_data['last_update_formatted']}")
    
    # Signal Strength indicator
    with col2:
        st.subheader("Signal Strength")
        
        # Create signal strength gauge
        signal_strength = status_data["signal_strength"]
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=signal_strength,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "RSSI (dBm)"},
            gauge={
                'axis': {'range': [-100, -40], 'tickwidth': 1},
                'bar': {'color': get_signal_color(signal_strength)},
                'steps': [
                    {'range': [-100, -80], 'color': "red"},
                    {'range': [-80, -67], 'color': "orange"},
                    {'range': [-67, -55], 'color': "yellow"},
                    {'range': [-55, -40], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 2},
                    'thickness': 0.75,
                    'value': signal_strength
                }
            }
        ))
        fig.update_layout(height=200)
        st.plotly_chart(fig, use_container_width=True)
        
        # Signal quality description
        st.write(f"Quality: {get_signal_quality_description(signal_strength)}")
    
    # Connection Uptime
    with col3:
        st.subheader("Connection Uptime")
        uptime_hours = status_data["uptime_hours"]
        st.metric("Total Uptime", f"{uptime_hours:.1f} hours")
        
        # Connection stability
        stability = status_data["stability"]
        st.progress(stability / 100)
        st.write(f"Stability: {stability}%")
    
    # Connection History
    st.subheader("Connection History")
    connection_history = status_data["connection_history"]
    
    # Plot connection history
    fig = px.line(
        connection_history,
        x='timestamp',
        y='signal_strength',
        labels={
            'timestamp': 'Time',
            'signal_strength': 'Signal Strength (dBm)'
        },
        title="WiFi Signal Strength History"
    )
    
    # Add connection status as colored regions
    for i, row in connection_history.iterrows():
        if not row['connected']:
            fig.add_vrect(
                x0=row['timestamp'],
                x1=row['timestamp'] + pd.Timedelta(minutes=5),
                fillcolor="red",
                opacity=0.2,
                layer="below",
                line_width=0
            )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Disconnection log
    st.subheader("Disconnection Log")
    
    # Filter only disconnection events
    disconnections = connection_history[connection_history['connected'] == False].copy()
    if not disconnections.empty:
        # Add formatted time column
        disconnections['formatted_time'] = disconnections['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Calculate durations (where possible)
        durations = []
        for i in range(len(disconnections)):
            if i < len(disconnections) - 1:
                # Find next connection after this disconnection
                next_connections = connection_history[
                    (connection_history['timestamp'] > disconnections.iloc[i]['timestamp']) & 
                    (connection_history['connected'] == True)
                ]
                
                if not next_connections.empty:
                    # Calculate outage duration
                    reconnect_time = next_connections.iloc[0]['timestamp']
                    duration = reconnect_time - disconnections.iloc[i]['timestamp']
                    durations.append(f"{duration.total_seconds() / 60:.1f} min")
                else:
                    durations.append("Ongoing")
            else:
                # If it's the last disconnection and still disconnected
                if not status_data["connected"]:
                    durations.append("Ongoing")
                else:
                    durations.append("Resolved")
        
        disconnections['duration'] = durations
        
        # Display the disconnection log table
        st.dataframe(
            disconnections[['formatted_time', 'duration']].rename(
                columns={
                    'formatted_time': 'Disconnection Time',
                    'duration': 'Outage Duration'
                }
            ),
            use_container_width=True
        )
    else:
        st.info("No disconnections recorded in the history.")
    
    # Refresh button
    if st.button("Refresh Status"):
        st.rerun()
    
    # Add recommendations based on signal strength
    if signal_strength < -70:
        st.warning("""
        ⚠️ Your WiFi signal is weak. Consider these improvements:
        - Move the ESP8266 device closer to your WiFi router
        - Install a WiFi range extender
        - Reduce interference from other electronic devices
        """)

def get_status_data(firebase_manager=None):
    """
    Get WiFi status data either from Firebase or generate demo data.
    """
    if firebase_manager and hasattr(firebase_manager, 'demo_mode') and not firebase_manager.demo_mode:
        try:
            # Fetch device status
            device_status = firebase_manager.get_device_status("default")
            
            if device_status:
                # Get current connection status
                connected = device_status.get('connected', False)
                signal_strength = device_status.get('signal_strength', -65)
                ssid = device_status.get('ssid', 'Unknown_Network')
                ip_address = device_status.get('ip_address', 'N/A')
                last_update = device_status.get('last_update', int(time.time()))
                
                # Format last update time
                last_update_formatted = datetime.fromtimestamp(last_update).strftime("%Y-%m-%d %H:%M:%S")
                
                # Get connection history
                connection_logs = firebase_manager.get_connection_logs("default", hours=24)
                
                if connection_logs and len(connection_logs) > 0:
                    # Process logs into DataFrame
                    timestamps = []
                    signal_strengths = []
                    connected_values = []
                    
                    for log in connection_logs:
                        timestamps.append(datetime.fromtimestamp(log.get('timestamp', 0)))
                        signal_strengths.append(log.get('signal_strength', -65))
                        connected_values.append(log.get('connected', True))
                    
                    connection_history = pd.DataFrame({
                        'timestamp': timestamps,
                        'signal_strength': signal_strengths,
                        'connected': connected_values
                    })
                    
                    # Calculate uptime and stability
                    total_samples = len(connection_history)
                    connected_samples = sum(connection_history['connected'])
                    stability = (connected_samples / total_samples) * 100 if total_samples > 0 else 100
                    
                    # Get uptime hours
                    if timestamps:
                        start_time = min(timestamps)
                        end_time = max(timestamps)
                        total_hours = (end_time - start_time).total_seconds() / 3600
                        uptime_hours = total_hours * (stability / 100)
                    else:
                        uptime_hours = 0
                    
                    # Return real data
                    st.success("Connected to Firebase! Showing real-time WiFi data.")
                    return {
                        "connected": connected,
                        "signal_strength": signal_strength,
                        "ssid": ssid,
                        "ip_address": ip_address if connected else "N/A",
                        "last_update_formatted": last_update_formatted,
                        "uptime_hours": uptime_hours,
                        "stability": round(stability, 1),
                        "connection_history": connection_history
                    }
            
            # If we couldn't get real data, fall back to demo data
            st.info("Unable to retrieve real WiFi data from Firebase. Showing demo data.")
        except Exception as e:
            st.error(f"Error retrieving WiFi status from Firebase: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
    
    # Generate demo data if no Firebase or if real data retrieval failed
    now = datetime.now()
    
    # Basic current status
    connected = np.random.choice([True, True, True, False], p=[0.8, 0.1, 0.05, 0.05])  # 95% chance of being connected
    signal_strength = -65 + np.random.normal(0, 5)  # Around -65 dBm with some variation
    signal_strength = max(-100, min(-40, signal_strength))  # Clamp between -100 and -40
    
    # Generate connection history for the past 24 hours
    history_hours = 24
    timestamps = [now - timedelta(hours=i) for i in range(history_hours, 0, -1)]
    
    # Random signal strengths with some correlation between adjacent values
    base_signal = -65
    signal_strengths = []
    connected_values = []
    
    for i in range(len(timestamps)):
        # Introduce some random drops
        if i > 0:
            # Add some correlation with previous value
            base_signal = 0.9 * base_signal + 0.1 * (-65 + np.random.normal(0, 3))
        
        # Apply random variation
        signal = base_signal + np.random.normal(0, 3)
        signal = max(-100, min(-40, signal))
        signal_strengths.append(signal)
        
        # Determine if connected (signal too weak means disconnection)
        is_connected = True
        if signal < -85:  # Very weak signal might mean disconnection
            is_connected = np.random.choice([True, False], p=[0.3, 0.7])  # 70% chance of disconnect if signal is very weak
        
        # Occasionally add random disconnections
        if np.random.random() < 0.05:  # 5% chance of random disconnection
            is_connected = False
            
        connected_values.append(is_connected)
    
    # Create connection history dataframe
    connection_history = pd.DataFrame({
        'timestamp': timestamps,
        'signal_strength': signal_strengths,
        'connected': connected_values
    })
    
    # Calculate uptime and stability
    total_samples = len(connection_history)
    connected_samples = sum(connection_history['connected'])
    stability = (connected_samples / total_samples) * 100
    
    # Create the status data dictionary
    status_data = {
        "connected": connected,
        "signal_strength": signal_strength,
        "ssid": "Home_WiFi_Network",
        "ip_address": "192.168.1.25" if connected else "N/A",
        "last_update_formatted": now.strftime("%Y-%m-%d %H:%M:%S"),
        "uptime_hours": history_hours * (stability / 100),
        "stability": round(stability, 1),
        "connection_history": connection_history
    }
    
    return status_data

def get_signal_color(signal_strength):
    """Return an appropriate color based on signal strength."""
    if signal_strength >= -55:
        return "green"
    elif signal_strength >= -67:
        return "yellow"
    elif signal_strength >= -80:
        return "orange"
    else:
        return "red"

def get_signal_quality_description(signal_strength):
    """Return a textual description of signal quality."""
    if signal_strength >= -55:
        return "Excellent"
    elif signal_strength >= -67:
        return "Good"
    elif signal_strength >= -80:
        return "Fair"
    else:
        return "Poor"

if __name__ == "__main__":
    # This allows the file to be run directly for testing
    st.set_page_config(
        page_title="WiFi Status",
        page_icon="📶",
        layout="wide"
    )
    display_wifi_status()