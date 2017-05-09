#!/usr/bin/python

import sys
from time import sleep
from pid.decorator import pidfile
import os
sys.path.append(os.path.abspath('..'))

import RPi.GPIO as GPIO

import SimpleConfig
import LightController
import PumpController
import TemperatureController

@pidfile()
def main():
    print "Starting Aquaponics System \n"
    print "\n"

    config = SimpleConfig.SimpleConfig(['/home/pi/aquaponics-scu/config/aquaponics.cfg'])

    # Set GPIO mode
    GPIO.setmode(GPIO.BOARD)

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
        print "Completed loop: {} \n".format(count)
        print "Sleeping 60 seconds before next loop"
        count += 1
        sleep(60)

if __name__ == '__main__':
    main()
