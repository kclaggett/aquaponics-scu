#!/usr/bin/python

import sys
from time import sleep
from pid.decorator import pidfile
import logging
from logging.handlers import RotatingFileHandler
import os
sys.path.append(os.path.abspath('..'))

import RPi.GPIO as GPIO

import SimpleConfig
import LightController
import PumpController
import TemperatureController

@pidfile()
def main():
    config = SimpleConfig.SimpleConfig(['/home/pi/aquaponics-scu/config/aquaponics.cfg'])
    logger = setup_logger(config)

    logger.info("Starting Aquaponics System")

    # Set GPIO mode
    GPIO.setmode(GPIO.BOARD)
    logger.debug("Setting GPIO to BOARD_MODE")

    pumps = PumpController.PumpController(config, logger)
    lights = LightController.LightController(config, logger)
    temp = TemperatureController.TemperatureController(config, logger)

    logger.info("Initialized Modules: Lights, Pumps, Temperature")
    logger.debug("Initializing Loop")

    count = 0
    while 1:
        try:
            pumps.runModule()
            sleep(1)
            lights.runModule()
            sleep(1)
            temp.runModule()
            logger.info("Completed loop: {} Sleeping 60 seconds before next loop".format(count))
            count += 1
            sleep(60)
        except Exception as err:
            logger.error("encountered error while running: %s", err)

def setup_logger(config):
    logger = logging.getLogger("basiclogger")
    logger.setLevel(logging.INFO)

    path = config.get("logdir", '/home/pi/aquaponics-scu/logs')
    rotating_handler = RotatingFileHandler(path, maxBytes=20000000, backupCount=10)
    logger.addHandler(rotating_handler)

    return logger

if __name__ == '__main__':
    main()
