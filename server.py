# This is the kitchen device = SERVER / Laundry Up
# This is the Laundry Program
import RPi.GPIO as GPIO
import socket
from datetime import datetime
from time import sleep
import os
import sys


# server_IP = 192.168.1.199
# Define parameters for communicating with laundry raspberry
HOST = '192.168.1.199'
PORT = 12345

server_socket = socket.socket()
server_socket.bind((HOST, PORT))

WASHER = 8  # LED for Washer
WORK = 12  # LED for Working Mode
# BUTTON = 19  # Reset button
SPEAKER = 7  # Active Speaker

# Configure the GPIO pins, numbering based on physical position
GPIO.setmode(GPIO.BOARD)
GPIO.setup(WASHER, GPIO.OUT)
GPIO.setup(WORK, GPIO.OUT)
# GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SPEAKER, GPIO.OUT)

# I am up and running ...
GPIO.output(WASHER, GPIO.HIGH)
# GPIO.output(DRYER, GPIO.HIGH)
GPIO.output(SPEAKER, GPIO.HIGH)
sleep(1)
GPIO.output(SPEAKER, GPIO.LOW)
GPIO.output(WASHER, GPIO.LOW)
# GPIO.output(DRYER, GPIO.LOW)

# Wait 2 minutes for the system to boot up and update the date/time
sleep(120)

file_name = datetime.strftime(datetime.now(), '%Y%m%d') + '_client_log.txt'

with open('/home/pi/Desktop/logs/my_log.txt', 'w') as file_log:
    file_log.write('File Name = ' + file_name)

with open('/home/pi/Desktop/logs/' + file_name, 'w') as log_file:
    log_file.write(str(datetime.now()) + ': Program starts.\n')


def write_log(log_text: str):
    with open('/home/pi/Desktop/logs/' + file_name, 'a') as f:
        f.write(log_text)


def print_save(msg_txt: str):
    msg = str(datetime.now()) + msg_txt
    print(msg)
    write_log(msg)


def beep_beep(n, d):
    for i in range(n):
        GPIO.output(SPEAKER, GPIO.HIGH)
        sleep(d)
        GPIO.output(SPEAKER, GPIO.LOW)
        sleep(d)


while True:
    try:

        # wait for signal from the other Raspberry
        print_save(': Listening to inputs from the client ... \n')
        server_socket.listen()
        conn, addr = server_socket.accept()
        data = conn.recv(1024)

        data = data.decode()
        print_save(f': Connected by ... {addr}\n')

        # We do not need this button
        # rst = GPIO.wait_for_edge(BUTTON, GPIO.RISING, timeout=300)

        # if rst:
        #     # turn both LEDs OFF
        #     print('Turn OFF the LEDs and stop playing the sound')

        #     GPIO.output(WASHER, GPIO.LOW)
        #     GPIO.output(DRYER, GPIO.LOW)
        #     GPIO.output(SPEAKER, GPIO.LOW)

        if data == 'w':
            print_save(': Washer is finished.\n')
            conn.sendall(b'Thank you.')

            # turn the Washer LED ON and play sound
            GPIO.output(WASHER, GPIO.HIGH)
            GPIO.output(WORK, GPIO.LOW)
            beep_beep(3, 1)

        # elif data == 'd':
        #     print_save(': Dryer is finished.\n')
        #     conn.sendall(b'Thank you.')
        #
        #     # turn the Dryer LED ON and play sound
        #     GPIO.output(DRYER, GPIO.HIGH)
        #     beep_beep(3, 1)

        elif data == 't':
            print_save(': Test message from ' + str(addr) + '.\n')
            conn.sendall(b'Connection established.')
            beep_beep(2, 0.2)
            GPIO.output(WORK, GPIO.HIGH)

        elif data == 'r':
            print_save(': Reset the beep flags.\n')
            GPIO.output(WASHER, GPIO.LOW)
            GPIO.output(WORK, GPIO.HIGH)
            conn.sendall(b'Reset signal received.')

        elif data == 's':
            print_save(': Received SHUTDOWN command.\n')
            # conn.sendall(b'SHUTDOWN command received.')
            beep_beep(5, 0.2)
            print_save(': I am shutting down now.\n')
            os.system("sudo shutdown -h 1")
            sys.exit()

    except KeyboardInterrupt:
        GPIO.cleanup()
        print_save(': Program exits.\n')
