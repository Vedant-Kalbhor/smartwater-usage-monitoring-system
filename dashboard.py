import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from firebase_manager import FirebaseManager
from data_processing import get_real_time_data, get_historical_data, detect_anomalies
from utils import check_alerts, format_volume, format_timestamp

def display_dashboard(firebase_manager: FirebaseManager):
    """
    Display the main dashboard with real-time and historical water monitoring data.
    """
    st.title("💧 Water Monitoring Dashboard")
    
    # Create tabs for different sections
    tabs = st.tabs(["Real-time Data", "Historical Data", "Alerts", "Export Data"])
    
    # Demo mode for simulated data
    if 'demo_mode' in st.session_state and st.session_state.demo_mode:
        demo_data = generate_demo_data()
        real_time_tab(tabs[0], demo_data.get("real_time", {}))
        historical_tab(tabs[1], demo_data.get("historical", pd.DataFrame()))
        alerts_tab(tabs[2], demo_data.get("alerts", []))
        export_tab(tabs[3], demo_data.get("historical", pd.DataFrame()))
    else:
        # Get real-time data
        real_time_data = get_real_time_data(firebase_manager)
        
        # Get historical data for the past 7 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        historical_data = get_historical_data(firebase_manager, start_date.timestamp(), end_date.timestamp())
        
        # Check for any alerts
        if 'user_id' in st.session_state and st.session_state.user_id:
            user_settings = firebase_manager.get_user_settings(st.session_state.user_id)
            thresholds = user_settings.get('alert_thresholds', {}) if user_settings else {}
        else:
            thresholds = {
                "pressure_high": 6.0,
                "pressure_low": 1.0,
                "flow_high": 20.0,
                "daily_usage_high": 500.0
            }
        
        alerts = check_alerts(real_time_data, thresholds)
        
        # Display data in tabs
        real_time_tab(tabs[0], real_time_data)
        historical_tab(tabs[1], historical_data)
        alerts_tab(tabs[2], alerts)
        export_tab(tabs[3], historical_data)

def real_time_tab(tab, data):
    """Display real-time water monitoring data."""
    with tab:
        st.subheader("Current Water Statistics")
        
        if not data:
            st.warning("No real-time data available. Check your sensor connection.")
            return
        
        # Current time
        st.write(f"Last updated: {format_timestamp(data.get('timestamp', datetime.now().timestamp()))}")
        
        # Create a 3-column layout for key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Flow rate gauge
            flow_rate = data.get('flow_rate', 0.0)
            st.metric("Flow Rate", f"{flow_rate:.1f} L/min", delta=None)
            
            # Create a gauge chart for flow rate
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=flow_rate,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Flow Rate (L/min)"},
                gauge={
                    'axis': {'range': [0, 30], 'tickwidth': 1},
                    'bar': {'color': "#1f77b4"},
                    'steps': [
                        {'range': [0, 5], 'color': "lightblue"},
                        {'range': [5, 15], 'color': "royalblue"},
                        {'range': [15, 30], 'color': "darkblue"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 25
                    }
                }
            ))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Pressure gauge
            pressure = data.get('pressure', 0.0)
            st.metric("Pressure", f"{pressure:.1f} bar", delta=None)
            
            # Create a gauge chart for pressure
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=pressure,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Pressure (bar)"},
                gauge={
                    'axis': {'range': [0, 10], 'tickwidth': 1},
                    'bar': {'color': "#ff7f0e"},
                    'steps': [
                        {'range': [0, 2], 'color': "lightyellow"},
                        {'range': [2, 6], 'color': "gold"},
                        {'range': [6, 10], 'color': "orange"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 8
                    }
                }
            ))
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            # Water usage metrics
            daily_usage = data.get('daily_usage', 0.0)
            hourly_usage = data.get('hourly_usage', 0.0)
            
            st.metric("Daily Usage", format_volume(daily_usage), delta=None)
            st.metric("Hourly Usage", format_volume(hourly_usage), delta=None)
            
            # WiFi connection status
            st.write("### Connectivity")
            st.success("Sensor Online ✅")

def historical_tab(tab, data):
    """Display historical water usage and pressure data."""
    with tab:
        st.subheader("Historical Water Usage")
        
        if isinstance(data, pd.DataFrame) and not data.empty:
            # Time range selector
            time_range = st.selectbox(
                "Select Time Range",
                ["Last 24 Hours", "Last 3 Days", "Last Week", "Last Month"],
                index=2
            )
            
            # Convert timestamps to datetime for better visualization
            data['datetime'] = pd.to_datetime(data['timestamp'], unit='s')
            data.set_index('datetime', inplace=True)
            
            # Filter data based on selected time range
            now = datetime.now()
            if time_range == "Last 24 Hours":
                filtered_data = data[data.index >= (now - timedelta(hours=24))]
            elif time_range == "Last 3 Days":
                filtered_data = data[data.index >= (now - timedelta(days=3))]
            elif time_range == "Last Week":
                filtered_data = data[data.index >= (now - timedelta(days=7))]
            else:  # Last Month
                filtered_data = data[data.index >= (now - timedelta(days=30))]
            
            # Resample data for better visualization
            if time_range == "Last 24 Hours":
                resampled_data = filtered_data.resample('15min').mean()
            elif time_range == "Last 3 Days":
                resampled_data = filtered_data.resample('1H').mean()
            elif time_range == "Last Week":
                resampled_data = filtered_data.resample('2H').mean()
            else:  # Last Month
                resampled_data = filtered_data.resample('6H').mean()
            
            # Fill NaN values
            resampled_data = resampled_data.fillna(method='ffill')
            
            # Visualization options
            visualization = st.radio(
                "Select Visualization",
                ["Water Usage", "Flow Rate", "Pressure", "Compare All"],
                horizontal=True
            )
            
            if visualization == "Water Usage":
                # Cumulative usage visualization
                daily_usage = filtered_data['volume'].resample('1D').sum().cumsum()
                
                fig = px.bar(
                    daily_usage,
                    labels={"value": "Water Usage (L)", "datetime": "Date"},
                    title="Cumulative Daily Water Usage"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Hourly usage patterns
                hourly_usage = filtered_data['volume'].resample('1H').sum()
                hourly_avg = hourly_usage.groupby(hourly_usage.index.hour).mean()
                
                fig = px.bar(
                    hourly_avg,
                    labels={"value": "Average Usage (L)", "index": "Hour of Day"},
                    title="Average Hourly Water Usage"
                )
                st.plotly_chart(fig, use_container_width=True)
                
            elif visualization == "Flow Rate":
                # Flow rate over time
                fig = px.line(
                    resampled_data,
                    y='flow_rate',
                    labels={"flow_rate": "Flow Rate (L/min)", "datetime": "Date"},
                    title="Water Flow Rate Over Time"
                )
                
                # Add anomaly detection
                anomalies = detect_anomalies(resampled_data, 'flow_rate')
                anomaly_points = resampled_data[anomalies]
                
                if not anomaly_points.empty:
                    fig.add_scatter(
                        x=anomaly_points.index,
                        y=anomaly_points['flow_rate'],
                        mode='markers',
                        marker=dict(color='red', size=10),
                        name='Anomalies'
                    )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Flow rate distribution
                fig = px.histogram(
                    filtered_data,
                    x='flow_rate',
                    labels={"flow_rate": "Flow Rate (L/min)", "count": "Frequency"},
                    title="Flow Rate Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
                
            elif visualization == "Pressure":
                # Pressure over time
                fig = px.line(
                    resampled_data,
                    y='pressure',
                    labels={"pressure": "Pressure (bar)", "datetime": "Date"},
                    title="Water Pressure Over Time"
                )
                
                # Add anomaly detection
                anomalies = detect_anomalies(resampled_data, 'pressure')
                anomaly_points = resampled_data[anomalies]
                
                if not anomaly_points.empty:
                    fig.add_scatter(
                        x=anomaly_points.index,
                        y=anomaly_points['pressure'],
                        mode='markers',
                        marker=dict(color='red', size=10),
                        name='Anomalies'
                    )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Pressure histogram
                fig = px.histogram(
                    filtered_data,
                    x='pressure',
                    labels={"pressure": "Pressure (bar)", "count": "Frequency"},
                    title="Pressure Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
                
            else:  # Compare All
                # Combined visualization
                fig = go.Figure()
                
                # Add flow rate
                fig.add_trace(go.Scatter(
                    x=resampled_data.index,
                    y=resampled_data['flow_rate'],
                    name='Flow Rate (L/min)',
                    line=dict(color='blue')
                ))
                
                # Add pressure on secondary y-axis
                fig.add_trace(go.Scatter(
                    x=resampled_data.index,
                    y=resampled_data['pressure'],
                    name='Pressure (bar)',
                    line=dict(color='orange'),
                    yaxis='y2'
                ))
                
                # Update layout for dual y-axis
                fig.update_layout(
                    title="Flow Rate and Pressure Over Time",
                    xaxis=dict(title="Date"),
                    yaxis=dict(
                        title="Flow Rate (L/min)",
                        titlefont=dict(color='blue'),
                        tickfont=dict(color='blue')
                    ),
                    yaxis2=dict(
                        title="Pressure (bar)",
                        titlefont=dict(color='orange'),
                        tickfont=dict(color='orange'),
                        anchor="x",
                        overlaying="y",
                        side="right"
                    ),
                    legend=dict(x=0.01, y=0.99)
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No historical data available for the selected time range.")
            
            # Demo chart with random data
            if 'demo_mode' in st.session_state and st.session_state.demo_mode:
                st.write("### Sample Historical Data")
                dates = pd.date_range(start=datetime.now() - timedelta(days=7), end=datetime.now(), freq='1H')
                flow_data = np.random.normal(10, 3, size=len(dates))
                pressure_data = np.random.normal(4, 0.5, size=len(dates))
                
                demo_df = pd.DataFrame({
                    'datetime': dates,
                    'flow_rate': flow_data,
                    'pressure': pressure_data
                })
                demo_df.set_index('datetime', inplace=True)
                
                fig = px.line(
                    demo_df,
                    y=['flow_rate', 'pressure'],
                    labels={"value": "Measurement", "datetime": "Date", "variable": "Metric"},
                    title="Sample Historical Data (Demo)"
                )
                st.plotly_chart(fig, use_container_width=True)

def alerts_tab(tab, alerts):
    """Display water monitoring alerts."""
    with tab:
        st.subheader("Water Monitoring Alerts")
        
        if alerts:
            for i, alert in enumerate(alerts):
                severity = alert.get('severity', 'info')
                if severity == 'high':
                    st.error(f"⚠️ {alert.get('message', 'Unknown alert')}")
                elif severity == 'medium':
                    st.warning(f"⚠️ {alert.get('message', 'Unknown alert')}")
                else:
                    st.info(f"ℹ️ {alert.get('message', 'Unknown alert')}")
        else:
            st.success("No active alerts. Your water system is functioning normally.")

def export_tab(tab, data):
    """Allow exporting of historical data."""
    with tab:
        st.subheader("Export Water Monitoring Data")
        
        if isinstance(data, pd.DataFrame) and not data.empty:
            # Time range selector for export
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    "Start Date",
                    value=datetime.now() - timedelta(days=7),
                    max_value=datetime.now()
                )
            with col2:
                end_date = st.date_input(
                    "End Date",
                    value=datetime.now(),
                    max_value=datetime.now()
                )
            
            # Convert timestamps to datetime for filtering
            if 'datetime' not in data.columns:
                if data.index.name == 'datetime':
                    data = data.reset_index()
                else:
                    data['datetime'] = pd.to_datetime(data['timestamp'], unit='s')
            
            # Filter data based on selected dates
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            filtered_data = data[(data['datetime'] >= start_datetime) & (data['datetime'] <= end_datetime)]
            
            # Format the data
            if not filtered_data.empty:
                # Convert to readable format
                export_data = filtered_data.copy()
                export_data['datetime'] = export_data['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
                
                # Export options
                export_format = st.selectbox(
                    "Export Format",
                    ["CSV", "JSON", "Excel"],
                    index=0
                )
                
                if export_format == "CSV":
                    csv = export_data.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"water_data_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                elif export_format == "JSON":
                    json_data = export_data.to_json(orient="records")
                    st.download_button(
                        label="Download JSON",
                        data=json_data,
                        file_name=f"water_data_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json",
                        mime="application/json"
                    )
                else:  # Excel
                    # For Streamlit, we'll use a workaround for Excel downloads
                    csv = export_data.to_csv(index=False)
                    st.download_button(
                        label="Download Excel (CSV format)",
                        data=csv,
                        file_name=f"water_data_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                
                # Preview of the data
                st.write(f"### Data Preview ({len(filtered_data)} records)")
                st.dataframe(filtered_data.head(10))
            else:
                st.warning("No data available for the selected date range.")
        else:
            st.info("No historical data available for export.")
            
            # Demo data for export
            if 'demo_mode' in st.session_state and st.session_state.demo_mode:
                st.write("### Sample Data for Export")
                dates = pd.date_range(start=datetime.now() - timedelta(days=7), end=datetime.now(), freq='1H')
                flow_data = np.random.normal(10, 3, size=len(dates))
                pressure_data = np.random.normal(4, 0.5, size=len(dates))
                
                demo_df = pd.DataFrame({
                    'datetime': dates,
                    'flow_rate': flow_data,
                    'pressure': pressure_data,
                    'volume': flow_data * 60 / 1000,  # Convert to L
                })
                
                st.dataframe(demo_df.head(10))
                
                # Export demo data
                csv = demo_df.to_csv(index=False)
                st.download_button(
                    label="Download Demo Data (CSV)",
                    data=csv,
                    file_name="demo_water_data.csv",
                    mime="text/csv"
                )

def generate_demo_data():
    """Generate demo data for the dashboard when no real data is available."""
    # Current time
    now = datetime.now().timestamp()
    
    # Real-time data
    real_time = {
        'timestamp': now,
        'flow_rate': 8.5,
        'pressure': 3.2,
        'volume': 0.5,
        'hourly_usage': 22.8,
        'daily_usage': 245.6
    }
    
    # Historical data
    dates = pd.date_range(start=datetime.now() - timedelta(days=7), end=datetime.now(), freq='1H')
    timestamps = [d.timestamp() for d in dates]
    
    # Create patterns for flow rate and pressure
    hour_of_day = [d.hour for d in dates]
    
    # Daily pattern multipliers
    daily_pattern = {
        0: 0.3,  # Midnight
        1: 0.2,
        2: 0.1,
        3: 0.1,
        4: 0.2,
        5: 0.5,
        6: 1.0,  # Morning peak
        7: 1.5,
        8: 1.2,
        9: 0.8,
        10: 0.7,
        11: 0.8,
        12: 1.0,  # Lunch time
        13: 0.9,
        14: 0.7,
        15: 0.6,
        16: 0.7,
        17: 1.2,  # Evening peak
        18: 1.8,
        19: 1.5,
        20: 1.2,
        21: 0.9,
        22: 0.6,
        23: 0.4
    }
    
    flow_rate = []
    pressure = []
    volume = []
    hourly_usage = []
    daily_usage = []
    
    # Generate data with realistic patterns
    daily_sum = 0
    hourly_sum = 0
    last_day = dates[0].day
    last_hour = dates[0].hour
    
    for i, (date, hour) in enumerate(zip(dates, hour_of_day)):
        # Reset daily/hourly sums when day/hour changes
        if date.day != last_day:
            daily_sum = 0
            last_day = date.day
            
        if date.hour != last_hour:
            hourly_sum = 0
            last_hour = date.hour
        
        # Base flow rate with pattern and random variations
        base_flow = daily_pattern.get(hour, 0.5) * 8.0
        flow = base_flow * (1 + np.random.normal(0, 0.1))
        flow_rate.append(max(0, flow))
        
        # Base pressure with random variations
        base_pressure = 3.5 + np.random.normal(0, 0.2)
        pressure.append(max(0.5, base_pressure))
        
        # Volume calculation (flow rate * 60 minutes / 1000 to get liters)
        vol = flow * 60 / 1000
        volume.append(vol)
        
        # Update hourly and daily usage
        hourly_sum += vol
        daily_sum += vol
        
        hourly_usage.append(hourly_sum)
        daily_usage.append(daily_sum)
    
    # Create DataFrame
    historical = pd.DataFrame({
        'timestamp': timestamps,
        'flow_rate': flow_rate,
        'pressure': pressure,
        'volume': volume,
        'hourly_usage': hourly_usage,
        'daily_usage': daily_usage
    })
    
    # Add some anomalies for demonstration
    anomaly_indices = np.random.choice(len(historical), size=3, replace=False)
    for idx in anomaly_indices:
        if idx > 0:  # Skip the first entry
            historical.loc[idx, 'flow_rate'] = historical.loc[idx, 'flow_rate'] * 3
            historical.loc[idx, 'pressure'] = historical.loc[idx, 'pressure'] * 1.5
    
    # Alerts
    alerts = [
        {
            'timestamp': now - 3600,  # 1 hour ago
            'message': "Unusual water flow detected (20.5 L/min) at 14:30",
            'severity': 'high'
        },
        {
            'timestamp': now - 7200,  # 2 hours ago
            'message': "Daily water usage exceeded threshold (510.2 L)",
            'severity': 'medium'
        },
        {
            'timestamp': now - 86400,  # 1 day ago
            'message': "Sensor connection restored after 5 minutes offline",
            'severity': 'info'
        }
    ]
    
    return {
        'real_time': real_time,
        'historical': historical,
        'alerts': alerts
    }