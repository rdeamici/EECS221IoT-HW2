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

def setup_rpi():
    # Create sensor object, communicating via  I2C protocol
    i2c = board.I2C()
    sensor = adafruit_tcs34725.TCS34725(i2c)

    # start UDP server
    RPiUDPServerSocket.bind((RPiIP,RPiPort))
    print("UDP server up and listening")

    return i2c,sensor


def check_connection():


def flash_slowly():
    GPIO.output(RED,HIGH)
    time.sleep(.5)

def wait_for_connection():
    

def main()
    i2c,sensor = setup_rpi()
    wait_for_connection()
    socket.socket()

if __name__ == "__main__":
    main()