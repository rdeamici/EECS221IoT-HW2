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

# create connection to rgb sensor
RGB_SENSOR = adafruit_tcs34725.TCS34725(board.I2C())


# setup UDP server on RPi
RPI_ADDRESS = '192.168.220.8'
RPI_PORT = 4210
RPiUDPServer = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# base line light level for both sensors
PHOTO_RESISTOR_BASELINE = 0
RGB_SENSOR_BASELINE = 0


def get_esp_data(timeout):
    '''
    listen for data to come in from the esp8266
    if the designated timeout is reached,
    the function will return empty strings for both values
    '''
    RPiUDPServer.settimeout(timeout)
    try:
        esp_data, esp_address = RPiUDPServer.recvfrom(255)
    except socket.timeout:
        print("socket timed out!")
        esp_data, esp_address = '',''
    except KeyboardInterrupt:
        raise
    
    return esp_data, esp_address


def slow_blink_time_to_sleep(start):
    '''
    ensure led stays in current state for at least half a second
    '''
    end = time.time()
    time_to_sleep = 1 - (end - start)

    if time_to_sleep < 0:
        raise ValueError("Took more than a second ({})  to check connection".format(end-start))

    return time_to_sleep


def wait_for_connection():
    '''
    flashes LED continuously while checking
    for data sent via UDP connection
    '''
    esp_address = ''
    onoff = [LOW, HIGH]
    switch = True

    while not esp_address:
        GPIO.output(RED,onoff[switch])
        start_time = time.time()
        esp_data , esp_address = get_esp_data(timeout=0.9)
        time_to_sleep = slow_blink_time_to_sleep(start_time)
        time.sleep(time_to_sleep)
        switch = not switch

    print(esp_address)
    return esp_data, esp_address




def main():
    '''
    main function
    '''
    #           ESP, RPI
    lights = [GREEN, BLUE]
    timed_out = True # 2 minute timeout
    try:
        while True:
            if timed_out:
                # step 1: flash light slowly while waiting for data from esp8266
                _ , (esp_address,esp_port) = wait_for_connection()
                # step 2: flash light quickly for 2 seconds
                for _ in range(10):
                    GPIO.output(RED,LOW)
                    time.sleep(0.1)
                    GPIO.output(RED,HIGH) # ensures red light will be left on
                    time.sleep(0.1)
                
            timed_out = False
            # step 3: get values from esp and from rgb sensor
            both_sensors_data = get_8_sensor_readings(timeout=2)

            # if the server ever waits more than 10 seconds for a
            # reading from the esp, then revert back to step 1
            if not both_sensors_data:
                timed_out = True
                GPIO.output(RED,LOW)
                GPIO.output(GREEN,LOW)
                GPIO.output(BLUE,LOW)
            else:
                light = find_brighter_light(both_sensors_data)
                high_light = lights[light]
                low_light = lights[not light]

                GPIO.output(high_light, HIGH)
                GPIO.output(low_light,LOW)

                return_data = int.to_bytes(light,1,'big')
                RPiUDPServer.sendto(return_data,(esp_address,esp_port))
    except Exception as e:
        print(e)
        print("\nturning off all lights...")
        GPIO.output(RED,LOW)
        GPIO.output(GREEN,LOW)
        GPIO.output(BLUE,LOW)
        print("Done! cleaning up GPIO...")
        GPIO.cleanup()
        print("Done!")
        return


def set_baselines(both_sensors_data):
    total_data_points = len(both_sensors_data)
    photo_resistor_avg = sum([d[0] for d in both_sensors_data])/total_data_points
    rgb_sensor_avg = sum([d[1] for d in both_sensors_data])/total_data_points

    return photo_resistor_avg,rgb_sensor_avg

def find_brighter_light(both_sensors_data):
    '''
    Get avg of all sensor readings for both sensors.
    If esp has a higher average, return False(0).
    If rgb has higher average, return True(1).
    '''
    esp_avg, rgb_avg = 0,0

    for esp_data,rgb_data in both_sensors_data:
        esp_avg += esp_data
        rgb_avg += rgb_data

    esp_avg /= len(both_sensors_data)
    rgb_avg /= len(both_sensors_data)

    return esp_avg < rgb_avg



def get_8_sensor_readings(timeout):
    '''
    get exactly 8 pairs of sensor readings
    '''
    both_sensors_data = []
    while len(both_sensors_data) < 8:
        esp_data, _ = get_esp_data(timeout)
        if esp_data:
            esp_data = int(esp_data)
            rgb_data = RGB_SENSOR.lux
            both_sensors_data.append((esp_data,rgb_data))
        else:
            return []
        print(both_sensors_data)
    return both_sensors_data

if __name__ == "__main__":
    # start UDP server
    RPiUDPServer.bind((RPI_ADDRESS,RPI_PORT))
    print("UDP server up and listening...")

    main()
