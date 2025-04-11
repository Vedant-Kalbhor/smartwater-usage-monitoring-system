import streamlit as st
import os
from firebase_manager import FirebaseManager
from auth import login_page, signup_page, reset_password_page, logout_user
from dashboard import display_dashboard
from settings import display_settings
import json

# App title and configuration
st.set_page_config(
    page_title="Water Monitoring System",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'login'
if 'refresh_dashboard' not in st.session_state:
    st.session_state.refresh_dashboard = False
if 'firebase_initialized' not in st.session_state:
    st.session_state.firebase_initialized = False

# For demo purposes, create a placeholder for Firebase credentials
# In a production environment, these would be stored securely in environment variables
def init_firebase():
    """Initialize Firebase with credentials from environment or placeholder values for demo."""
    if st.session_state.firebase_initialized:
        return st.session_state.firebase_manager
    
    # Try to get Firebase credentials from environment variables
    api_key = os.getenv("FIREBASE_API_KEY", "")
    auth_domain = os.getenv("FIREBASE_AUTH_DOMAIN", "")
    database_url = os.getenv("FIREBASE_DATABASE_URL", "")
    storage_bucket = os.getenv("FIREBASE_STORAGE_BUCKET", "")
    service_account_key = os.getenv("FIREBASE_SERVICE_ACCOUNT", "")
    
    # For demo purposes, if no credentials are found, use placeholder values
    # and simulate a connection
    if not (api_key and auth_domain and database_url):
        if 'demo_mode' not in st.session_state:
            st.session_state.demo_mode = True
            st.warning("⚠️ Running in demo mode with simulated data. No actual Firebase connection.")

    # Initialize Firebase manager
    firebase_manager = FirebaseManager(
        api_key=api_key,
        auth_domain=auth_domain,
        database_url=database_url,
        storage_bucket=storage_bucket,
        service_account_key=service_account_key
    )
    
    st.session_state.firebase_manager = firebase_manager
    st.session_state.firebase_initialized = True
    
    return firebase_manager

def main():
    """Main application function."""
    # Initialize Firebase
    firebase_manager = init_firebase()
    
    # Display app header
    st.sidebar.image("generated-icon.png", width=100)
    st.sidebar.title("Water Monitoring System")
    
    # Handle authentication and display appropriate view
    if not st.session_state.logged_in:
        # Authentication views
        auth_option = st.sidebar.radio("Authentication", ["Login", "Sign Up", "Reset Password"])
        
        if auth_option == "Login":
            login_page(firebase_manager)
        elif auth_option == "Sign Up":
            signup_page(firebase_manager)
        else:
            reset_password_page(firebase_manager)
    else:
        # User is logged in, display main navigation
        navigation = st.sidebar.radio("Navigation", ["Dashboard", "Settings", "Logout"])
        
        # Display user info
        st.sidebar.write(f"Logged in as: {st.session_state.user_email}")
        
        # Handle navigation
        if navigation == "Dashboard":
            display_dashboard(firebase_manager)
        elif navigation == "Settings":
            display_settings(firebase_manager)
        else:  # Logout
            logout_user()
            st.rerun()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2025 Water Monitoring System")

if __name__ == "__main__":
    main()