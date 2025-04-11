import pandas as pd
import numpy as np
from datetime import datetime
from firebase_manager import FirebaseManager

def get_real_time_data(firebase_manager: FirebaseManager):
    """
    Get real-time data from the Firebase database.
    
    Args:
        firebase_manager: Instance of FirebaseManager for database access
        
    Returns:
        dict: Dictionary containing the latest sensor readings
    """
    try:
        # In demo mode, generate random data
        if 'demo_mode' in pd.Series.__dict__ and pd.Series.__dict__['demo_mode']:
            return generate_demo_realtime_data()
        
        # Get latest readings from Firebase
        latest_data = firebase_manager.get_latest_readings()
        
        if not latest_data:
            return None
        
        # Get hourly and daily usage for context
        hourly_usage = firebase_manager.get_hourly_usage()
        daily_usage = firebase_manager.get_daily_usage()
        
        # Add usage to data
        latest_data['hourly_usage'] = hourly_usage
        latest_data['daily_usage'] = daily_usage
        
        return latest_data
        
    except Exception as e:
        print(f"Error getting real-time data: {str(e)}")
        return None

def get_historical_data(firebase_manager: FirebaseManager, start_date, end_date):
    """
    Get historical data for a specified date range.
    
    Args:
        firebase_manager: Instance of FirebaseManager for database access
        start_date: Start date for historical data
        end_date: End date for historical data
        
    Returns:
        DataFrame: Pandas DataFrame containing historical data
    """
    try:
        # In demo mode, generate random historical data
        if 'demo_mode' in pd.Series.__dict__ and pd.Series.__dict__['demo_mode']:
            return generate_demo_historical_data(start_date, end_date)
        
        # Get readings from Firebase for the specified date range
        readings = firebase_manager.get_historical_readings(start_date, end_date)
        
        if not readings:
            return pd.DataFrame()
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(readings)
        
        # Ensure timestamps are sorted
        if 'timestamp' in df.columns:
            df = df.sort_values('timestamp')
        
        return df
        
    except Exception as e:
        print(f"Error getting historical data: {str(e)}")
        return pd.DataFrame()

def resample_data(df, frequency='1H'):
    """
    Resample data to a specified frequency.
    
    Args:
        df: DataFrame with datetime index
        frequency: Pandas frequency string (e.g., '1H' for hourly, '1D' for daily)
        
    Returns:
        DataFrame: Resampled DataFrame
    """
    try:
        if df.empty:
            return df
        
        # Ensure DataFrame has a datetime index
        if 'datetime' not in df.columns and not isinstance(df.index, pd.DatetimeIndex):
            if 'timestamp' in df.columns:
                df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
                df.set_index('datetime', inplace=True)
            else:
                return df  # Can't resample without a datetime column
        
        # Resample data
        resampled = df.resample(frequency).mean()
        
        # Fill NaN values
        resampled = resampled.fillna(method='ffill')
        
        return resampled
        
    except Exception as e:
        print(f"Error resampling data: {str(e)}")
        return df

def detect_anomalies(df, column, window=20, threshold=3.0):
    """
    Detect anomalies in time series data using a rolling z-score method.
    
    Args:
        df: DataFrame with the time series data
        column: Column name to check for anomalies
        window: Rolling window size
        threshold: Z-score threshold for anomaly detection
        
    Returns:
        Series: Boolean series where True indicates an anomaly
    """
    try:
        if df.empty or column not in df.columns:
            return pd.Series(index=df.index)
        
        # Calculate rolling mean and standard deviation
        rolling_mean = df[column].rolling(window=window, center=True).mean()
        rolling_std = df[column].rolling(window=window, center=True).std()
        
        # Calculate z-scores
        z_scores = (df[column] - rolling_mean) / rolling_std
        
        # Identify anomalies where z-score exceeds threshold
        anomalies = abs(z_scores) > threshold
        
        return anomalies
        
    except Exception as e:
        print(f"Error detecting anomalies: {str(e)}")
        return pd.Series(False, index=df.index)

def generate_demo_realtime_data():
    """Generate demo real-time data for testing."""
    now = datetime.now().timestamp()
    
    # Random values for flow rate and pressure
    flow_rate = 8.5 + np.random.normal(0, 1.0)
    pressure = 3.2 + np.random.normal(0, 0.3)
    
    # Ensure positive values
    flow_rate = max(0.1, flow_rate)
    pressure = max(0.5, pressure)
    
    # Create data dictionary
    data = {
        'timestamp': now,
        'flow_rate': round(flow_rate, 2),
        'pressure': round(pressure, 2),
        'volume': round(flow_rate * 60 / 1000, 2),  # L/min to L
        'hourly_usage': round(22.8 + np.random.normal(0, 3.0), 2),
        'daily_usage': round(245.6 + np.random.normal(0, 10.0), 2)
    }
    
    return data

def generate_demo_historical_data(start_timestamp, end_timestamp):
    """Generate demo historical data for testing."""
    # Convert timestamps to datetime
    start_date = datetime.fromtimestamp(start_timestamp)
    end_date = datetime.fromtimestamp(end_timestamp)
    
    # Generate a date range with hourly frequency
    dates = pd.date_range(start=start_date, end=end_date, freq='1H')
    timestamps = [d.timestamp() for d in dates]
    
    # Generate flow rate with daily patterns
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
    
    # Generate data with patterns
    flow_rate = []
    pressure = []
    volume = []
    hourly_usage = []
    daily_usage = []
    
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
        flow_rate.append(max(0, round(flow, 2)))
        
        # Base pressure with random variations
        base_pressure = 3.5 + np.random.normal(0, 0.2)
        pressure.append(max(0.5, round(base_pressure, 2)))
        
        # Volume calculation
        vol = round(flow * 60 / 1000, 2)  # L/min to L
        volume.append(vol)
        
        # Update hourly and daily usage
        hourly_sum += vol
        daily_sum += vol
        
        hourly_usage.append(round(hourly_sum, 2))
        daily_usage.append(round(daily_sum, 2))
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'flow_rate': flow_rate,
        'pressure': pressure,
        'volume': volume,
        'hourly_usage': hourly_usage,
        'daily_usage': daily_usage
    })
    
    # Add some anomalies for demonstration
    anomaly_indices = np.random.choice(len(df), size=3, replace=False)
    for idx in anomaly_indices:
        if idx > 0:  # Skip the first entry
            df.loc[idx, 'flow_rate'] = df.loc[idx, 'flow_rate'] * 3
            df.loc[idx, 'pressure'] = df.loc[idx, 'pressure'] * 1.5
    
    return df