"""
Script to chek if VPN is connected and perform actions
according to flag in file /home/luigi/selenium1/nordvpn_target

If VPN is connected:
    - If flag == 0, disconnect

If VPN is disconnected:
    - If flag == 1, connect

Display status in LED
Green: connected
Yellow: disconnected
Red: anything else, and in case of mismatch between status and target
Need root proviledges, put command in root crontab to execute at startup
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
    # Check flag in file, only read first character
    with open("/home/luigi/selenium1/nordvpn_target", "r") as f:
        target = f.read(1)
    # If connected, turn on green and turn off everything else
    if re.match(re_conn, vpn_status):
        r_pin.write(0)
        y_pin.write(0)
        g_pin.write(1)
        # If connected and flag is 0, turn on red and disconnect
        if target == "0":
            r_pin.write(1)
            y_pin.write(0)
            g_pin.write(0)
            _ = subprocess.run(["nordvpn", "d"] , capture_output=True)
    # If disconnected, turn on yellow
    elif re.match(re_disc, vpn_status):
        r_pin.write(0)
        y_pin.write(1)
        g_pin.write(0)
        # If disconnected and flag is 1, turn on red and connect
        if target == "1":
            r_pin.write(1)
            y_pin.write(0)
            g_pin.write(0)
            _ = subprocess.run(["nordvpn", "1"] , capture_output=True)
    # Anything else, turn on red
    else:
        r_pin.write(1)
        y_pin.write(0)
        g_pin.write(0)
    # wait 30 seconds between checks
    time.sleep(30)
