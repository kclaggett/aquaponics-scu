#!/usr/bin/python

import sys
from time import sleep
import os
sys.path.append(os.path.abspath('..'))

import SimpleConfig
import LightController
import PumpController
import TemperatureController

print "Starting Aquaponics System \n"
print "\n"

config = SimpleConfig.SimpleConfig('/home/pi/aquaponics-scu/config/aquaponics.cfg')

pumps = PumpController.PumpController(config)
lights = LightController.LightController(config)
temp = TemperatureController.TemperatureController(config)

print "Initialized Modules: Lights, Pumps, Temperature \n"
print "\n"

print "Initializing Loop, press Ctrl + C to exit \n"

count = 0
while 1:
    pumps.runModule()
    sleep(1)
    lights.runModule()
    sleep(1)
    temp.runModule()
    current_temp = temp.getTemp()
    print "Completed loop: {} Current Temp detected: {} \n".format(count, current_temp)
    print "Sleeping 60 seconds before next loop"
    sleep(60)
