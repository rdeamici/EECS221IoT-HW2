import time
import board
import sys
import adafruit_tcs34725
import RPi.GPIO as GPIO

# Setup LED lights
green = 5
red = 6
blue = 13

GPIO.setmode(GPIO.BCM)
GPIO.setup(green, GPIO.OUT)
GPIO.setup(red, GPIO.OUT)
GPIO.setup(blue, GPIO.OUT)
