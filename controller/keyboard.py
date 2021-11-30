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
    root = "/home/pi/keyboard_firmware/e-ink/pic"
    base = tok[0].strip()
    lang = tok[1].strip()
    img_path = ""
    if path.isdir(f"{root}/{base}/{lang}"):
        # absolute path must be provided for os.walk later on
        img_path = f"{root}/{base}/{lang}"
    else:
        print(f"Error: unresolved lang_code {lang_code}")
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

def send_key(scancode):
    try:
        UART.write(scancode)
    except serial.SerialException as e:
        print(f"Error: Couldn't send {scancode} to UART")
        print(e)
        GPIO.cleanup()
        sys.exit()

# Switch up callback hardcoded for SW1
def sw_callback():
    if GPIO.input(SW1):
        # Switch down
        send_key(scancodes["KEY_OEM_3"][1].encode())
    else:
        # Switch up
        send_key(scancodes["KEY_OEM_3"][1].encode())

if __name__ == "__main__":
    # Configure SW1 as BCM input with default pull low
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SW1,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
    # Configure callback for button press
    GPIO.add_event_detect(SW1,GPIO.RISING,callback=sw_callback, bouncetime=200)
    # Main loop
    while True:
        # Read UART for language code <base>_<lang>
        try:
            rxd = str(UART.readline().decode())
            img = get_img(rxd)
            if img != "":
                update_key(img)
        # Error
        except serial.SerialException as e:
            print("Error: Serial could not read.")
            print(e)
            print("Exit.")
            break
        # Manual exit
        try:
            sleep(0.1)
        except KeyboardInterrupt:
            break
    # Clean up
    GPIO.cleanup()
    sys.exit()
