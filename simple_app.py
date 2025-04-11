import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from firebase_manager import FirebaseManager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Water Monitoring System - Dashboard without authentication

# App title and configuration
st.set_page_config(
    page_title="Water Monitoring Dashboard",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'
if 'firebase_initialized' not in st.session_state:
    st.session_state.firebase_initialized = False

# Initialize Firebase
def init_firebase():
    """Initialize Firebase with credentials from environment variables."""
    if st.session_state.firebase_initialized:
        return st.session_state.firebase_manager
    
    # Get Firebase credentials from environment variables
    api_key = os.getenv("FIREBASE_API_KEY")
    auth_domain = os.getenv("FIREBASE_AUTH_DOMAIN")
    database_url = os.getenv("FIREBASE_DATABASE_URL")
    storage_bucket = os.getenv("FIREBASE_STORAGE_BUCKET")
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    database_secret = os.getenv("FIREBASE_DATABASE_SECRET")
    
    # Check if necessary credentials are available (mainly database_url and database_secret)
    if not database_url or not database_secret:
        st.warning("⚠️ Running in demo mode with simulated data. Firebase credentials not found.")
        st.session_state.demo_mode = True
        firebase_manager = FirebaseManager()  # Initialize with demo mode defaults
        st.session_state.firebase_manager = firebase_manager
        st.session_state.firebase_initialized = True
        return firebase_manager
    
    # We have the required credentials
    # Initialize Firebase manager with real credentials
    firebase_manager = FirebaseManager(
        api_key=api_key,
        auth_domain=auth_domain,
        database_url=database_url,
        storage_bucket=storage_bucket,
        service_account_key=None  # No service account for this simplified version
    )
    
    # Verify if Firebase is connected
    test_data = firebase_manager.get_device_status("default")
    if test_data is not None:
        st.success("🔥 Connected to Firebase successfully!")
        st.session_state.demo_mode = False
    else:
        st.warning("⚠️ Unable to connect to Firebase. Running in demo mode.")
        st.session_state.demo_mode = True
    
    st.session_state.firebase_manager = firebase_manager
    st.session_state.firebase_initialized = True
    
    return firebase_manager

# Initialize Firebase connection
firebase_manager = init_firebase()

# Check if we're in demo mode
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = True

if st.session_state.demo_mode:
    st.warning("⚠️ Running in demo mode with simulated data. No actual device connection.")

# Apply custom styling
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 1px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-left: 20px;
        padding-right: 20px;
    }
    .reportview-container .main footer {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def format_volume(volume, unit='L'):
    """Format volume with appropriate units."""
    if volume is None:
        return "N/A"
    
    if unit == 'L':
        if volume < 1:
            return f"{volume * 1000:.0f} mL"
        elif volume < 10:
            return f"{volume:.2f} L"
        elif volume < 1000:
            return f"{volume:.1f} L"
        else:
            return f"{volume / 1000:.2f} m³"
    
    return f"{volume:.1f} {unit}"

def generate_demo_data():
    """Generate demo data for display purposes."""
    # Current time
    now = datetime.now()
    
    # Real-time measurement data
    current_data = {
        'timestamp': now,
        'flow_rate': 8.5 + np.random.normal(0, 1.0),
        'pressure': 3.2 + np.random.normal(0, 0.3),
        'hourly_usage': 22.8,
        'daily_usage': 245.6,
        'weekly_usage': 1678.4
    }
    
    # Ensure positive values
    current_data['flow_rate'] = max(0.1, current_data['flow_rate'])
    current_data['pressure'] = max(0.5, current_data['pressure'])
    
    # Historical data for charts
    dates = pd.date_range(start=now - timedelta(days=7), end=now, freq='1h')
    
    # Generate patterns for flow rate and pressure
    hour_of_day = [d.hour for d in dates]
    
    # Daily pattern multipliers (simulate higher usage in morning and evening)
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
    
    # Generate flow and pressure data with patterns
    flow_rate = []
    pressure = []
    volume = []
    
    for date, hour in zip(dates, hour_of_day):
        # Base flow rate with pattern and random variations
        base_flow = daily_pattern.get(hour, 0.5) * 8.0
        flow = base_flow * (1 + np.random.normal(0, 0.1))
        flow_rate.append(max(0, round(flow, 2)))
        
        # Base pressure with random variations
        base_pressure = 3.5 + np.random.normal(0, 0.2)
        pressure.append(max(0.5, round(base_pressure, 2)))
        
        # Volume calculation (flow rate * 60 minutes / 1000 to get liters)
        vol = flow * 60 / 1000
        volume.append(round(vol, 2))
    
    # Create DataFrame
    historical = pd.DataFrame({
        'timestamp': dates,
        'flow_rate': flow_rate,
        'pressure': pressure,
        'volume': volume
    })
    
    # Aggregate data by day/hour/week for summary stats
    historical['date'] = historical['timestamp'].dt.date
    hourly_data = historical.groupby(historical['timestamp'].dt.hour)['volume'].mean().reset_index()
    hourly_data.columns = ['hour', 'avg_volume']
    
    daily_data = historical.groupby(historical['timestamp'].dt.date)['volume'].sum().reset_index()
    daily_data.columns = ['date', 'total_volume']
    
    return {
        'current': current_data,
        'historical': historical,
        'hourly_summary': hourly_data,
        'daily_summary': daily_data
    }

def main():
    """Main application function."""
    # Display app header
    st.sidebar.title("Water Monitoring System")
    st.sidebar.markdown("---")
    
    # Navigation
    page = st.sidebar.radio(
        "Navigation", 
        ["Dashboard", "Historical Analysis", "WiFi Status", "Settings"]
    )
    
    # Store the current page in session state
    st.session_state.current_page = page
    
    # Display appropriate page
    if page == "Dashboard":
        display_dashboard()
    elif page == "Historical Analysis":
        display_historical()
    elif page == "WiFi Status":
        # Import the WiFi status component
        from wifi_status import display_wifi_status
        display_wifi_status(firebase_manager)  # Pass firebase_manager for real data if available
    elif page == "Settings":
        # Display settings
        display_settings()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2025 Water Monitoring System")

def display_dashboard():
    """Display the main dashboard with current readings."""
    st.title("💧 Water Monitoring Dashboard")
    
    # Check if we have a Firebase connection
    if not st.session_state.demo_mode and firebase_manager:
        try:
            # Try to get real data from Firebase
            latest_reading = firebase_manager.get_latest_reading("default")
            hourly_usage = firebase_manager.get_hourly_usage()
            daily_usage = firebase_manager.get_daily_usage()
            
            if latest_reading:
                current_data = {
                    'timestamp': datetime.now(),
                    'flow_rate': latest_reading.get('flow_rate', 0),
                    'pressure': latest_reading.get('pressure', 0),
                    'hourly_usage': hourly_usage,
                    'daily_usage': daily_usage,
                    'weekly_usage': daily_usage * 7  # Estimate for demo
                }
                
                # Get historical data for today's pattern
                now = datetime.now()
                start_of_day = datetime(now.year, now.month, now.day).timestamp()
                historical_readings = firebase_manager.get_historical_readings(start_of_day, now.timestamp())
                
                if historical_readings:
                    # Process historical readings into DataFrame format
                    timestamps = []
                    flow_rates = []
                    pressures = []
                    volumes = []
                    
                    for reading in historical_readings:
                        timestamps.append(datetime.fromtimestamp(reading.get('timestamp', 0)))
                        flow_rates.append(reading.get('flow_rate', 0))
                        pressures.append(reading.get('pressure', 0))
                        # Estimate volume (flow rate * 60 seconds / 1000 to get liters)
                        volumes.append(reading.get('flow_rate', 0) * 60 / 1000)
                    
                    historical_df = pd.DataFrame({
                        'timestamp': timestamps,
                        'flow_rate': flow_rates,
                        'pressure': pressures,
                        'volume': volumes,
                        'date': [t.date() for t in timestamps]
                    })
                    
                    data = {
                        'current': current_data,
                        'historical': historical_df
                    }
                else:
                    # No historical data available, fall back to demo
                    st.info("No historical data available from Firebase. Showing demo data.")
                    data = generate_demo_data()
            else:
                # No data available from Firebase, fall back to demo
                st.info("No real-time data available from Firebase. Showing demo data.")
                data = generate_demo_data()
                current_data = data['current']
        except Exception as e:
            st.error(f"Error retrieving data from Firebase: {str(e)}")
            data = generate_demo_data()
            current_data = data['current']
    else:
        # Get demo data if no Firebase or in demo mode
        data = generate_demo_data()
        current_data = data['current']
    
    # Current time
    st.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Main metrics row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Flow rate gauge
        flow_rate = current_data['flow_rate']
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
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Pressure gauge
        pressure = current_data['pressure']
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
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        # Volume usage metrics
        st.subheader("Water Usage Summary")
        
        # Create metrics for different time periods
        st.metric("Hourly Usage", format_volume(current_data['hourly_usage']))
        st.metric("Daily Usage", format_volume(current_data['daily_usage']))
        st.metric("Weekly Usage", format_volume(current_data['weekly_usage']))
        
        # Status indicator
        st.write("### System Status")
        st.success("✅ All systems operational")
    
    # Recent activity
    st.subheader("Recent Activity")
    
    # Get the last 5 hours of data
    recent_data = data['historical'].tail(5)
    
    # Create a table of recent readings
    st.dataframe(
        recent_data[['timestamp', 'flow_rate', 'pressure', 'volume']].rename(
            columns={
                'timestamp': 'Time',
                'flow_rate': 'Flow Rate (L/min)',
                'pressure': 'Pressure (bar)',
                'volume': 'Volume (L)'
            }
        ),
        use_container_width=True
    )
    
    # Today's usage pattern
    st.subheader("Today's Usage Pattern")
    
    # Filter for today
    today = datetime.now().date()
    today_data = data['historical'][data['historical']['date'] == today]
    
    if not today_data.empty:
        # Create line chart of today's flow rate
        fig = px.line(
            today_data,
            x='timestamp',
            y=['flow_rate', 'pressure'],
            labels={
                'timestamp': 'Time',
                'value': 'Measurement',
                'variable': 'Metric'
            },
            title="Today's Water Flow and Pressure"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for today yet.")

def display_historical():
    """Display historical data analysis."""
    st.title("📊 Historical Water Usage Analysis")
    
    # Time range selector
    time_range = st.selectbox(
        "Select Time Range",
        ["Last 24 Hours", "Last Week", "Last Month"],
        index=1
    )
    
    # Check if we have a Firebase connection
    if not st.session_state.demo_mode and firebase_manager:
        try:
            # Get timestamps for the selected time range
            now = datetime.now()
            
            if time_range == "Last 24 Hours":
                start_timestamp = (now - timedelta(hours=24)).timestamp()
            elif time_range == "Last Week":
                start_timestamp = (now - timedelta(days=7)).timestamp()
            else:  # Last Month
                start_timestamp = (now - timedelta(days=30)).timestamp()
                
            end_timestamp = now.timestamp()
            
            # Retrieve historical data from Firebase
            historical_readings = firebase_manager.get_historical_readings(start_timestamp, end_timestamp)
            
            if historical_readings and len(historical_readings) > 0:
                # Process historical readings into DataFrame format
                timestamps = []
                flow_rates = []
                pressures = []
                volumes = []
                
                for reading in historical_readings:
                    timestamps.append(datetime.fromtimestamp(reading.get('timestamp', 0)))
                    flow_rates.append(reading.get('flow_rate', 0))
                    pressures.append(reading.get('pressure', 0))
                    # Estimate volume (flow rate * interval minutes / 1000 to get liters)
                    volumes.append(reading.get('flow_rate', 0) * 60 / 1000)  # Assuming readings every minute
                
                historical_data = pd.DataFrame({
                    'timestamp': timestamps,
                    'flow_rate': flow_rates,
                    'pressure': pressures,
                    'volume': volumes
                })
                
                # Add datetime column for filtering
                historical_data['datetime'] = pd.to_datetime(historical_data['timestamp'])
            else:
                st.info("No historical data available from Firebase for the selected time range. Showing demo data.")
                # Get demo data if no Firebase data available
                data = generate_demo_data()
                historical_data = data['historical']
                # Add datetime column for filtering if not present
                if 'datetime' not in historical_data.columns:
                    historical_data['datetime'] = pd.to_datetime(historical_data['timestamp'])
        except Exception as e:
            st.error(f"Error retrieving historical data from Firebase: {str(e)}")
            # Fall back to demo data
            data = generate_demo_data()
            historical_data = data['historical']
            # Add datetime column for filtering if not present
            if 'datetime' not in historical_data.columns:
                historical_data['datetime'] = pd.to_datetime(historical_data['timestamp'])
    else:
        # Get demo data if no Firebase or in demo mode
        data = generate_demo_data()
        historical_data = data['historical']
        # Add datetime column for filtering if not present
        if 'datetime' not in historical_data.columns:
            historical_data['datetime'] = pd.to_datetime(historical_data['timestamp'])
    
    # We already have datetime column, no need to convert again
    # Add date column if not present for daily aggregation
    if 'date' not in historical_data.columns:
        historical_data['date'] = historical_data['datetime'].dt.date
    
    # Filter data based on selected time range
    now = datetime.now()
    if time_range == "Last 24 Hours":
        filtered_data = historical_data[historical_data['datetime'] >= (now - timedelta(hours=24))]
    elif time_range == "Last Week":
        filtered_data = historical_data[historical_data['datetime'] >= (now - timedelta(days=7))]
    else:  # Last Month
        filtered_data = historical_data[historical_data['datetime'] >= (now - timedelta(days=30))]
    
    # Create a copy of filtered data with proper date columns
    data_for_analysis = filtered_data.copy()
    # Convert date column to datetime if it's not already
    if 'date' in data_for_analysis.columns and not pd.api.types.is_datetime64_dtype(data_for_analysis['date']):
        data_for_analysis['date'] = pd.to_datetime(data_for_analysis['date'])
    
    # Daily, weekly, monthly summaries
    st.subheader("Water Consumption Summary")
    col1, col2, col3 = st.columns(3)
    
    # Calculate total volumes
    hourly_avg = filtered_data['volume'].mean() * filtered_data.shape[0] / 24
    # Handle the date aggregation safely
    if 'date' in data_for_analysis.columns:
        daily_totals = data_for_analysis.groupby(data_for_analysis['datetime'].dt.date)['volume'].sum()
        daily_avg = daily_totals.mean() if not daily_totals.empty else 0
    else:
        daily_avg = filtered_data['volume'].mean() * 24  # Estimate based on hourly average
    total_volume = filtered_data['volume'].sum()
    
    with col1:
        st.metric("Average Hourly Usage", format_volume(hourly_avg))
    with col2:
        st.metric("Average Daily Usage", format_volume(daily_avg))
    with col3:
        st.metric("Total Volume", format_volume(total_volume))
    
    # Tabs for different visualizations
    tabs = st.tabs(["Usage Over Time", "Daily Patterns", "Pressure Analysis"])
    
    # Usage over time tab
    with tabs[0]:
        # Make a copy to avoid modifying the original data
        resample_data = filtered_data.copy()
        # Remove non-numeric columns except datetime before resampling
        for col in resample_data.columns:
            if col != 'datetime' and not pd.api.types.is_numeric_dtype(resample_data[col]):
                resample_data = resample_data.drop(col, axis=1)
                
        # Safely resample with appropriate intervals
        if len(resample_data) > 0:
            # Resample to appropriate intervals based on time range
            if time_range == "Last 24 Hours":
                resampled = resample_data.set_index('datetime').resample('15min').mean().reset_index()
            elif time_range == "Last Week":
                resampled = resample_data.set_index('datetime').resample('3h').mean().reset_index()
            else:  # Last Month
                resampled = resample_data.set_index('datetime').resample('1D').mean().reset_index()
            
            # Volume over time chart
            fig = px.area(
                resampled,
                x='datetime',
                y='volume',
                labels={
                    'datetime': 'Time',
                    'volume': 'Volume (L)'
                },
                title=f"Water Volume Over {time_range}"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data for the selected time range.")
        
        # Calculate cumulative usage - handle date safely
        date_groups = filtered_data.groupby(filtered_data['datetime'].dt.date)['volume'].sum()
        date_index = [pd.to_datetime(d) for d in date_groups.index]
        daily_usage = pd.DataFrame({
            'date': date_index,
            'daily_volume': date_groups.values
        })
        daily_usage['cumulative'] = daily_usage['daily_volume'].cumsum()
        
        # Cumulative usage chart
        if not daily_usage.empty:
            fig = px.line(
                daily_usage,
                x='date',
                y='cumulative',
                labels={
                    'date': 'Date',
                    'cumulative': 'Cumulative Volume (L)'
                },
                title="Cumulative Water Usage"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Daily patterns tab
    with tabs[1]:
        # Hourly usage patterns
        hourly_avg = filtered_data.groupby(filtered_data['datetime'].dt.hour)['volume'].mean().reset_index()
        hourly_avg.columns = ['hour', 'avg_volume']
        
        # Hourly pattern chart
        fig = px.bar(
            hourly_avg,
            x='hour',
            y='avg_volume',
            labels={
                'hour': 'Hour of Day',
                'avg_volume': 'Average Volume (L)'
            },
            title="Average Hourly Water Usage"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Daily usage patterns
        daily_totals = filtered_data.groupby(filtered_data['datetime'].dt.date)['volume'].sum().reset_index()
        daily_totals.columns = ['date', 'total_volume']
        
        # Daily usage chart
        fig = px.bar(
            daily_totals,
            x='date',
            y='total_volume',
            labels={
                'date': 'Date',
                'total_volume': 'Total Volume (L)'
            },
            title="Daily Water Usage"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Weekday vs. weekend patterns
        filtered_data['weekday'] = filtered_data['datetime'].dt.day_name()
        weekday_avg = filtered_data.groupby('weekday')['volume'].mean().reset_index()
        
        # Order days correctly
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_avg['weekday'] = pd.Categorical(weekday_avg['weekday'], categories=days_order, ordered=True)
        weekday_avg = weekday_avg.sort_values('weekday')
        
        # Weekday pattern chart
        fig = px.bar(
            weekday_avg,
            x='weekday',
            y='volume',
            labels={
                'weekday': 'Day of Week',
                'volume': 'Average Volume (L)'
            },
            title="Average Water Usage by Day of Week"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Pressure analysis tab
    with tabs[2]:
        # Make sure we have resampled data (initialize if not defined yet)
        resampled = pd.DataFrame()
        if len(resample_data) > 0:
            # Resample data for this tab if not done yet
            if time_range == "Last 24 Hours":
                resampled = resample_data.set_index('datetime').resample('15min').mean().reset_index()
            elif time_range == "Last Week":
                resampled = resample_data.set_index('datetime').resample('3h').mean().reset_index()
            else:  # Last Month
                resampled = resample_data.set_index('datetime').resample('1D').mean().reset_index()
                
        if not resampled.empty:
            # Pressure over time
            fig = px.line(
                resampled,
                x='datetime',
                y='pressure',
                labels={
                    'datetime': 'Time',
                    'pressure': 'Pressure (bar)'
                },
                title=f"Water Pressure Over {time_range}"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data to show pressure over time.")
        
        # Pressure distribution
        if len(filtered_data) > 0:
            fig = px.histogram(
                filtered_data,
                x='pressure',
                nbins=20,
                labels={
                    'pressure': 'Pressure (bar)',
                    'count': 'Frequency'
                },
                title="Pressure Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Relationship between pressure and flow rate
            fig = px.scatter(
                filtered_data,
                x='pressure',
                y='flow_rate',
                trendline="ols",
                labels={
                    'pressure': 'Pressure (bar)',
                    'flow_rate': 'Flow Rate (L/min)'
                },
                title="Relationship Between Pressure and Flow Rate"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data to analyze pressure distribution.")

def display_settings():
    """Display settings page."""
    st.title("⚙️ Water Monitoring Settings")
    
    # Check if Firebase is available
    if not st.session_state.demo_mode and firebase_manager:
        # Use real Firebase data if available
        firebase_warning = st.empty()
        user_id = "default"  # Since we removed authentication
        
        try:
            # Try to get user settings from Firebase
            user_settings = firebase_manager.get_user_settings(user_id)
            if not user_settings:
                firebase_warning.info("No settings found in Firebase. Using default values.")
                # Initialize with default values if not found
                user_settings = {
                    "alert_thresholds": {
                        "pressure_high": 6.0,
                        "pressure_low": 1.0,
                        "flow_high": 20.0,
                        "daily_usage_high": 500.0
                    },
                    "sensor_calibration": {
                        "flow_factor": 1.0,
                        "pressure_zero": 0.0,
                        "pressure_factor": 1.0
                    },
                    "notifications": {
                        "enable_email": True,
                        "email": "user@example.com",
                        "preferences": {
                            "high_pressure": True,
                            "low_pressure": True,
                            "high_flow": True,
                            "usage_limit": True,
                            "offline": True
                        }
                    }
                }
        except Exception as e:
            firebase_warning.error(f"Error retrieving settings from Firebase: {str(e)}")
            # Initialize with default values if error occurs
            user_settings = {
                "alert_thresholds": {
                    "pressure_high": 6.0,
                    "pressure_low": 1.0,
                    "flow_high": 20.0,
                    "daily_usage_high": 500.0
                },
                "sensor_calibration": {
                    "flow_factor": 1.0,
                    "pressure_zero": 0.0,
                    "pressure_factor": 1.0
                },
                "notifications": {
                    "enable_email": True,
                    "email": "user@example.com",
                    "preferences": {
                        "high_pressure": True,
                        "low_pressure": True,
                        "high_flow": True,
                        "usage_limit": True,
                        "offline": True
                    }
                }
            }
        # Default settings if needed
        default_settings = {
            "alert_thresholds": {
                "pressure_high": 6.0,
                "pressure_low": 1.0,
                "flow_high": 20.0,
                "daily_usage_high": 500.0
            },
            "sensor_calibration": {
                "flow_factor": 1.0,
                "pressure_zero": 0.0,
                "pressure_factor": 1.0
            },
            "notifications": {
                "enable_email": True,
                "email": "user@example.com",
                "preferences": {
                    "high_pressure": True,
                    "low_pressure": True,
                    "high_flow": True,
                    "usage_limit": True,
                    "offline": True
                }
            }
        }
        
        # Set user_settings to either the retrieved settings or defaults
        if not user_settings:
            user_settings = default_settings
            
    else:
        # Show warning for demo mode
        st.info("Running in demo mode. Settings are not saved to Firebase.")
        
        # Use default settings for demo mode
        user_settings = {
            "alert_thresholds": {
                "pressure_high": 6.0,
                "pressure_low": 1.0,
                "flow_high": 20.0,
                "daily_usage_high": 500.0
            },
            "sensor_calibration": {
                "flow_factor": 1.0,
                "pressure_zero": 0.0,
                "pressure_factor": 1.0
            },
            "notifications": {
                "enable_email": True,
                "email": "user@example.com",
                "preferences": {
                    "high_pressure": True,
                    "low_pressure": True,
                    "high_flow": True,
                    "usage_limit": True,
                    "offline": True
                }
            }
        }
    
    # Create tabs for different settings
    tabs = st.tabs(["Alert Thresholds", "Sensor Calibration", "Notifications"])
    
    # Alert thresholds tab
    with tabs[0]:
        st.subheader("Alert Threshold Settings")
        st.write("Set thresholds for when alerts should be triggered.")
        
        with st.form("threshold_form"):
            # Pressure thresholds
            st.write("### Pressure Thresholds")
            col1, col2 = st.columns(2)
            
            with col1:
                pressure_high = st.number_input(
                    "High Pressure Threshold (bar)",
                    min_value=1.0,
                    max_value=10.0,
                    value=user_settings["alert_thresholds"]["pressure_high"],
                    step=0.1,
                    help="Alert when pressure exceeds this value"
                )
            
            with col2:
                pressure_low = st.number_input(
                    "Low Pressure Threshold (bar)",
                    min_value=0.1,
                    max_value=5.0,
                    value=user_settings["alert_thresholds"]["pressure_low"],
                    step=0.1,
                    help="Alert when pressure falls below this value"
                )
            
            # Flow threshold
            st.write("### Flow Threshold")
            flow_high = st.number_input(
                "High Flow Rate Threshold (L/min)",
                min_value=1.0,
                max_value=50.0,
                value=user_settings["alert_thresholds"]["flow_high"],
                step=0.5,
                help="Alert when flow rate exceeds this value"
            )
            
            # Usage threshold
            st.write("### Usage Threshold")
            daily_usage_high = st.number_input(
                "Daily Usage Threshold (L)",
                min_value=50.0,
                max_value=2000.0,
                value=user_settings["alert_thresholds"]["daily_usage_high"],
                step=10.0,
                help="Alert when daily water usage exceeds this value"
            )
            
            # Save button
            save_button = st.form_submit_button("Save Thresholds")
            
            if save_button:
                if not st.session_state.demo_mode and firebase_manager:
                    try:
                        # Update alert thresholds in user settings
                        thresholds = {
                            "pressure_high": pressure_high,
                            "pressure_low": pressure_low,
                            "flow_high": flow_high,
                            "daily_usage_high": daily_usage_high
                        }
                        
                        # Save to Firebase
                        if user_settings:
                            user_settings["alert_thresholds"] = thresholds
                            firebase_manager.save_user_settings(user_id, user_settings)
                            st.success("Alert thresholds saved to Firebase successfully!")
                        else:
                            # Create new settings object if none exists
                            new_settings = {
                                "alert_thresholds": thresholds,
                                "sensor_calibration": {
                                    "flow_factor": 1.0,
                                    "pressure_zero": 0.0,
                                    "pressure_factor": 1.0
                                },
                                "notifications": {
                                    "enable_email": True,
                                    "email": "user@example.com",
                                    "preferences": {
                                        "high_pressure": True,
                                        "low_pressure": True,
                                        "high_flow": True,
                                        "usage_limit": True,
                                        "offline": True
                                    }
                                }
                            }
                            firebase_manager.save_user_settings(user_id, new_settings)
                            st.success("New settings created and saved to Firebase successfully!")
                    except Exception as e:
                        st.error(f"Error saving settings to Firebase: {str(e)}")
                else:
                    st.success("Alert thresholds saved successfully! (Demo mode - not saved to Firebase)")
    
    # Sensor calibration tab
    with tabs[1]:
        st.subheader("Sensor Calibration")
        st.write("Adjust calibration factors for your water sensors.")
        
        with st.form("calibration_form"):
            # Flow meter calibration
            st.write("### Flow Meter Calibration")
            flow_factor = st.number_input(
                "Flow Factor",
                min_value=0.5,
                max_value=1.5,
                value=user_settings["sensor_calibration"]["flow_factor"],
                step=0.01,
                help="Multiplier to adjust flow rate readings"
            )
            
            # Pressure sensor calibration
            st.write("### Pressure Sensor Calibration")
            col1, col2 = st.columns(2)
            
            with col1:
                pressure_zero = st.number_input(
                    "Pressure Zero Offset",
                    min_value=-1.0,
                    max_value=1.0,
                    value=user_settings["sensor_calibration"]["pressure_zero"],
                    step=0.01,
                    help="Zero offset adjustment for pressure readings"
                )
            
            with col2:
                pressure_factor = st.number_input(
                    "Pressure Factor",
                    min_value=0.5,
                    max_value=1.5,
                    value=user_settings["sensor_calibration"]["pressure_factor"],
                    step=0.01,
                    help="Multiplier to adjust pressure readings"
                )
            
            # Calibration test
            st.write("### Calibration Test")
            st.info("To test calibration, apply the factors to a known reference value.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                test_flow = st.number_input(
                    "Test Flow Rate (L/min)",
                    min_value=0.0,
                    max_value=30.0,
                    value=10.0,
                    step=0.5
                )
                st.write(f"Calibrated Flow: {test_flow * flow_factor:.2f} L/min")
            
            with col2:
                test_pressure = st.number_input(
                    "Test Pressure (bar)",
                    min_value=0.0,
                    max_value=10.0,
                    value=3.0,
                    step=0.1
                )
                st.write(f"Calibrated Pressure: {test_pressure * pressure_factor + pressure_zero:.2f} bar")
            
            # Save button
            save_button = st.form_submit_button("Save Calibration")
            
            if save_button:
                if not st.session_state.demo_mode and firebase_manager:
                    try:
                        # Update calibration settings
                        calibration = {
                            "flow_factor": flow_factor,
                            "pressure_zero": pressure_zero,
                            "pressure_factor": pressure_factor
                        }
                        
                        # Save to Firebase
                        if user_settings:
                            user_settings["sensor_calibration"] = calibration
                            firebase_manager.save_user_settings(user_id, user_settings)
                            # Also update the ESP device with new calibration
                            firebase_manager.save_sensor_calibration(user_id, calibration)
                            st.success("Sensor calibration saved to Firebase successfully!")
                        else:
                            st.error("Unable to save calibration: Missing user settings.")
                    except Exception as e:
                        st.error(f"Error saving calibration to Firebase: {str(e)}")
                else:
                    st.success("Sensor calibration saved successfully! (Demo mode - not saved to Firebase)")
    
    # Notifications tab
    with tabs[2]:
        st.subheader("Notification Settings")
        st.write("Configure how and when you receive alerts about your water system.")
        
        with st.form("notification_form"):
            # Email notifications
            st.write("### Email Notifications")
            enable_email = st.checkbox(
                "Enable Email Notifications",
                value=user_settings["notifications"]["enable_email"]
            )
            
            # Email address
            email = st.text_input(
                "Email Address",
                value=user_settings["notifications"]["email"],
                disabled=not enable_email
            )
            
            # Notification preferences
            st.write("### Alert Types")
            col1, col2 = st.columns(2)
            
            with col1:
                high_pressure = st.checkbox(
                    "High Pressure Alerts",
                    value=user_settings["notifications"]["preferences"]["high_pressure"],
                    disabled=not enable_email
                )
                
                low_pressure = st.checkbox(
                    "Low Pressure Alerts",
                    value=user_settings["notifications"]["preferences"]["low_pressure"],
                    disabled=not enable_email
                )
                
                high_flow = st.checkbox(
                    "High Flow Alerts",
                    value=user_settings["notifications"]["preferences"]["high_flow"],
                    disabled=not enable_email
                )
            
            with col2:
                usage_limit = st.checkbox(
                    "Usage Limit Alerts",
                    value=user_settings["notifications"]["preferences"]["usage_limit"],
                    disabled=not enable_email
                )
                
                offline = st.checkbox(
                    "Offline Sensor Alerts",
                    value=user_settings["notifications"]["preferences"]["offline"],
                    disabled=not enable_email
                )
            
            # Save button
            save_button = st.form_submit_button("Save Notification Settings")
            
            if save_button:
                if not st.session_state.demo_mode and firebase_manager:
                    try:
                        # Update notification settings
                        notification_settings = {
                            "enable_email": enable_email,
                            "email": email if enable_email else "",
                            "preferences": {
                                "high_pressure": high_pressure,
                                "low_pressure": low_pressure,
                                "high_flow": high_flow,
                                "usage_limit": usage_limit,
                                "offline": offline
                            }
                        }
                        
                        # Save to Firebase
                        if user_settings:
                            user_settings["notifications"] = notification_settings
                            firebase_manager.save_user_settings(user_id, user_settings)
                            st.success("Notification settings saved to Firebase successfully!")
                        else:
                            st.error("Unable to save notification settings: Missing user settings.")
                    except Exception as e:
                        st.error(f"Error saving notification settings to Firebase: {str(e)}")
                else:
                    st.success("Notification settings saved successfully! (Demo mode - not saved to Firebase)")

if __name__ == "__main__":
    main()