import time
import board
import sys
import adafruit_tcs34725
import RPi.GPIO as GPIO
import socket

HIGH = GPIO.HIGH
LOW = GPIO.LOW

# Setup LED lights
GREEN = 5
RED = 6
BLUE = 13

#setup board pinouts
GPIO.setmode(GPIO.BCM)
GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(RED, GPIO.OUT)
GPIO.setup(BLUE, GPIO.OUT)

# setup UDP server on RPi
RPi_address = '192.168.0.16'
RPiPort = 4210
RPiUDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

#port to receive data from ESP8266
ESPPort = 4210

def setup_rpi():
    # Create sensor object, communicating via  I2C protocol
    i2c = board.I2C()
    sensor = adafruit_tcs34725.TCS34725(i2c)

    # start UDP server
    RPiUDPServerSocket.bind((RPi_address,RPiPort))
    print("UDP server up and listening...")

    return i2c, sensor


def check_connection():
    data, address = RPiUDPServerSocket.recvfrom(ESPPort)
    return data, address

def calculate_time_diff(start):
    end = time.time()
    time_to_sleep = 0.5 - (end - start)

    if time_to_sleep < 0:
        raise ValueError("took more than half a sec ({})  to check connection".format(end-start))

    return time_to_sleep


def flash_slowly():
    '''
    Represents a single on/off light blink cycle.
    Blinks light half second on, half second off.
    Checks for data sent via UDP during on period and
    during off period, if no data was found previously.
    '''
    GPIO.output(RED,HIGH)
    start = time.time()
    data, ESP_address = check_connection()
    time_to_sleep = calculate_time_diff(start)
    time.sleep(time_to_sleep)

    GPIO.output(RED,LOW)
    start = time.time()

    if not data:
        data, ESP_address = check_connection()

    time_to_sleep = calculate_time_diff(start)
    time.sleep(time_to_sleep)

    return data, ESP_address

def wait_for_connection():
    '''
    flashes LED continuously while checking
    for data sent via UDP connection
    '''
    data = ''
    while not data:
        data, address = flash_slowly()    
    
    return data, address

def main():
    i2c,sensor = setup_rpi()
    data, address = wait_for_connection()
    

if __name__ == "__main__":
    main()