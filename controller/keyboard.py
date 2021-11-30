# Keyboard demo

import sys
import subprocess
from time import sleep
from os import path
from os import walk
import serial
import RPi.GPIO as GPIO

# Rpi e-ink hat switch BCM pins
SW1 = 21
# scancode assignments (https://kbdlayout.info/KBDFI/scancodes finnish layout)
keys = {\
        "KEY_OEM_3":SW1,\
        }
# key scancodes [down,up]
scancodes = {\
        "KEY_OEM_3":["\x00\x33","\x00\x44"] #TODO placeholder codes
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
    # Print each found image into its correspoding display
    images = next(walk(img_path), (None, None, []))[2]
    for i in images:
        # Strip filename suffix
        iname=i.split(".")[0]
        try:
            # Check for existence
            if keys[iname]:
                # here we would select the correct key, but
                # we got only one key.
                args=f"{img_path}/{i}"
                try:
                    p = subprocess.Popen([exe, args], stdin=subprocess.DEVNULL)
                    stdout,stderr = p.communicate()
                except subprocess.CalledProcessError as e:
                    print("Error: Could not update key subprocess popen.")
                    print(e)
                    print("Exit.")
                    sys.exit()
            else:
                continue
        except KeyError:
            continue

# Switch down callback
def send_key_down(channel):
    # Demo hardcoded for SW1
    try:
        UART.write(scancodes["KEY_OEM_3"][0].encode())
    except serial.SerialException as e:
        print(f"Error: Couldn't send {scancodes['KEY_OEM_3'][0]} to UART")
        print(e)
        print("Exit.")
        sys.exit()

# Switch up callback
def send_key_up():
    # Demo hardcoded for SW1
    try:
        UART.write(scancodes["KEY_OEM_3"][1].encode())
    except serial.SerialException as e:
        print(f"Error: Couldn't send {scancodes['KEY_OEM_3'][0]} to UART")
        print(e)
        print("Exit.")
        sys.exit()

if __name__ == "__main__":
    # Configure SW1 as BCM input with default pull low
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SW1,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
    # Configure callback for button press
    GPIO.add_event_detect(SW1,GPIO.RISING,callback=send_key_down, bouncetime=200)
    # Main loop
    while True:
        # Read UART for language code <base>_<lang>
        try:
            rxd = str(UART.read().decode())
            img = get_img(rxd)
            if img != "":
                update_key(img)
        # Error
        except serial.SerialException as e:
            print("Error: Serial could not read.")
            print(e)
            print("Exit.")
            break
        # Check for sw1 falling edge (demo, otherwise full matrix)
        try:
            GPIO.wait_for_edge(SW1, GPIO.FALLING)
            send_key_up()
        # User exit
        except KeyboardInterrupt:
            print("Exit from signal")
            break
        sleep(0.1)
    # Clean up
    GPIO.cleanup()
    sys.exit()
