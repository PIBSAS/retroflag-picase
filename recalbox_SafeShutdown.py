import subprocess
import os
import time
from multiprocessing import Process

#initialize pins
powerPin = 3 #pin 5
ledPin = 14 #TXD Pin 8
resetPin = 2 #pin 3
powerenPin = 4 #pin 7

def set_gpio(pin, mode, level=None, pull=None):
	cmd = ["raspi-gpio", "set", str(pin), mode]
	if pull:
		cmd.append(pull)
	if level:
		cmd.append(level)
	subprocess.run(cmd, check=True)

def get_level(pin):
	result = subprocess.run(["raspi-gpio", "get", str(pin)], capture_output=True, text=True)
	line = result.stdout.strip()
	
	for part in line.split():
		if part.startswith("level="):
			return int(part.split("=")[1])
	return None

#initialize GPIO settings
def init():
	set_gpio(powerPin, "ip", pull="pu")
	set_gpio(resetPin, "ip", pull="pu")
	set_gpio(ledPin, "op", level="dh")
	set_gpio(powerenPin, "op", level="dh")
	
#waits for user to hold button up to 1 second before issuing poweroff command
def poweroff():
	while True:
		level = get_level(powerPin)
		if level == 0:
			os.system("killall emulationstation")
			time.sleep(5)
			os.system("shutdown -h now")
			break
		time.sleep(0.1)

#blinks the LED to signal button being pushed
def ledBlink():
	while True:
		level = get_level(powerPin)
		if level == 0:
			while get_level(powerPin) == 0:
				subprocess.run(["raspi-gpio", "set", str(ledPin), "dl"])
				time.sleep(0.2)
				subprocess.run(["raspi-gpio", "set", str(ledPin), "dh"])
				time.sleep(0.2)
		else:
			subprocess.run(["raspi-gpio", "set", str(ledPin), "dh"])
		time.sleep(0.1)

#resets the pi
def reset():
	while True:
		level = get_level(resetPin)
		if level == 0:
			os.system("killall emulationstation")
			time.sleep(5)
			os.system("shutdown -r now")
			break
		time.sleep(0.1)

if __name__ == "__main__":
	#initialize GPIO settings
	init()
	#create a multiprocessing.Process instance for each function to enable parallelism 
	powerProcess = Process(target = poweroff)
	ledProcess = Process(target = ledBlink)
	resetProcess = Process(target = reset)
	
	powerProcess.start()
	ledProcess.start()
	resetProcess.start()
	
	powerProcess.join()
	ledProcess.join()
	resetProcess.join()
