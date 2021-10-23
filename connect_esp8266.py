import time
import board
import sys
import adafruit_tcs34725
import RPi.GPIO as GPIO
import socket

# Setup LED lights
GREEN = 5
RED = 6
BLUE = 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(green, GPIO.OUT)
GPIO.setup(red, GPIO.OUT)
GPIO.setup(blue, GPIO.OUT)


def setup_rpi():
    # Create sensor object, communicating via  I2C protocol
    i2c = board.I2C()
    sensor = adafruit_tcs34725.TCS34725(i2c)
    return i2c,sensor

def wait_for_connection():


def main()
    i2c,sensor = setup_rpi()

    socket.socket()

if __name__ == "__main__":
    setup_rpi()
    main()