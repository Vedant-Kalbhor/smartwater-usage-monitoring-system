import json
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from firebase_manager import FirebaseManager

class ESPManager:
    """
    Manager class for handling ESP8266 device communication and data.
    """
    
    def __init__(self, firebase_manager: FirebaseManager = None):
        """
        Initialize the ESP Manager.
        
        Args:
            firebase_manager: Instance of FirebaseManager for database access
        """
        self.firebase_manager = firebase_manager
        self.device_info = {}
        self.last_reading = {}
        self.connection_status = {
            "connected": False,
            "last_seen": None,
            "signal_strength": 0,
            "ip_address": "",
            "firmware_version": "",
        }
    
    def get_device_status(self, device_id="default"):
        """
        Get the current status of an ESP8266 device.
        
        Args:
            device_id: ID of the ESP device to check
            
        Returns:
            dict: Device status information
        """
        if self.firebase_manager:
            try:
                # Get device info from Firebase
                device_data = self.firebase_manager.get_device_status(device_id)
                if device_data:
                    self.device_info = device_data
                    
                    # Update connection status
                    last_seen_timestamp = device_data.get("last_update", 0)
                    last_seen = datetime.fromtimestamp(last_seen_timestamp)
                    current_time = datetime.now()
                    time_diff = (current_time - last_seen).total_seconds()
                    
                    # If we've heard from the device in the last 2 minutes, consider it connected
                    self.connection_status["connected"] = time_diff < 120
                    self.connection_status["last_seen"] = last_seen
                    self.connection_status["signal_strength"] = device_data.get("rssi", 0)
                    self.connection_status["ip_address"] = device_data.get("ip_address", "")
                    self.connection_status["firmware_version"] = device_data.get("firmware_version", "")
                    
                    return self.connection_status
            except Exception as e:
                print(f"Error getting device status: {e}")
        
        # Return demo data if no Firebase connection or error
        return self.generate_demo_device_status()
    
    def get_latest_reading(self, device_id="default"):
        """
        Get the latest sensor reading from an ESP8266 device.
        
        Args:
            device_id: ID of the ESP device
            
        Returns:
            dict: Latest sensor reading
        """
        if self.firebase_manager:
            try:
                # Get latest reading from Firebase
                latest_reading = self.firebase_manager.get_latest_reading(device_id)
                if latest_reading:
                    self.last_reading = latest_reading
                    return self.last_reading
            except Exception as e:
                print(f"Error getting latest reading: {e}")
        
        # Return demo data if no Firebase connection or error
        return self.generate_demo_sensor_reading()
    
    def get_connection_history(self, device_id="default", hours=24):
        """
        Get WiFi connection history for an ESP8266 device.
        
        Args:
            device_id: ID of the ESP device
            hours: Number of hours of history to retrieve
            
        Returns:
            DataFrame: Connection history with timestamps and signal strength
        """
        if self.firebase_manager:
            try:
                # Get connection logs from Firebase
                connection_logs = self.firebase_manager.get_connection_logs(device_id, hours)
                if connection_logs:
                    # Process and return the real data
                    df = pd.DataFrame(connection_logs)
                    return df
            except Exception as e:
                print(f"Error getting connection history: {e}")
        
        # Return demo data if no Firebase connection or error
        return self.generate_demo_connection_history(hours)
    
    def get_sensor_readings(self, device_id="default", start_time=None, end_time=None):
        """
        Get historical sensor readings from an ESP8266 device.
        
        Args:
            device_id: ID of the ESP device
            start_time: Start timestamp for data retrieval
            end_time: End timestamp for data retrieval
            
        Returns:
            DataFrame: Historical sensor readings
        """
        if not start_time:
            start_time = datetime.now() - timedelta(days=7)
        if not end_time:
            end_time = datetime.now()
            
        if self.firebase_manager:
            try:
                # Get sensor readings from Firebase
                readings = self.firebase_manager.get_historical_readings(
                    start_time.timestamp(),
                    end_time.timestamp()
                )
                
                if readings:
                    # Process and return the real data
                    df = pd.DataFrame(readings)
                    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
                    return df
            except Exception as e:
                print(f"Error getting sensor readings: {e}")
        
        # Return demo data if no Firebase connection or error
        return self.generate_demo_sensor_readings(start_time, end_time)
    
    def send_command(self, device_id="default", command="restart", params=None):
        """
        Send a command to an ESP8266 device.
        
        Args:
            device_id: ID of the ESP device
            command: Command to send
            params: Additional parameters for the command
            
        Returns:
            bool: Success status
        """
        if not params:
            params = {}
            
        if self.firebase_manager:
            try:
                command_data = {
                    "command": command,
                    "params": params,
                    "timestamp": int(time.time()),
                    "status": "pending"
                }
                
                return self.firebase_manager.send_device_command(device_id, command_data)
            except Exception as e:
                print(f"Error sending command: {e}")
                return False
        
        # Mock successful command if no Firebase
        print(f"[DEMO] Command {command} sent to device {device_id}")
        return True
    
    def update_calibration(self, calibration_data):
        """
        Update sensor calibration values in Firebase.
        
        Args:
            calibration_data: Dictionary with calibration values
            
        Returns:
            bool: Success status
        """
        if self.firebase_manager:
            try:
                return self.firebase_manager.save_sensor_calibration(
                    "default",  # Default user ID
                    calibration_data
                )
            except Exception as e:
                print(f"Error updating calibration: {e}")
                return False
        
        # Mock successful update if no Firebase
        print(f"[DEMO] Calibration updated: {calibration_data}")
        return True
        
    def generate_demo_device_status(self):
        """Generate demo device status data for testing."""
        now = datetime.now()
        connected = np.random.choice([True, True, True, False], p=[0.8, 0.1, 0.05, 0.05])
        last_seen = now if connected else now - timedelta(minutes=np.random.randint(5, 60))
        
        return {
            "connected": connected,
            "last_seen": last_seen,
            "signal_strength": -65 + np.random.normal(0, 5),
            "ip_address": "192.168.1.25" if connected else "Unknown",
            "firmware_version": "1.0.3"
        }
    
    def generate_demo_sensor_reading(self):
        """Generate demo sensor reading for testing."""
        now = datetime.now()
        hour = now.hour
        
        # Create a realistic daily pattern
        hour_factor = {
            0: 0.3, 1: 0.2, 2: 0.1, 3: 0.1, 4: 0.2, 5: 0.5,
            6: 1.0, 7: 1.5, 8: 1.2, 9: 0.8, 10: 0.7, 11: 0.8,
            12: 1.0, 13: 0.9, 14: 0.7, 15: 0.6, 16: 0.7, 17: 1.2,
            18: 1.8, 19: 1.5, 20: 1.2, 21: 0.9, 22: 0.6, 23: 0.4
        }
        
        # Base flow with time-appropriate pattern
        base_flow = hour_factor.get(hour, 0.5) * 8.0
        flow_rate = max(0.1, base_flow * (1 + np.random.normal(0, 0.1)))
        
        # Base pressure with some random variation
        pressure = max(0.5, 3.5 + np.random.normal(0, 0.2))
        
        # Calculate some cumulative volumes
        hourly_usage = flow_rate * 60 / 1000  # L per minute * 60 min / 1000 to convert to cubic meters
        daily_usage = hourly_usage * 24 * 0.7  # 70% of theoretical maximum daily usage
        
        return {
            "timestamp": int(now.timestamp()),
            "flow_rate": round(flow_rate, 2),
            "pressure": round(pressure, 2),
            "hourly_usage": round(hourly_usage, 2),
            "daily_usage": round(daily_usage, 2),
            "total_volume": round(daily_usage * 30, 2),  # Simulate a month of usage
            "battery": 85 + np.random.randint(-5, 5)  # Battery percentage
        }
    
    def generate_demo_connection_history(self, hours=24):
        """Generate demo connection history for testing."""
        now = datetime.now()
        timestamps = [now - timedelta(hours=i) for i in range(hours, 0, -1)]
        
        # Random signal strengths with some correlation
        base_signal = -65
        signal_strengths = []
        connected_values = []
        
        for i in range(len(timestamps)):
            if i > 0:
                # Add some correlation with previous value
                base_signal = 0.9 * base_signal + 0.1 * (-65 + np.random.normal(0, 3))
            
            # Apply random variation
            signal = base_signal + np.random.normal(0, 3)
            signal = max(-100, min(-40, signal))
            signal_strengths.append(signal)
            
            # Determine if connected
            is_connected = True
            if signal < -85:
                # Very weak signal might mean disconnection
                is_connected = np.random.choice([True, False], p=[0.3, 0.7])
            
            # Occasionally add random disconnections
            if np.random.random() < 0.05:
                is_connected = False
                
            connected_values.append(is_connected)
        
        return pd.DataFrame({
            'timestamp': timestamps,
            'signal_strength': signal_strengths,
            'connected': connected_values
        })
    
    def generate_demo_sensor_readings(self, start_time, end_time):
        """Generate demo sensor readings for a time range."""
        # Create a date range with hourly samples
        date_range = pd.date_range(start=start_time, end=end_time, freq='1h')
        
        # Create patterns for flow rate and pressure
        hour_of_day = [d.hour for d in date_range]
        
        # Daily pattern multipliers
        daily_pattern = {
            0: 0.3, 1: 0.2, 2: 0.1, 3: 0.1, 4: 0.2, 5: 0.5,
            6: 1.0, 7: 1.5, 8: 1.2, 9: 0.8, 10: 0.7, 11: 0.8,
            12: 1.0, 13: 0.9, 14: 0.7, 15: 0.6, 16: 0.7, 17: 1.2,
            18: 1.8, 19: 1.5, 20: 1.2, 21: 0.9, 22: 0.6, 23: 0.4
        }
        
        # Generate data
        flow_rates = []
        pressures = []
        volumes = []
        timestamps = []
        
        for date, hour in zip(date_range, hour_of_day):
            # Base flow rate with pattern and random variations
            base_flow = daily_pattern.get(hour, 0.5) * 8.0
            flow = base_flow * (1 + np.random.normal(0, 0.1))
            flow_rates.append(max(0, round(flow, 2)))
            
            # Base pressure with random variations
            base_pressure = 3.5 + np.random.normal(0, 0.2)
            pressures.append(max(0.5, round(base_pressure, 2)))
            
            # Volume calculation (flow rate * 60 minutes / 1000 to get liters)
            vol = flow * 60 / 1000
            volumes.append(round(vol, 3))
            
            # Unix timestamp
            timestamps.append(int(date.timestamp()))
        
        # Create DataFrame
        return pd.DataFrame({
            'timestamp': timestamps,
            'datetime': date_range,
            'flow_rate': flow_rates,
            'pressure': pressures,
            'volume': volumes
        })