import streamlit as st
import re
from firebase_manager import FirebaseManager

def validate_email(email):
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))

def validate_password(password):
    """Validate password strength."""
    # Check if password meets minimum requirements
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    
    # Check if password contains at least one uppercase letter, one lowercase letter, and one digit
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    
    return True, "Password is valid."

def login_page(firebase_manager: FirebaseManager):
    """Display the login page and handle login process."""
    st.title("🔐 Login to Water Monitoring System")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        login_button = st.form_submit_button("Login")
        
        if login_button:
            # Validate inputs
            if not email or not password:
                st.error("Please enter both email and password.")
                return
            
            if not validate_email(email):
                st.error("Please enter a valid email address.")
                return
            
            # Demo mode with simulated login
            if 'demo_mode' in st.session_state and st.session_state.demo_mode:
                # Simulate successful login in demo mode
                if email == "demo@example.com" and password == "Demo1234":
                    st.session_state.logged_in = True
                    st.session_state.user_id = "demo_user_id"
                    st.session_state.user_email = email
                    st.session_state.current_view = 'dashboard'
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("In demo mode, use email 'demo@example.com' and password 'Demo1234'")
                return
            
            # Attempt login with Firebase
            user = firebase_manager.login_user(email, password)
            
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user.get('localId')
                st.session_state.user_email = email
                st.session_state.current_view = 'dashboard'
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Login failed. Please check your email and password.")
    
    # Demo mode notice
    if 'demo_mode' in st.session_state and st.session_state.demo_mode:
        st.info("🔍 Demo Mode: Use email 'demo@example.com' and password 'Demo1234' to log in.")

def signup_page(firebase_manager: FirebaseManager):
    """Display the signup page and handle registration process."""
    st.title("📝 Sign Up for Water Monitoring System")
    
    with st.form("signup_form"):
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter a strong password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        signup_button = st.form_submit_button("Sign Up")
        
        if signup_button:
            # Validate inputs
            if not email or not password or not confirm_password:
                st.error("Please fill in all fields.")
                return
            
            if not validate_email(email):
                st.error("Please enter a valid email address.")
                return
            
            valid_password, password_message = validate_password(password)
            if not valid_password:
                st.error(password_message)
                return
            
            if password != confirm_password:
                st.error("Passwords do not match.")
                return
            
            # Demo mode with simulated sign up
            if 'demo_mode' in st.session_state and st.session_state.demo_mode:
                st.success("Account created successfully in demo mode!")
                st.info("Now you can login with the credentials you just created.")
                return
            
            # Attempt to create user with Firebase
            user = firebase_manager.create_user(email, password)
            
            if user:
                st.success("Account created successfully!")
                st.info("You can now login with your new account.")
            else:
                st.error("Failed to create account. The email might already be registered.")
    
    # Demo mode notice
    if 'demo_mode' in st.session_state and st.session_state.demo_mode:
        st.info("🔍 Demo Mode: Account creation is simulated and won't persist.")

def reset_password_page(firebase_manager: FirebaseManager):
    """Display the password reset page."""
    st.title("🔄 Reset Password")
    
    with st.form("reset_form"):
        email = st.text_input("Email", placeholder="Enter your email")
        
        reset_button = st.form_submit_button("Send Reset Link")
        
        if reset_button:
            if not email:
                st.error("Please enter your email address.")
                return
            
            if not validate_email(email):
                st.error("Please enter a valid email address.")
                return
            
            # Demo mode with simulated password reset
            if 'demo_mode' in st.session_state and st.session_state.demo_mode:
                st.success("Password reset link sent in demo mode!")
                st.info("In a real environment, you would receive an email with password reset instructions.")
                return
            
            # Attempt to send password reset email with Firebase
            try:
                firebase_manager.reset_password(email)
                st.success("Password reset link sent! Please check your email.")
            except Exception as e:
                st.error(f"Error sending password reset link: {str(e)}")
    
    # Demo mode notice
    if 'demo_mode' in st.session_state and st.session_state.demo_mode:
        st.info("🔍 Demo Mode: Password reset is simulated and no actual email will be sent.")

def logout_user():
    """Handle the logout process."""
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_email = None
    st.session_state.current_view = 'login'