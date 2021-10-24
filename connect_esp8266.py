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
RPiIP = '192.168.0.16'
RPiPort = 4210
RPiUDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

#port to receive data from ESP8266
ESPPort = 4210

def setup_rpi():
    # Create sensor object, communicating via  I2C protocol
    i2c = board.I2C()
    sensor = adafruit_tcs34725.TCS34725(i2c)

    # start UDP server
    RPiUDPServerSocket.bind((RPiIP,RPiPort))
    print("UDP server up and listening...")

    return i2c, sensor


def check_connection():
    data, address = RPiUDPServerSocket.recvfrom(ESPPort)
    return data,address

def flash_slowly():
    GPIO.output(RED,HIGH)
    start = time.time()
    data, address = check_connection()
    end = time.time()
    if end - start < 0.5:
        time_to_sleep = 0.5 - (end-start)
    else:
        raise ValueError("took more than half ({}) a second to check connection".format(
            end-start
        ))
    time.sleep(time_to_sleep)


def wait_for_connection():
    data = ''
    while not data:
        data, address = flash_slowly()    
    
    return data, address

def main()
    i2c,sensor = setup_rpi()
    data, address = wait_for_connection()

if __name__ == "__main__":
    main()