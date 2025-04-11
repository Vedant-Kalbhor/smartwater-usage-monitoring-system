from datetime import datetime

def check_alerts(data, thresholds):
    """
    Check sensor data against thresholds and return any alerts.
    
    Args:
        data: Dictionary containing sensor data
        thresholds: Dictionary containing alert thresholds
        
    Returns:
        list: List of alert messages
    """
    if not data or not thresholds:
        return []
    
    alerts = []
    current_time = datetime.now().strftime("%H:%M")
    
    # Check pressure high threshold
    if 'pressure' in data and 'pressure_high' in thresholds:
        pressure = data['pressure']
        threshold = thresholds['pressure_high']
        
        if pressure > threshold:
            alerts.append({
                'message': f"High pressure detected: {pressure:.1f} bar (threshold: {threshold:.1f} bar) at {current_time}",
                'severity': 'high',
                'timestamp': datetime.now().timestamp()
            })
    
    # Check pressure low threshold
    if 'pressure' in data and 'pressure_low' in thresholds:
        pressure = data['pressure']
        threshold = thresholds['pressure_low']
        
        if pressure < threshold:
            alerts.append({
                'message': f"Low pressure detected: {pressure:.1f} bar (threshold: {threshold:.1f} bar) at {current_time}",
                'severity': 'high',
                'timestamp': datetime.now().timestamp()
            })
    
    # Check flow rate threshold
    if 'flow_rate' in data and 'flow_high' in thresholds:
        flow_rate = data['flow_rate']
        threshold = thresholds['flow_high']
        
        if flow_rate > threshold:
            alerts.append({
                'message': f"High flow rate detected: {flow_rate:.1f} L/min (threshold: {threshold:.1f} L/min) at {current_time}",
                'severity': 'medium',
                'timestamp': datetime.now().timestamp()
            })
    
    # Check daily usage threshold
    if 'daily_usage' in data and 'daily_usage_high' in thresholds:
        daily_usage = data['daily_usage']
        threshold = thresholds['daily_usage_high']
        
        if daily_usage > threshold:
            alerts.append({
                'message': f"Daily water usage exceeded: {daily_usage:.1f} L (threshold: {threshold:.1f} L)",
                'severity': 'medium',
                'timestamp': datetime.now().timestamp()
            })
    
    return alerts

def format_volume(volume, unit='L'):
    """
    Format volume with appropriate units.
    
    Args:
        volume: Volume in liters
        unit: Base unit
        
    Returns:
        str: Formatted volume string
    """
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

def format_timestamp(timestamp, format_str="%Y-%m-%d %H:%M:%S"):
    """
    Format a timestamp to a human-readable string.
    
    Args:
        timestamp: UNIX timestamp
        format_str: Format string
        
    Returns:
        str: Formatted timestamp string
    """
    if timestamp is None:
        return "N/A"
    
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime(format_str)
    except (ValueError, TypeError) as e:
        print(f"Error formatting timestamp: {str(e)}")
        return "Invalid timestamp"

def validate_input(value, min_val, max_val, default):
    """
    Validate numerical input and provide a default if out of range.
    
    Args:
        value: Input value
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        default: Default value if out of range
        
    Returns:
        float: Validated value
    """
    try:
        val = float(value)
        if val < min_val or val > max_val:
            return default
        return val
    except (ValueError, TypeError):
        return default