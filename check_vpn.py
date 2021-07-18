"""
Script to check if Nordvpn is connected
Need root proviledges, put command in root crontab to execute at startup
To be run on Up Squared (but compatible with Raspberry and other boards)
Up Squared reference links:
https://github.com/up-board/up-community/wiki/Pinout_UP2
https://github.com/up-board/up-community/wiki/MRAA
https://github.com/eclipse/mraa/blob/master/docs/up2.md

Green: connected
Yellow: disconnected
Red: anything else
"""
import subprocess
import mraa
import time
import re

# Define pins
r_pin_no = 40
y_pin_no = 38
g_pin_no = 36

# Export the GPIO pin for use
r_pin = mraa.Gpio(r_pin_no)
y_pin = mraa.Gpio(y_pin_no)
g_pin = mraa.Gpio(g_pin_no)

# Small delay to allow udev rules to execute (necessary only on up)
time.sleep(0.1)

# Configure the pin direction
r_pin.dir(mraa.DIR_OUT)
y_pin.dir(mraa.DIR_OUT)
g_pin.dir(mraa.DIR_OUT)

# Turn off all pins to start
r_pin.write(0)
y_pin.write(0)
g_pin.write(0)

# Compile regex for status check
re_conn = re.compile(r".*Status: Connected.*")
re_disc = re.compile(r".*Status: Disconnected.*")

# Loop
while True:
    # Check Nordvpn status
    status = subprocess.run(["nordvpn", "status"] , capture_output=True)
    vpn_status = status.stdout.decode("UTF-8")
    # If connected, turn on green and turn off everything else
    if re.match(re_conn, vpn_status):
        r_pin.write(0)
        y_pin.write(0)
        g_pin.write(1)
    # If disconnected, turn on yellow
    elif re.match(re_disc, vpn_status):
        r_pin.write(0)
        y_pin.write(1)
        g_pin.write(0)
    # Else turn on red
    else:
        r_pin.write(1)
        y_pin.write(0)
        g_pin.write(0)
    # wait some seconds between checks
    time.sleep(30)
