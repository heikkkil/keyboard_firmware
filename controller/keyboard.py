# Keyboard demo

import sys
import serial
import RPi.GPIO as GPIO
from subprocess import Popen
from time import sleep
from os import path
from os import walk

# Rpi e-ink hat switch BCM pins
SW1 = "21"
SW2 = "20"
# scancode assignments (https://kbdlayout.info/KBDFI/scancodes finnish layout)
keys = {\
        "KEY_OEM_3":SW1,\
        "KEY_LSHIFT":SW2\
        }
keycodes = {\
        "KEY_OEM_3":"\x00\x33" #TODO real code
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
    if path.isdir(base) and path.isdir(lang):
        # absolute path must be provided for os.walk later on
        img_path = f"{root}/{base}/{lang}"
    else:
        print("Error: unresolved lang_code {lang_code}")
    return img_path

# Draw key character image into e-ink with subprocess
def update_key(img_path):
    exe="/home/pi/keyboard_firmware/bin/edp.exe"
    # Print each found image into its correspoding display
    images = next(walk(img_path), (None, None, []))[2]
    for img in images:
        try
            if keys[img]:
            # here we would select the correct key, but we got only one key.
            cmd=f"{exe} {img}"
        except KeyError:
            continue
    try:
        Popen(["/bin/bash", cmd])
    except:
        print("Error: Could not update key (subprocess popen). Exit.")
        sys.exit()

# Send switch event with keycode to host with UART
def send_key(scancode):
    try:
        UART.write(scancode)
    except:
        print("Error: Could not send to serial. Exit.")
        sys.exit()

# Prioritize key image update over transmission
if __name__ == "__main__":
    # Configure button1
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(SW1,GPIO.IN)

    # Read UART for languge code base_lang
    try:
        rxd = UART.read()
        img = get_img(rxd)
        if img != "":
            update_key(img)
    # Error
    except:
        print("Error: Serial could not read. Exit.")
        sys.exit()
    #TODO test if serial flushing is needed as "finally"

    # Poll switch 1, here we would listen to or poll the whole matrix, but no.
    try:
        while True:
            if GPIO.input(SW1):
                send_key(scancode)
                pass
            sleep(0.1)
    # Error
    except:
        print(f"Error: GPIO {SW1} could not be read. Exit.")
        sys.exit()
