#!/usr/bin/env python3
#
#   rtl-aprs-igate - Configuration File Reader
#     Reads a RTL-SDR configuration file, verifies input values,
#     and generates the rtl_fm options
#
#   Copyright (C) 2025 Bryan Klofas bklofas@gmail.com
#   Released under MIT license

import logging
import os
import sys
import subprocess
from configparser import RawConfigParser


# Set up defaults
filename = "station.conf"
rtl_aprs_igate_config = {
    # SDR settings
    "frequency": 144.39,
    "device_idx": 0,
    "ppm": 0,
    "bias": False,
    "gain": -1
}


# Check if the station.conf file is present
if not os.path.isfile(filename):
    logging.critical("Config file %s does not exist!" % filename)
    sys.exit()


# Read the station.conf file
config = RawConfigParser(rtl_aprs_igate_config)
config.read(filename)


# Set the configuration file options
frequency = config.getfloat("rtl_fm", "frequency")
device_idx = config.get("rtl_fm", "device_idx")
ppm = config.getfloat("rtl_fm", "ppm")
gain = config.getfloat("rtl_fm", "gain")
try:
    bias = config.getboolean("rtl_fm", "bias")
except: 
    logging.warning("Config file: Bias-Tee option is not defined as True or False. Setting to False.")
    bias = False

# Verify config file options are sane
if frequency < 100 or frequency > 800:
    logging.critical("Config file: Frequency %s is not valid! (Outside 100 - 800 MHz)" % frequency)
    sys.exit()

if ppm < -20 or ppm > 20:
    logging.critical("Config file: PPM %s is not valid! (Outside +/- 20 ppm)" % ppm)
    sys.exit()

if gain < -1 or gain > 40:
    logging.critical("Config file: Gain %s is probaly not valid!" % gain)
    sys.exit()


# Generate the arguments based on config file
# If there is device_idx (which is a string) specified, otherwise don't even print a -d argument
if device_idx != '0':
    device_idx_param = f"-d {str(device_idx)} "
else:
    device_idx_param = ""
    
# If there is a PPM specified, otherwise don't even print a -p argument
if ppm != 0:
    ppm_param = f"-p {ppm} "
else:
    ppm_param = ""

# If there is a gain specified, otherwise don't even print a -g argument
if gain != -1:
    gain_param = f"-g {gain:.1f} "
else:
    gain_param = ""


# Print the options
print(f"Frequency: {frequency:.3f} MHz")
print(f"Device_index: {device_idx}")
print(f"PPM: {ppm}")
print(f"Bias-Tee: {bias}")
print(f"Gain: {gain}")


# Generate the rtl_fm command based on the arguments above
rtl_fm_cmd = (
    f"rtl_fm -f {frequency} "
    f"{device_idx_param}"
    f"{'-T ' if bias else ''}"
    f"{ppm_param}"
    f"{gain_param}"
    f"| direwolf -c direwolf.conf -r 24000 -"
)

print("command:", rtl_fm_cmd)


# Send the command to the container to run
subprocess.run(rtl_fm_cmd, 
    shell=True, check=True, text=True)

