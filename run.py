#!/usr/bin/env python
#
#   rtl-aprs-igate - Configuration File Reader
#

#import copy
#import logging
#import os
#import traceback
#import json
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
#if not os.path.isfile(filename):
#    logging.critical("Config file %s does not exist!" % filename)


config = RawConfigParser(rtl_aprs_igate_config)
config.read(filename)

frequency = config.getfloat("rtl_fm", "frequency")
device_idx = config.get("rtl_fm", "device_idx")
ppm = config.getfloat("rtl_fm", "ppm")
bias = config.getboolean("rtl_fm", "bias")
gain = config.getfloat("rtl_fm", "gain")

# If there is device_idx (which is a string) specified, else don't even print a -d argument
if device_idx != '0':
    device_idx_param = f"-d {str(device_idx)} "
else:
    device_idx_param = ""
    
# If there is a PPM specified, else don't even print a -p argument
if ppm != 0:
    ppm_param = f"-p {ppm} "
else:
    ppm_param = ""

# If there is a gain specified, else don't even print a -g argument
if gain != -1:
    gain_param = f"-g {gain:.1f} "
else:
    gain_param = ""

#print(rtl_aprs_igate_config)

# Generate the rtl_fm command based on the inputs above
rtl_fm_cmd = (
    f"rtl_fm -f {frequency} "
    f"{device_idx_param}"
    f"{'-T ' if bias else ''}"
    f"{ppm_param}"
    f"{gain_param}"
    f"| direwolf -c direwolf.conf -r 24000 -"
)

print("command: ", rtl_fm_cmd)

