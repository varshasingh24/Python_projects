
import requests
import sqlite3
import psycopg2
import pandas as pd
# import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
# import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def fetch_weather_data(api_key, city):
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no"
    response = requests.get(url)
    print(response.json())
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching data:", response.status_code)
        return None

def setup_database():
    # Replace the following URL with your actual Neon DB connection URL
    neon_db_url = 'postgresql://neondb_owner:npg_QPox7B2IyELi@ep-soft-scene-a5lxxiie-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require'  # Replace with your Neon DB URL
    
    try:
        # Connect to your PostgreSQL database using the connection URL
        conn = psycopg2.connect(neon_db_url)
        print("Connection to NeonDB successful!")  # Success message
        
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather (
                id SERIAL PRIMARY KEY,
                city TEXT,
                temperature REAL,
                humidity REAL,
                date TIMESTAMP
            )
        ''')
        conn.commit()
        return conn

    except Exception as e:
        print("Error connecting to NeonDB:", e)  # Error message
        return None  # Return None if connection fails


def insert_weather_data(conn, city, temperature, humidity, date):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO weather (city, temperature, humidity, date)
        VALUES (%s, %s, %s, %s)
    ''', (city, temperature, humidity, date))
    conn.commit()

def fetch_data_from_db(conn):
    
    df = pd.read_sql_query("SELECT * FROM weather", conn)
    conn.close()
    return df
def visualize_temperature_trends(df, city):
    # Convert 'date' column to datetime format
    df['date'] = pd.to_datetime(df['date'])

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot temperature with a line and markers
    line, = ax.plot(df['date'], df['temperature'], marker='o', linestyle='-', color='royalblue', label='Temperature (°C)')
    
    # Add title and labels
    ax.set_title(f'Temperature Trends Over Time in {city}', fontsize=20, fontweight='bold', color='darkblue')
    ax.set_xlabel('Date: & Time:', fontsize=16)
    ax.set_ylabel('Temperature (°C)', fontsize=16)
    
    # Format x-axis for better readability
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.xticks(rotation=45, ha='right')
    
    # Set y-axis range
    ax.set_ylim(df['temperature'].min() - 1, df['temperature'].max() + 1)
    
    # Add grid with enhanced visibility
    ax.grid(True, linestyle='--', alpha=0.7, color='gray')
    
    # Add a legend
    ax.legend(fontsize=14)
    
    # Add text for coordinates
    coord_text = ax.text(0.05, 0.95, '', transform=ax.transAxes, fontsize=12, verticalalignment='top')

    # Animation function
    def update(frame):
        line.set_data(df['date'][:frame], df['temperature'][:frame])
        coord_text.set_text(f'Date: {df["date"].iloc[frame-1].strftime("%Y-%m-%d %H:%M")}, Temp: {df["temperature"].iloc[frame-1]} °C')
        return line, coord_text

    # Create animation with a delay of 500 milliseconds
    ani = FuncAnimation(fig, update, frames=len(df), blit=True, repeat=False, interval=500)

    # Adjust layout for better spacing
    plt.tight_layout()
    
    # Show the plot
    plt.show()

def main():
    api_key = 'afcf03669d7c4a48abd122037251806'  # Replace with your API key
    city = 'Greater Noida'  # Change to your desired city

    # Fetch weather data
    weather_data = fetch_weather_data(api_key, city)
    print("weather_data", weather_data)
    if weather_data:
    # Extract temperature and humidity from the new API response structure
        temperature = weather_data['current']['temp_c']  # Use 'temp_c' for Celsius
        humidity = weather_data['current']['humidity']
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Set up database and insert data
        conn = setup_database()
        insert_weather_data(conn, city, temperature, humidity, date)

        # Fetch data from the database
        df = fetch_data_from_db(conn)
        conn.close()

        # Visualize temperature trends
        visualize_temperature_trends(df, city)

if __name__ == "__main__":
    main()




