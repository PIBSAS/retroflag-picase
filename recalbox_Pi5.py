import subprocess
import os
import time
from multiprocessing import Process

# Pines BCM
powerPin = 3     # pin 5
ledPin = 14      # TXD Pin 8
resetPin = 2     # pin 3
powerenPin = 4   # pin 7

def set_gpio(pin, *args):
    # Ejemplo: set_gpio(14, "op", "dh")
    cmd = ["pinctrl", "set", str(pin)] + list(args)
    subprocess.run(cmd, check=True)

def get_level(pin):
    result = subprocess.run(["pinctrl", "get", str(pin)], capture_output=True, text=True)
    line = result.stdout.strip()
    for part in line.split():
        if part.startswith("level="):
            return int(part.split("=")[1])
    return None

def init():
    set_gpio(powerPin, "ip")      # input
    set_gpio(resetPin, "ip")
    set_gpio(ledPin, "op", "dh")  # output high
    set_gpio(powerenPin, "op", "dh")

def poweroff():
    while True:
        if get_level(powerPin) == 0:
            os.system("killall emulationstation")
            time.sleep(5)
            os.system("shutdown -h now")
            break
        time.sleep(0.1)

def ledBlink():
    while True:
        if get_level(powerPin) == 0:
            while get_level(powerPin) == 0:
                set_gpio(ledPin, "dl")
                time.sleep(0.2)
                set_gpio(ledPin, "dh")
                time.sleep(0.2)
        else:
            set_gpio(ledPin, "dh")
        time.sleep(0.1)

def reset():
    while True:
        if get_level(resetPin) == 0:
            os.system("killall emulationstation")
            time.sleep(5)
            os.system("shutdown -r now")
            break
        time.sleep(0.1)

if __name__ == "__main__":
    init()
    powerProcess = Process(target=poweroff)
    ledProcess = Process(target=ledBlink)
    resetProcess = Process(target=reset)

    powerProcess.start()
    ledProcess.start()
    resetProcess.start()

    powerProcess.join()
    ledProcess.join()
    resetProcess.join()
