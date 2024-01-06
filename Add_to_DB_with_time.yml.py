import time
import datetime
import sqlite3
import requests
import paho.mqtt.client as mqtt
import requests


# Database setup
conn = sqlite3.connect('weather_data.db')
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE IF NOT EXISTS weather_light_status 
             (timestamp TEXT, temperature REAL, humidity INTEGER, light_status TEXT)''')

# Set MQTT broker and topic
broker = "test.mosquitto.org"
pub_topic = "iotproject/asmweather"   # asm -Automate Scens Management  send messages to this topic

# MQTT callback functions
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_publish(client, userdata, mid):
    print("Data published")

# Function to fetch weather data
def get_weather():
    api_key = "a23df0e6db663530882cd6476a5dcd39"
    city = 'Stockholm'
    api_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    response = requests.get(api_url)
    weather_data = response.json()

    temperature = weather_data['main']['temp']
    humidity = weather_data['main']['humidity']
    light_status = determine_light_status(temperature, humidity)

    return temperature, humidity, light_status

def determine_light_status(temperature, humidity):
    # Logic to determine light status based on temperature and humidity
    # Replace with actual control logic
    return "Light On" if temperature < 10 else "Light Off"

# MQTT setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_publish = on_publish
client.connect(broker, 1883, 60)
client.loop_start()

# Main loop
try:
    while True:
        temperature, humidity, light_status = get_weather()
        timestamp = datetime.datetime.now().isoformat()

        # Save to database
        c.execute("INSERT INTO weather_light_status VALUES (?, ?, ?, ?)", 
                  (timestamp, temperature, humidity, light_status))
        conn.commit()

        # Publish to MQTT
        client.publish(pub_topic, f"{timestamp}, {temperature}, {humidity}, {light_status}")

        # Wait for 30 minutes
        time.sleep(1800)
except KeyboardInterrupt:
    print("Program stopped by user")

finally:
    conn.close()
    client.loop_stop()
