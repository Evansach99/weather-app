# Imports for MQTT
import time
import datetime
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import subprocess
import requests
import json

# Using decimal to round the value for lux :)
from decimal import Decimal

# Set MQTT broker and topic
broker = "test.mosquitto.org"   # Broker

pub_topic = "iotproject/asmweather"    # asm -Automate Scens Management  send messages to this topic

############### MQTT section ##################
# when connecting to mqtt do this;
def on_connect(client, userdata, flags, rc):
        if rc==0:
                print("Connection established. Code: "+str(rc))
        else:
                print("Connection failed. Code: " + str(rc))
def on_publish(client, userdata, mid):
    print("Published: " + str(mid))
def on_disconnect(client, userdata, rc):
        if rc != 0:
                print ("Unexpected disonnection. Code: ", str(rc))
        else:
                print("Disconnected. Code: " + str(rc))
def on_log(client, userdata, level, buf):               # Message is in buf
    print("MQTT Log: " + str(buf))

def get_weather():
    api_key = "a23df0e6db663530882cd6476a5dcd39"
    city = 'Stockholm'
    api_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    response = requests.get(api_url)
    weather_data = response.json()

    temperature = weather_data['main']['temp']
    humidity = weather_data['main']['humidity']
    weather_des =weather_data['weather'][0]['description']


    print(f'{temperature}°C, {humidity}%',)
    weather_status =control_message(temperature,humidity)
#   print(weather_status)
    return temperature,humidity,weather_status,city,weather_des


def control_message(temperature,humidity):
    tempval = float(temperature)
    humidityval = int(humidity)
    if (-20.00 >= tempval) and (tempval <= -10.00):
        subprocess.run(["tdtool", "--on", "4"])  # Adjust the device ID accordingly
        val_lgt ="Light One / turned On"
        return val_lgt
    elif (-9.99 >= tempval) and (tempval <= 1.00) :
        subprocess.run(["tdtool", "--on", "4"])  # Adjust the device ID accordingly
        val_lgt ="Light Two / turned On"
        return val_lgt
    elif (1.99 >= tempval) and (tempval <= 10.00) :
        subprocess.run(["tdtool", "--on", "4"])  # Adjust the device ID accordingly
        val_lgt ="Light three / turned On"
        return val_lgt

# Connect functions for MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish
client.on_log = on_log

# Connect to MQTT
print("Attempting to connect to broker " + broker)
client.connect(broker)  
# Broker address, port and keepalive -
#-(maximum period in seconds allowed between communications with the broker)
client.loop_start()

# Loop that publishes message
while True:
        # Here, call the correct function from the sensor section depending on sensor
        data_to_send =str(get_weather())        
        client.publish(pub_topic, str(data_to_send))
        time.sleep(2.0) # Set delay


