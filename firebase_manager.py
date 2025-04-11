import json
import os
import time
import requests
from datetime import datetime, timedelta
import uuid
import random

class FirebaseManager:
    """
    Firebase manager class that works with both real Firebase data and demo data.
    """
    
    def __init__(self, api_key=None, auth_domain=None, database_url=None, storage_bucket=None, service_account_key=None):
        """
        Initialize Firebase connection with provided credentials.
        
        Args:
            api_key: Firebase API key
            auth_domain: Firebase auth domain
            database_url: Firebase database URL
            storage_bucket: Firebase storage bucket
            service_account_key: Firebase service account key (JSON string)
        """
        self.config = {
            "apiKey": api_key,
            "authDomain": auth_domain,
            "databaseURL": database_url,
            "storageBucket": storage_bucket
        }
        
        # Check for Firebase Database Secret
        self.database_secret = os.getenv("FIREBASE_DATABASE_SECRET")
        
        # Flag for demo mode - use real data if we have all required credentials
        self.demo_mode = not all([database_url, self.database_secret])
        print(f"Firebase Manager initialized in {'demo' if self.demo_mode else 'live'} mode")
    
    def login_user(self, email, password):
        """
        Mock authentication with email and password for demo mode.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            dict: User information if authentication succeeds
        """
        # For demo mode, accept any valid-looking email/password
        if self.demo_mode:
            if '@' in email and len(password) >= 6:
                return {
                    'localId': 'demo-user-id',
                    'email': email,
                    'displayName': email.split('@')[0],
                    'idToken': f"demo-token-{uuid.uuid4()}",
                    'refreshToken': f"demo-refresh-{uuid.uuid4()}",
                    'expiresIn': '3600'
                }
            else:
                print("Demo login failed: Invalid email or password too short")
                return None
        
        print("Real Firebase authentication not implemented")
        return None
    
    def create_user(self, email, password):
        """
        Mock user creation for demo mode.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            dict: User information if creation succeeds
        """
        # For demo mode, pretend to create a user
        if self.demo_mode:
            if '@' in email and len(password) >= 6:
                user_id = f"demo-user-{uuid.uuid4()}"
                return {
                    'localId': user_id,
                    'email': email,
                    'displayName': email.split('@')[0],
                    'idToken': f"demo-token-{uuid.uuid4()}",
                    'refreshToken': f"demo-refresh-{uuid.uuid4()}",
                    'expiresIn': '3600'
                }
            else:
                print("Demo user creation failed: Invalid email or password too short")
                return None
                
        print("Real Firebase user creation not implemented")
        return None
    
    def reset_password(self, email):
        """
        Mock password reset for demo mode.
        
        Args:
            email: User email
        """
        # For demo mode, pretend to send a reset email
        if self.demo_mode:
            if '@' in email:
                print(f"[DEMO] Password reset email sent to {email}")
                return True
            else:
                print(f"Demo password reset failed: Invalid email")
                raise ValueError("Invalid email format")
        
        print("Real Firebase password reset not implemented")
        raise NotImplementedError("Firebase connection required")
    
    def change_password(self, email, current_password, new_password):
        """
        Mock password change for demo mode.
        
        Args:
            email: User email
            current_password: Current password
            new_password: New password
        """
        # For demo mode, pretend to change password
        if self.demo_mode:
            if '@' in email and len(current_password) >= 6 and len(new_password) >= 6:
                print(f"[DEMO] Password changed for {email}")
                return True
            else:
                print(f"Demo password change failed: Invalid email or password too short")
                raise ValueError("Invalid email format or password too short")
        
        print("Real Firebase password change not implemented")
        raise NotImplementedError("Firebase connection required")
    
    def get_latest_readings(self):
        """
        Get the latest sensor readings (mock data for demo mode).
        
        Returns:
            dict: Latest sensor readings
        """
        # For demo mode, generate random readings
        if self.demo_mode:
            now = datetime.now()
            return {
                'timestamp': now.timestamp(),
                'flow_rate': 8.5 + random.uniform(-1.0, 1.0),
                'pressure': 3.2 + random.uniform(-0.3, 0.3),
                'temperature': 21.5 + random.uniform(-0.5, 0.5)
            }
        
        print("Real Firebase readings not implemented")
        return None
    
    def get_hourly_usage(self):
        """
        Get the water usage for the current hour from Firebase.
        
        Returns:
            float: Water usage in liters
        """
        # For demo mode, generate random hourly usage
        if self.demo_mode:
            hour = datetime.now().hour
            
            # Simulate typical daily water usage pattern
            hour_factors = {
                0: 0.2, 1: 0.1, 2: 0.1, 3: 0.1, 4: 0.2, 5: 0.5,
                6: 1.2, 7: 1.5, 8: 1.2, 9: 0.8, 10: 0.7, 11: 0.8,
                12: 1.0, 13: 0.9, 14: 0.7, 15: 0.6, 16: 0.7, 17: 1.0,
                18: 1.5, 19: 1.2, 20: 1.0, 21: 0.8, 22: 0.5, 23: 0.3
            }
            
            base_usage = 25.0  # Base hourly usage in liters
            return base_usage * hour_factors.get(hour, 1.0) * random.uniform(0.8, 1.2)
        
        try:
            # Get the current hour timestamp range
            now = datetime.now()
            start_of_hour = datetime(now.year, now.month, now.day, now.hour).timestamp()
            
            # Calculate usage by fetching readings in the current hour
            return self._calculate_usage_for_period(start_of_hour, now.timestamp())
        except Exception as e:
            print(f"Error getting hourly usage from Firebase: {str(e)}")
            return 0.0
    
    def get_daily_usage(self):
        """
        Get the water usage for the current day from Firebase.
        
        Returns:
            float: Water usage in liters
        """
        # For demo mode, generate random daily usage
        if self.demo_mode:
            # Simulate a reasonable daily water usage with some randomness
            weekday = datetime.now().weekday()
            
            # Simulate different usage patterns on different days
            day_factors = {0: 1.0, 1: 0.9, 2: 1.1, 3: 1.0, 4: 1.2, 5: 1.5, 6: 1.3}
            
            base_usage = 240.0  # Base daily usage in liters
            return base_usage * day_factors.get(weekday, 1.0) * random.uniform(0.9, 1.1)
        
        try:
            # Get the current day timestamp range
            now = datetime.now()
            start_of_day = datetime(now.year, now.month, now.day).timestamp()
            
            # Calculate usage by fetching readings for the current day
            return self._calculate_usage_for_period(start_of_day, now.timestamp())
        except Exception as e:
            print(f"Error getting daily usage from Firebase: {str(e)}")
            return 0.0
            
    def _calculate_usage_for_period(self, start_timestamp, end_timestamp):
        """
        Helper method to calculate total water usage for a period by
        fetching readings and calculating the difference in total volume.
        
        Args:
            start_timestamp: Start of period timestamp
            end_timestamp: End of period timestamp
            
        Returns:
            float: Water usage in liters for the period
        """
        # Fetch readings for the period
        readings = self.get_historical_readings(start_timestamp, end_timestamp)
        
        if not readings:
            return 0.0
            
        # Sort readings by timestamp to ensure correct ordering
        readings.sort(key=lambda x: x.get('timestamp', 0))
        
        # If we only have one reading, we can't calculate usage
        if len(readings) < 2:
            return 0.0
            
        # Calculate the difference between the first and last reading's total volume
        first_reading = readings[0]
        last_reading = readings[-1]
        
        first_volume = first_reading.get('total_volume', 0)
        last_volume = last_reading.get('total_volume', 0)
        
        # Calculate the difference (usage)
        usage = max(0, last_volume - first_volume)  # Ensure non-negative
        
        return usage
    
    def get_historical_readings(self, start_timestamp, end_timestamp):
        """
        Get historical sensor readings for a specified time range from Firebase.
        
        Args:
            start_timestamp: Start timestamp
            end_timestamp: End timestamp
            
        Returns:
            list: List of readings
        """
        # For demo mode, generate random historical readings
        if self.demo_mode:
            readings = []
            start_time = datetime.fromtimestamp(start_timestamp)
            end_time = datetime.fromtimestamp(end_timestamp)
            
            # Determine interval based on date range
            delta = end_time - start_time
            if delta.days > 7:
                # Hourly readings for larger ranges
                interval = timedelta(hours=1)
            else:
                # More frequent readings for smaller ranges
                interval = timedelta(minutes=15)
            
            current = start_time
            while current <= end_time:
                # Generate reading with some pattern
                hour = current.hour
                
                # Flow rate varies by hour with some randomness
                hour_factor = 0.5 + 0.5 * abs(12 - hour) / 12
                if hour >= 6 and hour <= 9:  # Morning peak
                    hour_factor = 1.5
                elif hour >= 17 and hour <= 20:  # Evening peak
                    hour_factor = 1.8
                
                # Add some day-of-week variation
                day_factor = 1.0
                if current.weekday() >= 5:  # Weekend
                    day_factor = 1.3
                
                flow_rate = 8.0 * hour_factor * day_factor * random.uniform(0.8, 1.2)
                pressure = 3.2 + random.uniform(-0.3, 0.3)
                
                readings.append({
                    'timestamp': current.timestamp(),
                    'flow_rate': flow_rate,
                    'pressure': pressure,
                    'temperature': 21.5 + random.uniform(-0.5, 0.5)
                })
                
                current += interval
            
            return readings
        
        try:
            # Try different possible paths for sensor readings
            possible_paths = ['sensor_readings', 'readings', 'data']
            readings = []
            
            for path in possible_paths:
                try:
                    # Construct the Firebase REST API URL
                    url = f"{self.config['databaseURL']}/{path}.json"
                    if self.database_secret:
                        url += f"?auth={self.database_secret}"
                        # Add query parameters to filter by time range
                        url += f'&orderBy="timestamp"&startAt={start_timestamp}&endAt={end_timestamp}'
                    
                    print(f"Trying to get historical readings from path: {path}")
                    
                    # Make the API request
                    response = requests.get(url)
                    
                    # If successful and has content
                    if response.status_code == 200:
                        readings_data = response.json()
                        
                        # If there's actual data here
                        if readings_data and isinstance(readings_data, dict):
                            print(f"Found historical readings at path: {path}")
                            
                            # Convert the dictionary to a list and collect readings
                            path_readings = list(readings_data.values())
                            readings.extend(path_readings)
                            
                            # Break after finding readings
                            if readings:
                                break
                except Exception as e:
                    print(f"Error reading from path {path}: {str(e)}")
                    continue
            
            # If we found any readings, process them
            if readings:
                # Sort by timestamp
                readings.sort(key=lambda x: x.get("timestamp", 0))
                
                # Convert total_ml to total_volume (in liters) for each reading
                for reading in readings:
                    if 'total_ml' in reading:
                        reading['total_volume'] = reading['total_ml'] / 1000.0
                
                return readings
            else:
                print("No historical readings found in any tested path.")
                return []
            
        except Exception as e:
            print(f"Error getting historical readings from Firebase: {str(e)}")
            return []
    
    def save_user_settings(self, user_id, settings):
        """
        Mock saving user settings for demo mode.
        
        Args:
            user_id: User ID
            settings: Dictionary of settings
        """
        # For demo mode, pretend to save settings
        if self.demo_mode:
            print(f"[DEMO] Settings saved for user {user_id}: {settings}")
            return True
        
        print("Real Firebase settings save not implemented")
        raise NotImplementedError("Firebase connection required")
    
    def save_sensor_calibration(self, user_id, calibration):
        """
        Mock saving sensor calibration for demo mode.
        
        Args:
            user_id: User ID
            calibration: Dictionary of calibration settings
        """
        # For demo mode, pretend to save calibration
        if self.demo_mode:
            print(f"[DEMO] Calibration saved for user {user_id}: {calibration}")
            return True
        
        print("Real Firebase calibration save not implemented")
        raise NotImplementedError("Firebase connection required")
    
    def get_user_settings(self, user_id):
        """
        Mock getting user settings for demo mode.
        
        Args:
            user_id: User ID
            
        Returns:
            dict: User settings
        """
        # For demo mode, return default settings
        if self.demo_mode:
            return {
                "email": "demo@example.com",
                "created_at": (datetime.now() - timedelta(days=30)).timestamp(),
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
                    "email": "demo@example.com",
                    "preferences": {
                        "high_pressure": True,
                        "low_pressure": True,
                        "high_flow": True,
                        "usage_limit": True,
                        "offline": True
                    }
                }
            }
        
        print("Real Firebase user settings not implemented")
        return None
            
    def get_device_status(self, device_id):
        """
        Get device status from Firebase.
        
        Args:
            device_id: ID of the ESP device (not used in actual implementation as ESP32 uses a fixed path)
            
        Returns:
            dict: Device status
        """
        # For demo mode, generate a simulated device status
        if self.demo_mode:
            return {
                "device_id": device_id or "demo-device-01",
                "ip_address": "192.168.1.100",
                "mac_address": "AA:BB:CC:DD:EE:FF",
                "firmware_version": "1.0.5",
                "connected": True,
                "ssid": "Realme Narzo",
                "signal_strength": random.randint(-85, -55),
                "last_update": datetime.now().timestamp(),
                "uptime": random.randint(1000, 50000),
                "wifi_quality": random.randint(60, 95),
                "battery_level": random.randint(75, 100) if random.random() > 0.1 else random.randint(10, 30)
            }
        
        try:
            # The ESP32 doesn't send specific device status data, but we can construct it
            # from the latest reading and calculate the "last seen" time
            
            # Get the latest reading for basic status
            latest_reading = self.get_latest_reading(None)
            
            if latest_reading is None:
                return None
                
            # Get the latest timestamp
            last_update = latest_reading.get('timestamp', int(time.time()))
            
            # Get the wifi info from the ESP32 firmware (SSID is hardcoded in the firmware)
            # The ESP32 code prints WiFi signal strength but doesn't store in Firebase directly
            # So we'll approximate it here (typical close-range WiFi strength)
            signal_strength = -65  # A reasonable value, in dBm
            
            # Create a device status dict from available information
            status_data = {
                "device_id": "esp32-sensor",
                "ip_address": "192.168.1.100",  # Approximate value, ESP32 gets dynamic IP
                "connected": True,
                "ssid": "Realme Narzo",  # From the ESP32 firmware
                "signal_strength": signal_strength,
                "last_update": last_update,
                "battery_percentage": latest_reading.get('battery_percentage', 100)
            }
            
            # Calculate time difference from now to last update
            time_diff = int(time.time()) - last_update
            
            # If the last update was more than 2 minutes ago, device may be offline
            if time_diff > 120:  # 2 minutes threshold
                status_data["connected"] = False
            
            # Return the constructed device status
            return status_data
            
        except Exception as e:
            print(f"Error getting device status from Firebase: {str(e)}")
            return None
        
    def get_latest_reading(self, device_id):
        """
        Get latest sensor reading from Firebase.
        
        Args:
            device_id: ID of the ESP device (not used in actual implementation as ESP32 uses a fixed path)
            
        Returns:
            dict: Latest sensor reading
        """
        # For demo mode, generate a simulated reading
        if self.demo_mode:
            now = datetime.now()
            hour = now.hour
            
            # Flow rate varies by hour with some randomness
            hour_factor = 0.5 + 0.5 * abs(12 - hour) / 12
            if hour >= 6 and hour <= 9:  # Morning peak
                hour_factor = 1.5
            elif hour >= 17 and hour <= 20:  # Evening peak
                hour_factor = 1.8
            
            # Add some day-of-week variation
            day_factor = 1.0
            if now.weekday() >= 5:  # Weekend
                day_factor = 1.3
            
            flow_rate = 8.0 * hour_factor * day_factor * random.uniform(0.8, 1.2)
            pressure = 3.2 + random.uniform(-0.3, 0.3)
            
            return {
                "device_id": device_id or "demo-device-01",
                "timestamp": now.timestamp(),
                "flow_rate": flow_rate,
                "pressure": pressure,
                "temperature": 21.5 + random.uniform(-0.5, 0.5),
                "total_volume": 1000.0 + random.uniform(0, 500.0)
            }
        
        try:
            # First, check the root of the database to see what paths exist
            root_url = f"{self.config['databaseURL']}/.json"
            if self.database_secret:
                root_url += f"?auth={self.database_secret}"
                
            root_response = requests.get(root_url)
            
            if root_response.status_code == 200:
                root_data = root_response.json()
                if not isinstance(root_data, dict):
                    print(f"Root data is not a dictionary: {root_data}")
                else:
                    print(f"Available root paths in Firebase: {list(root_data.keys())}")
                    
                    # Check if we have sensor_readings path
                    if 'sensor_readings' in root_data:
                        print("sensor_readings path exists in Firebase!")
                        
                    # Check if we have latest_reading path
                    if 'latest_reading' in root_data:
                        print("latest_reading path exists in Firebase!")
            else:
                print(f"Failed to get root data from Firebase: {root_response.status_code}")
            
            # Try multiple paths for latest reading, in case the ESP firmware is using a different path
            possible_paths = ['latest_reading', 'latest', 'current_reading', 'current']
            reading_data = None
            
            for path in possible_paths:
                url = f"{self.config['databaseURL']}/{path}.json"
                if self.database_secret:
                    url += f"?auth={self.database_secret}"
                    
                print(f"Trying to read from path: {path}")
                response = requests.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    if data is not None:
                        print(f"Found data at path: {path}")
                        reading_data = data
                        break
            
            # If no data found in any of the paths
            if reading_data is None:
                print("No data found in any of the expected paths.")
                return None
            
            # Convert total_ml to total_volume (in liters)
            if 'total_ml' in reading_data:
                reading_data['total_volume'] = reading_data['total_ml'] / 1000.0
                
            # Print the data we found for debugging
            print(f"Found reading data: {reading_data}")
                
            # Return the latest reading
            return reading_data
            
        except Exception as e:
            print(f"Error getting latest reading from Firebase: {str(e)}")
            return None
        
    def get_connection_logs(self, device_id, hours=24):
        """
        Get WiFi connection logs. For real implementation, this is constructed
        from sensor reading timestamps (since ESP32 doesn't explicitly track connections).
        
        Args:
            device_id: ID of the ESP device (not used in actual implementation)
            hours: Number of hours of history to retrieve
            
        Returns:
            list: Connection logs
        """
        # For demo mode, generate simulated connection logs
        if self.demo_mode:
            logs = []
            now = datetime.now()
            
            # Simulate some connection events over the requested time period
            for i in range(random.randint(5, 15)):
                # Random time within the requested period
                event_time = now - timedelta(hours=random.uniform(0, hours))
                
                # Decide if this is a connect or disconnect event
                event_type = random.choice(["connect", "disconnect"])
                
                # Generate appropriate event details
                if event_type == "connect":
                    rssi = random.randint(-85, -55)
                    logs.append({
                        "timestamp": event_time.timestamp(),
                        "event": "connect",
                        "ip_address": "192.168.1.100",
                        "ssid": "Realme Narzo",
                        "signal_strength": rssi,
                        "connected": True,
                        "quality": min(100, max(0, int((rssi + 100) * 2)))
                    })
                else:
                    logs.append({
                        "timestamp": event_time.timestamp(),
                        "event": "disconnect",
                        "connected": False,
                        "reason": random.choice(["timeout", "user_initiated", "wifi_lost", "power_cycle"])
                    })
            
            # Sort by timestamp
            logs.sort(key=lambda x: x["timestamp"])
            return logs
        
        try:
            # The ESP32 firmware doesn't explicitly record connection logs
            # We can infer connection status from sensor readings
            # Calculate the timestamp for 'hours' ago
            start_time = (datetime.now() - timedelta(hours=hours)).timestamp()
            end_time = datetime.now().timestamp()
            
            # Get historical readings for this time period
            readings = self.get_historical_readings(start_time, end_time)
            
            if not readings:
                # No readings available
                return []
                
            # Sort readings by timestamp
            readings.sort(key=lambda x: x.get("timestamp", 0))
            
            # Generate connection logs from reading timestamps
            # If there are gaps in readings larger than 2 minutes (120 seconds),
            # we'll assume a disconnection occurred
            logs = []
            
            # Always assume a connection at the first reading
            first_reading = readings[0]
            logs.append({
                "timestamp": first_reading.get("timestamp") - 1,  # Just before first reading
                "event": "connect",
                "ip_address": "192.168.1.100",  # Approximate, ESP32 gets dynamic IP
                "ssid": "Realme Narzo",
                "signal_strength": -65,  # Reasonable WiFi strength
                "connected": True,
                "quality": 70  # Reasonable WiFi quality
            })
            
            # Check for gaps between readings
            for i in range(1, len(readings)):
                prev_time = readings[i-1].get("timestamp", 0)
                curr_time = readings[i].get("timestamp", 0)
                
                # If there's a gap larger than 2 minutes, assume disconnection and reconnection
                if curr_time - prev_time > 120:  # 2 minutes in seconds
                    # Disconnection event
                    logs.append({
                        "timestamp": prev_time + 60,  # 1 minute after last reading
                        "event": "disconnect",
                        "connected": False,
                        "reason": "timeout"  # Assume timeout
                    })
                    
                    # Reconnection event
                    logs.append({
                        "timestamp": curr_time - 1,  # Just before new reading
                        "event": "connect",
                        "ip_address": "192.168.1.100",
                        "ssid": "Realme Narzo",
                        "signal_strength": -65,
                        "connected": True,
                        "quality": 70
                    })
            
            # Check if the most recent reading is more than 2 minutes old
            last_reading = readings[-1]
            last_time = last_reading.get("timestamp", 0)
            
            if datetime.now().timestamp() - last_time > 120:
                # Add disconnection event
                logs.append({
                    "timestamp": last_time + 60,  # 1 minute after last reading
                    "event": "disconnect",
                    "connected": False,
                    "reason": "timeout"
                })
            
            # Sort logs by timestamp
            logs.sort(key=lambda x: x.get("timestamp", 0))
            
            return logs
            
        except Exception as e:
            print(f"Error generating connection logs: {str(e)}")
            return []
        
    def send_device_command(self, device_id, command_data):
        """
        Mock sending a command to a device for demo mode.
        
        Args:
            device_id: ID of the ESP device
            command_data: Command data dictionary
            
        Returns:
            bool: Success status
        """
        # For demo mode, pretend to send a command
        if self.demo_mode:
            print(f"[DEMO] Command sent to device {device_id}: {command_data}")
            return True
        
        print("Real Firebase device command not implemented")
        return False
