import streamlit as st
from firebase_manager import FirebaseManager

def display_settings(firebase_manager: FirebaseManager):
    """
    Display and manage user settings for the water monitoring system.
    """
    st.title("⚙️ Water Monitoring Settings")
    
    # Create tabs for different settings categories
    tabs = st.tabs(["Alert Thresholds", "Sensor Calibration", "Notifications"])
    
    # Get current user settings
    user_id = st.session_state.get('user_id')
    user_settings = None
    
    if user_id:
        user_settings = firebase_manager.get_user_settings(user_id)
    
    # Default settings if none are found
    if not user_settings:
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
                "email": st.session_state.get('user_email', ''),
                "preferences": {
                    "high_pressure": True,
                    "low_pressure": True,
                    "high_flow": True,
                    "usage_limit": True,
                    "offline": True
                }
            }
        }
    
    # Alert Thresholds Tab
    alert_thresholds_tab(tabs[0], firebase_manager, user_id, user_settings)
    
    # Sensor Calibration Tab
    sensor_calibration_tab(tabs[1], firebase_manager, user_id, user_settings)
    
    # Notifications Tab
    notifications_tab(tabs[2], firebase_manager, user_id, user_settings)

def alert_thresholds_tab(tab, firebase_manager, user_id, user_settings):
    """Display and manage alert threshold settings."""
    with tab:
        st.subheader("Alert Threshold Settings")
        st.write("Set thresholds for when alerts should be triggered.")
        
        # Get current thresholds
        thresholds = user_settings.get('alert_thresholds', {})
        
        with st.form("threshold_form"):
            # Pressure thresholds
            st.write("### Pressure Thresholds")
            col1, col2 = st.columns(2)
            
            with col1:
                pressure_high = st.number_input(
                    "High Pressure Threshold (bar)",
                    min_value=1.0,
                    max_value=10.0,
                    value=float(thresholds.get('pressure_high', 6.0)),
                    step=0.1,
                    help="Alert when pressure exceeds this value"
                )
            
            with col2:
                pressure_low = st.number_input(
                    "Low Pressure Threshold (bar)",
                    min_value=0.1,
                    max_value=5.0,
                    value=float(thresholds.get('pressure_low', 1.0)),
                    step=0.1,
                    help="Alert when pressure falls below this value"
                )
            
            # Flow threshold
            st.write("### Flow Threshold")
            flow_high = st.number_input(
                "High Flow Rate Threshold (L/min)",
                min_value=1.0,
                max_value=50.0,
                value=float(thresholds.get('flow_high', 20.0)),
                step=0.5,
                help="Alert when flow rate exceeds this value"
            )
            
            # Usage threshold
            st.write("### Usage Threshold")
            daily_usage_high = st.number_input(
                "Daily Usage Threshold (L)",
                min_value=50.0,
                max_value=2000.0,
                value=float(thresholds.get('daily_usage_high', 500.0)),
                step=10.0,
                help="Alert when daily water usage exceeds this value"
            )
            
            # Save button
            save_button = st.form_submit_button("Save Thresholds")
            
            if save_button:
                # Prepare updated thresholds
                updated_thresholds = {
                    "alert_thresholds": {
                        "pressure_high": pressure_high,
                        "pressure_low": pressure_low,
                        "flow_high": flow_high,
                        "daily_usage_high": daily_usage_high
                    }
                }
                
                # Demo mode
                if 'demo_mode' in st.session_state and st.session_state.demo_mode:
                    st.success("Alert thresholds saved successfully in demo mode!")
                    # Update session state for demo
                    if 'user_settings' not in st.session_state:
                        st.session_state.user_settings = {}
                    st.session_state.user_settings.update(updated_thresholds)
                    return
                
                # Save to Firebase
                if user_id:
                    try:
                        firebase_manager.save_user_settings(user_id, updated_thresholds)
                        st.success("Alert thresholds saved successfully!")
                    except Exception as e:
                        st.error(f"Error saving thresholds: {str(e)}")
                else:
                    st.error("User not authenticated. Please log in again.")

def sensor_calibration_tab(tab, firebase_manager, user_id, user_settings):
    """Display and manage sensor calibration settings."""
    with tab:
        st.subheader("Sensor Calibration")
        st.write("Adjust calibration factors for your water sensors.")
        
        # Get current calibration
        calibration = user_settings.get('sensor_calibration', {})
        
        with st.form("calibration_form"):
            # Flow meter calibration
            st.write("### Flow Meter Calibration")
            flow_factor = st.number_input(
                "Flow Factor",
                min_value=0.5,
                max_value=1.5,
                value=float(calibration.get('flow_factor', 1.0)),
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
                    value=float(calibration.get('pressure_zero', 0.0)),
                    step=0.01,
                    help="Zero offset adjustment for pressure readings"
                )
            
            with col2:
                pressure_factor = st.number_input(
                    "Pressure Factor",
                    min_value=0.5,
                    max_value=1.5,
                    value=float(calibration.get('pressure_factor', 1.0)),
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
                # Prepare updated calibration
                updated_calibration = {
                    "flow_factor": flow_factor,
                    "pressure_zero": pressure_zero,
                    "pressure_factor": pressure_factor
                }
                
                # Demo mode
                if 'demo_mode' in st.session_state and st.session_state.demo_mode:
                    st.success("Sensor calibration saved successfully in demo mode!")
                    # Update session state for demo
                    if 'user_settings' not in st.session_state:
                        st.session_state.user_settings = {}
                    if 'sensor_calibration' not in st.session_state.user_settings:
                        st.session_state.user_settings['sensor_calibration'] = {}
                    st.session_state.user_settings['sensor_calibration'].update(updated_calibration)
                    return
                
                # Save to Firebase
                if user_id:
                    try:
                        firebase_manager.save_sensor_calibration(user_id, updated_calibration)
                        st.success("Sensor calibration saved successfully!")
                    except Exception as e:
                        st.error(f"Error saving calibration: {str(e)}")
                else:
                    st.error("User not authenticated. Please log in again.")

def notifications_tab(tab, firebase_manager, user_id, user_settings):
    """Display and manage notification settings."""
    with tab:
        st.subheader("Notification Settings")
        st.write("Configure how and when you receive alerts about your water system.")
        
        # Get current notification settings
        notifications = user_settings.get('notifications', {})
        preferences = notifications.get('preferences', {})
        
        with st.form("notification_form"):
            # Email notifications
            st.write("### Email Notifications")
            enable_email = st.checkbox(
                "Enable Email Notifications",
                value=notifications.get('enable_email', True)
            )
            
            # Email address
            email = st.text_input(
                "Email Address",
                value=notifications.get('email', st.session_state.get('user_email', '')),
                disabled=not enable_email
            )
            
            # Notification preferences
            st.write("### Alert Types")
            col1, col2 = st.columns(2)
            
            with col1:
                high_pressure = st.checkbox(
                    "High Pressure Alerts",
                    value=preferences.get('high_pressure', True),
                    disabled=not enable_email
                )
                
                low_pressure = st.checkbox(
                    "Low Pressure Alerts",
                    value=preferences.get('low_pressure', True),
                    disabled=not enable_email
                )
                
                high_flow = st.checkbox(
                    "High Flow Alerts",
                    value=preferences.get('high_flow', True),
                    disabled=not enable_email
                )
            
            with col2:
                usage_limit = st.checkbox(
                    "Usage Limit Alerts",
                    value=preferences.get('usage_limit', True),
                    disabled=not enable_email
                )
                
                offline = st.checkbox(
                    "Offline Sensor Alerts",
                    value=preferences.get('offline', True),
                    disabled=not enable_email
                )
            
            # Save button
            save_button = st.form_submit_button("Save Notification Settings")
            
            if save_button:
                # Prepare updated notification settings
                updated_notifications = {
                    "notifications": {
                        "enable_email": enable_email,
                        "email": email,
                        "preferences": {
                            "high_pressure": high_pressure,
                            "low_pressure": low_pressure,
                            "high_flow": high_flow,
                            "usage_limit": usage_limit,
                            "offline": offline
                        }
                    }
                }
                
                # Demo mode
                if 'demo_mode' in st.session_state and st.session_state.demo_mode:
                    st.success("Notification settings saved successfully in demo mode!")
                    # Update session state for demo
                    if 'user_settings' not in st.session_state:
                        st.session_state.user_settings = {}
                    st.session_state.user_settings.update(updated_notifications)
                    return
                
                # Save to Firebase
                if user_id:
                    try:
                        firebase_manager.save_user_settings(user_id, updated_notifications)
                        st.success("Notification settings saved successfully!")
                    except Exception as e:
                        st.error(f"Error saving notification settings: {str(e)}")
                else:
                    st.error("User not authenticated. Please log in again.")