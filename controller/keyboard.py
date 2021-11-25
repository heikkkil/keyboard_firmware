# Keyboard demo

import sys
import subprocess
from time import sleep
from os import path
from os import walk
import serial
import RPi.GPIO as GPIO

# Rpi e-ink hat switch BCM pins
SW1 = "21"
SW2 = "20"
# scancode assignments (https://kbdlayout.info/KBDFI/scancodes finnish layout)
keys = {\
        "KEY_OEM_3":SW1,\
        "KEY_LSHIFT":SW2\
        }
# key scancodes [down,up]
scancodes = {\
        "KEY_OEM_3":["\x00\x33","\x00\x00"] #TODO real code
        }
# UART device (RDX = GPIO 14, TDX = GPIO 15)
UART = serial.Serial("/dev/ttyS0", 9600)

# Lookup and return drawable image path for language code
def get_img(lang_code):
    tok = str(lang_code).split("_")
    root = "/home/pi/keyboard_firmware/pic"
    base = tok[0]
    lang = tok[1]
    img_path = ""
    if path.isdir(f"{root}/{base}") and path.isdir(f"{root}/{base}/{lang}"):
        # absolute path must be provided for os.walk later on
        img_path = f"{root}/{base}/{lang}"
    else:
        print("Error: unresolved lang_code {lang_code}")
    return img_path

# Draw key character image into e-ink with subprocess
def update_key(img_path):
    exe="/home/pi/keyboard_firmware/epd.exe"
    cmd="echo error"
    # Print each found image into its correspoding display
    images = next(walk(img_path), (None, None, []))[2]
    print(images)
    for i in images:
       iname=i.split(".")[0]
       try:
            if keys[iname]:
                # here we would select the correct key, but we got only one key.
                args=f"{img_path}/{i}"
                print(cmd)
                try:
                    subprocess.Popen([exe, args])
                except subprocess.CalledProcessError as e:
                    print("Error: Could not update key subprocess popen.")
                    print(e)
                    print("Exit.")
                    sys.exit()
            else:
                continue
       except KeyError:
            continue

# Send switch event with keycode to host with UART
def send_key(scancode):
    try:
        UART.write(scancode)
    except serial.SerialException as e:
        print("Error: Could not send to serial.")
        print(e)
        print("Exit.")
        sys.exit()

# Prioritize key image update over transmission
if __name__ == "__main__":
    # Configure button1
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(SW1,GPIO.IN)
    # demo specific flag for key status
    DOWN = False
    while True:
        # Read UART for languge code base_lang
        try:
            rxd = UART.read()
            img = get_img(rxd)
            if img != "":
                update_key(img)
        # Error
        except serial.SerialException as e:
            print("Error: Serial could not read.")
            print(e)
            print("Exit.")
            break
        #TODO test if serial flushing is needed as "finally"
        # Here we would listen to or poll the whole matrix, but now just one.
        # TODO change to edge detection
        for key in keys:
            try:
                if GPIO.input(keys[key]):
                    send_key(scancodes[key][0])
                    DOWN = True
                else:
                    if DOWN:
                        send_key(scancodes[key][1])
                        DOWN = False
            # Error
            except Exception as e:
                print(f"Error: GPIO {SW1} could not be read.")
                print(e)
                print("Exit.")
                break
        sleep(0.1)
    sys.exit()

