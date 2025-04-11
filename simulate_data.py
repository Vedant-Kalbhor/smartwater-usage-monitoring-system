import json
import random
import time
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Firebase configuration - hardcoded for simplicity
FIREBASE_DATABASE_URL = "https://waterflowtracker-92042.firebaseio.com"
FIREBASE_DATABASE_SECRET = "6t89jTnqLrvQelMdKHxXqh3jS2Ox9isTNJN9oFN6"

def simulate_water_data(num_days=3, readings_per_day=24, start_date=None):
    """
    Simulate water monitoring data for a given number of days.
    
    Args:
        num_days: Number of days to simulate (default: 3)
        readings_per_day: Number of readings per day (default: 24)
        start_date: Start date for simulation (default: 3 days ago)
    
    Returns:
        List of simulated readings
    """
    if start_date is None:
        start_date = datetime.now() - timedelta(days=num_days)
    
    readings = []
    
    # Pattern data
    daily_patterns = {
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
    
    # Time interval between readings in seconds
    interval = 24 * 60 * 60 / readings_per_day
    
    current_time = start_date
    hourly_usage = 0
    daily_usage = 0
    last_day = current_time.day
    last_hour = current_time.hour
    
    for i in range(num_days * readings_per_day):
        # Get current hour and its pattern multiplier
        hour = current_time.hour
        day_multiplier = 1.0 + (random.random() * 0.5 - 0.25)  # Random day variation
        
        # Reset usages if day/hour changes
        if current_time.day != last_day:
            daily_usage = 0
            last_day = current_time.day
            
        if current_time.hour != last_hour:
            hourly_usage = 0
            last_hour = current_time.hour
        
        # Base flow rate with pattern and random variations
        base_flow = daily_patterns.get(hour, 0.5) * 8.0  # L/min
        flow_rate = base_flow * day_multiplier * (1 + random.random() * 0.3 - 0.15)
        
        # Base pressure with random variations
        pressure = 3.5 + random.random() * 0.6 - 0.3  # bar
        
        # Calculate volume for this interval
        minutes = interval / 60
        volume = flow_rate * minutes  # Liters
        
        # Add to hourly and daily usage
        hourly_usage += volume
        daily_usage += volume
        
        # Create the reading
        timestamp = current_time.timestamp()
        reading = {
            'timestamp': timestamp,
            'flow_rate': round(flow_rate, 2),
            'pressure': round(pressure, 2),
            'volume': round(volume, 2),
            'hourly_usage': round(hourly_usage, 2),
            'daily_usage': round(daily_usage, 2)
        }
        
        readings.append(reading)
        
        # Advance time for next reading
        current_time += timedelta(seconds=interval)
    
    return readings

def upload_to_firebase(readings):
    """
    Upload simulated readings to Firebase using REST API with database secret.
    
    Args:
        readings: List of reading dictionaries
    """
    if not FIREBASE_DATABASE_URL:
        print("Firebase database URL is missing. Cannot upload data.")
        return False
        
    if not FIREBASE_DATABASE_SECRET:
        print("Firebase database secret is missing. Cannot upload data.")
        return False
    
    # Format the database URL properly
    database_url = FIREBASE_DATABASE_URL.rstrip('/')
    
    # Make sure database URL doesn't start with https:// for Firebase REST API
    if database_url.startswith('https://'):
        database_url = database_url[8:]
    
    try:
        # Upload each reading to sensor_readings path (like the ESP32 would)
        sensor_readings_url = f"https://{database_url}/sensor_readings.json?auth={FIREBASE_DATABASE_SECRET}"
        timestamp_now = int(time.time())
        
        # Create a batch upload object
        batch_data = {}
        
        # Base starting volume (500 liters = 500,000 ml)
        starting_volume = 500000
        
        # Add each reading with a timestamp key
        for reading in readings:
            timestamp_key = str(int(reading['timestamp']))
            
            # Convert hourly_usage and daily_usage to total_ml to match ESP32 format
            # Since ESP32 sends total_ml, not hourly/daily usage
            reading_copy = reading.copy()
            
            # Convert volume to milliliters
            volume_ml = reading_copy.pop('volume', 0) * 1000
            
            # Add total_ml to match ESP32 format (simulate a device that's been running)
            # Start with a base volume and add the current reading's volume
            reading_copy['total_ml'] = starting_volume + (volume_ml * (readings.index(reading) + 1))
            
            # Remove hourly and daily usage as ESP32 doesn't send these
            if 'hourly_usage' in reading_copy:
                reading_copy.pop('hourly_usage')
            if 'daily_usage' in reading_copy:
                reading_copy.pop('daily_usage')
            
            # Add to batch
            batch_data[timestamp_key] = reading_copy
        
        # Send batch upload to Firebase
        response = requests.put(sensor_readings_url, json=batch_data)
        response.raise_for_status()
        
        # Update the latest_reading node (just like ESP32 would)
        latest = readings[-1].copy()
        
        # Format latest reading to match ESP32 format
        if 'hourly_usage' in latest:
            latest.pop('hourly_usage')
        if 'daily_usage' in latest:
            latest.pop('daily_usage')
        if 'volume' in latest:
            # Convert volume in liters to total_ml
            volume_ml = latest.pop('volume', 0) * 1000
            # Use the same starting_volume defined above
            latest['total_ml'] = starting_volume + (volume_ml * len(readings))
        
        # Add battery percentage
        latest['battery_percentage'] = 85
        
        latest_url = f"https://{database_url}/latest_reading.json?auth={FIREBASE_DATABASE_SECRET}"
        response = requests.put(latest_url, json=latest)
        response.raise_for_status()
        
        print(f"Successfully uploaded data to Firebase: {response.status_code}")
        return True
    
    except Exception as e:
        print(f"Error uploading to Firebase: {str(e)}")
        return False

def main():
    """
    Main function to generate and upload simulated data.
    """
    # Generate historical data for the past 3 days
    historical_readings = simulate_water_data(num_days=3, readings_per_day=24)
    
    # Generate current data (last hour)
    current_time = datetime.now() - timedelta(hours=1)
    current_readings = simulate_water_data(num_days=1, readings_per_day=24, start_date=current_time)
    
    # Combine all readings
    all_readings = historical_readings + current_readings
    
    # Upload to Firebase
    success = upload_to_firebase(all_readings)
    
    if success:
        print(f"Successfully uploaded {len(all_readings)} readings to Firebase.")
    else:
        print("Failed to upload data to Firebase.")
        # Save locally for debugging
        with open("simulated_data.json", "w") as f:
            json.dump(all_readings, f, indent=2)
        print(f"Saved {len(all_readings)} readings to simulated_data.json for reference.")

if __name__ == "__main__":
    main()