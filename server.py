# This is the kitchen device = SERVER / Laundry Up
# This is the Laundry Program
import RPi.GPIO as GPIO
import socket
from datetime import datetime
from time import sleep


# server_IP = 192.168.2.208
# Define parameters for communicating with laundry raspberry
HOST = '192.168.2.208'
PORT = 12345

server_socket = socket.socket()
server_socket.bind((HOST, PORT))

WASHER = 8  # LED for Washer
DRYER = 12  # LED for Dryer
# BUTTON = 19  # Reset button
SPEAKER = 7  # Active Speaker

# Configure the GPIO pins, numbering based on physical position
GPIO.setmode(GPIO.BOARD)
GPIO.setup(WASHER, GPIO.OUT)
GPIO.setup(DRYER, GPIO.OUT)
# GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SPEAKER, GPIO.OUT)

# I am up and running ...
GPIO.output(WASHER, GPIO.HIGH)
GPIO.output(DRYER, GPIO.HIGH)
GPIO.output(SPEAKER, GPIO.HIGH)
sleep(1)
GPIO.output(SPEAKER, GPIO.LOW)
GPIO.output(WASHER, GPIO.LOW)
GPIO.output(DRYER, GPIO.LOW)

file_name = datetime.strftime(datetime.now(), '%Y%m%d') + '_server_log.txt'


def write_log(log_text: str):
    with open('/home/pi/Desktop/logs/' + file_name, 'a') as f:
        f.write(log_text)


def print_save(msg_txt: str):
    msg = str(datetime.now()) + msg_txt
    print(msg)
    write_log(msg)


def beep_beep(n):
    for i in range(n):
        GPIO.output(SPEAKER, GPIO.HIGH)
        sleep(1)
        GPIO.output(SPEAKER, GPIO.LOW)
        sleep(1)


print_save(': Program starts.\n')

# curr_time = datetime.now()
# valid_signal = 0

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
            beep_beep(3)

        elif data == 'd':
            print_save(': Dryer is finished.\n')
            conn.sendall(b'Thank you.')

            # turn the Dryer LED ON and play sound
            GPIO.output(DRYER, GPIO.HIGH)
            beep_beep(3)

        elif data == 't':
            print_save(': Test message from ' + str(addr) + '\n')
            conn.sendall(b'Connection established.')

        elif data == 'r':
            print_save(': Reset the beep flags.\n')
            GPIO.output(WASHER, GPIO.LOW)
            GPIO.output(DRYER, GPIO.LOW)
            conn.sendall(b'Reset signal received.')

        data = ''

    except KeyboardInterrupt:
        GPIO.cleanup()
        print_save(': Program exits.\n')
