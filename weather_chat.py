import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for

load_dotenv()
app = Flask(__name__)

def get_weather(city):
    """
    Get real-time weather data for a given city using OpenWeatherMap API
    """
    # You should store your API key as an environment variable
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        raise ValueError("Please set the OPENWEATHER_API_KEY environment variable")

    # OpenWeatherMap API endpoint
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    # Parameters for the API request
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric'  # For Celsius
    }

    try:
        # Make API request
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the JSON response
        weather_data = response.json()
        
        # Extract relevant information
        temperature = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        description = weather_data['weather'][0]['description']
        wind_speed = weather_data['wind']['speed']
        
        # Extract sunrise and sunset times (convert from Unix timestamp)
        sunrise_time = datetime.fromtimestamp(weather_data['sys']['sunrise']).strftime('%H:%M')
        sunset_time = datetime.fromtimestamp(weather_data['sys']['sunset']).strftime('%H:%M')
        
        # Format the weather information
        weather_info = {
            'city': city,
            'temperature': f"{temperature}°C",
            'humidity': f"{humidity}%",
            'description': description.capitalize(),
            'wind_speed': f"{wind_speed} m/s",
            'sunrise': sunrise_time,
            'sunset': sunset_time,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return weather_info
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data: {str(e)}"
    except (KeyError, ValueError) as e:
        return f"Error parsing weather data: {str(e)}"

@app.route('/')
def home():
    return render_template('welcome.html')

@app.route('/chat', methods=['POST'])
def chat():
    username = request.form.get('username')
    city = request.form.get('city')
    weather = get_weather(city)
    if isinstance(weather, dict):
        return f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: linear-gradient(120deg, #e0f4ff, #f0fff0);
                    padding: 20px;
                }}
                .weather-info {{
                    background: white;
                    padding: 20px;
                    border-radius: 15px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    margin: 20px auto;
                    max-width: 800px;
                }}
                .weather-item {{
                    display: inline-block;
                    padding: 10px 20px;
                    margin: 5px;
                    background: #f0f8ff;
                    border-radius: 20px;
                    border: 1px solid #a8e6cf;
                }}
                h2 {{
                    color: #4a90e2;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="weather-info">
                <h2>Hello {username}! Current weather in {weather['city']}</h2>
                <div style="text-align: center;">
                    <span class="weather-item">🌡️ {weather['temperature']}</span>
                    <span class="weather-item">💧 {weather['humidity']}</span>
                    <span class="weather-item">🌤️ {weather['description']}</span>
                    <span class="weather-item">💨 {weather['wind_speed']}</span>
                    <span class="weather-item">🌅 Sunrise: {weather['sunrise']}</span>
                    <span class="weather-item">🌇 Sunset: {weather['sunset']}</span>
                    <span class="weather-item">🕒 Updated: {weather['timestamp']}</span>
                </div>
            </div>
        </body>
        </html>
        """
    return weather  # Error message

if __name__ == "__main__":
    app.run(debug=True)
