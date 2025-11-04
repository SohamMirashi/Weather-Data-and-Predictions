# Weather Info App - User Guide

## Flow Overview

1. **Login Page (index.html)**
   - Sign Up: Create a new account
   - Sign In: Login with existing credentials
   - After successful authentication, automatically redirects to the weather page

2. **Weather Page (index_weather.html)**
   - Enter an address to get coordinates
   - Get weather information based on coordinates
   - Get personalized weather advice

## How to Use

### Starting the Application

1. **Start the Backend Server:**
   ```bash
   cd D:\Programming\Projects\Weather-Data-and-Predictions
   python start_server.py
   ```

2. **Start the Weather API Server (if using weather features):**
   ```bash
   python main_weather.py
   ```

3. **Open the Login Page:**
   - Navigate to `Website/index.html`
   - Or open in browser: `file:///D:/Programming/Projects/Weather-Data-and-Predictions/Website/index.html`

### Testing the Flow

1. **Sign Up:**
   - Enter your details
   - Click "Get Started"
   - Wait for success message
   - Automatically redirects to weather page

2. **Sign In:**
   - Enter your credentials
   - Click "Sign In"
   - Wait for success message
   - Automatically redirects to weather page

3. **Use Weather Features:**
   - Enter an address (e.g., "Delhi")
   - Click "Get Coordinates"
   - Click "Get Weather"
   - View weather details and advice

## Files Structure

- `index.html` - Login/Signup page
- `index_weather.html` - Weather information page
- `styles.css` - Stylesheet for login page

## Notes

- The backend server must be running for authentication to work
- The weather API server must be running for weather features to work
- Data is stored in MySQL database `weather_info`
