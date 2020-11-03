# This is the Laundry client device = CLIENT / Laundry Down
# This is the Laundry Program
import RPi.GPIO as GPIO
import socket
from datetime import datetime
from time import sleep


# Define input/output pins
WASHER = 8
BUTTON = 11
LED = 16
DRYER = 35

# client_IP = 192.168.2.209
# Define parameters for communicating with monitoring raspberry
HOST = '192.168.2.208'
PORT = 12345

file_name = datetime.strftime(datetime.now(), '%Y%m%d') + '_client_log.txt'


def write_log(log_text: str):
    with open('/home/pi/Desktop/logs/' + file_name, 'a') as f:
        f.write(log_text)


def print_save(msg_txt: str):
    msg = str(datetime.now()) + msg_txt
    print(msg)
    write_log(msg)


def conn_to_server(my_str):
    no_conn = True

    while no_conn:
        try:
            print_save(f': Probing connection to server {HOST} on port {PORT}\n')
            s = socket.socket()
            s.connect((HOST, PORT))
            print_save(f': Sending {my_str} to the server\n')
            s.sendall(my_str)
            data = s.recv(1024)
            print_save(f': Server responded: {data}')
            no_conn = False
            print_save(': Connection to the server has been established.\n')
            print_save(f': The server responded "{data.decode()}".\n')
            print_save(': Waiting for signals from sensor ...\n')

        except Exception as e:
            print_save(f': There is no connection to the server. {e}\n')
            sleep(60)


print_save(': Program starts.\n')

conn_to_server(b't')

# Configure GPIO pins, numbering based on physical position
GPIO.setmode(GPIO.BOARD)
GPIO.setup(WASHER, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# GPIO.setup(DRYER, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LED, GPIO.OUT)

GPIO.output(LED, GPIO.HIGH)
w = 0
d = 0


def send_signal(w_d_r):

    if w_d_r == b'w':
        print_save(': Sending "washer" message to monitoring raspberry\n')
    # elif w_d_r == b'd':
    #     print_save(': Sending "dryer" message to monitoring raspberry\n')
    elif w_d_r == b'r':
        print_save(': Sending Reset signal\n')
    else:
        print_save(f': It should have been "w", "d" or "r" but it is {w_d_r.decode()}\n')

    conn_to_server(w_d_r)


curr_time = datetime.now()
valid_signal = 0
bln = True  # if bln is False, do not compute the signal from washer sensor

while True:
    try:
        wsh = GPIO.wait_for_edge(WASHER, GPIO.RISING, timeout=300)
        # dry = GPIO.wait_for_edge(DRYER, GPIO.RISING, timeout=300)
        rst = GPIO.wait_for_edge(BUTTON, GPIO.RISING, timeout=300)
        
        if wsh and bln:
            w += 1
            print_save(f': Received signal # {w} from the washer sensor.\n')
            duration = datetime.now() - curr_time
            print_save(f': duration between signals: {duration.seconds} seconds.\n')
            if duration.seconds > 3:
                curr_time = datetime.now()
            else:
                valid_signal = valid_signal + 1
                print_save(f': valid signal #: {valid_signal}. If = 3 then contact server.\n')
                if valid_signal == 3:
                    print_save(': Turning OFF the LED and notifying the server ...\n')
                    GPIO.output(LED, GPIO.LOW)
                    send_signal(b'w')
                    print_save(': Waiting for reset signal ...\n')
                    bln = False

        if rst and not bln:
            # Send reset notification to the Server
            w = 0
            d = 0
            send_signal(b'r')
            print_save(': Reset performed. Turning ON the LED.\n')
            GPIO.output(LED, GPIO.HIGH)
            bln = True
            print_save(': Waiting for signals from sensor ...\n')

    except KeyboardInterrupt:
        GPIO.cleanup()
        print_save(': Program exits.\n')
