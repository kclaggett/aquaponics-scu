import RPi.GPIO as GPIO
import time


class PumpController(object):

    def __init__(self, config, logger):
        self._initialize(config, logger)
    
    def _initialize(self, config, logger):
        self.logger = logger
        self.onCycle = config.getInt('pump.on_interval.seconds', 2700)
        self.offCycle = config.getInt('pump.off_interval.seconds', 900)
        self.outPin = config.getInt('pump.output_board_pin')

        self.totalCycle = self.onCycle + self.offCycle;

        if GPIO.getmode() is None:
            raise Exception("GPIO mode not initialized")
        try:
            GPIO.cleanup(self.outPin)
        except:
            pass  # need to do for reinit, so don't bother with exceptions

        GPIO.setup(self.outPin, GPIO.OUT)
        GPIO.output(self.outPin, GPIO.LOW)
                 
        self.lastChange = 0
        self.lastState = 'off'

    def runModule(self):
        currTime = time.time()
        
        self.logger.debug("Last Pump state: %s last change time: %s current time: %s on-cycle: %s, off-cycle: %s", self.lastState, self.lastChange, currTime, self.onCycle, self.offCycle)

        if self.lastState == 'on' and currTime - self.lastChange > self.onCycle:
            GPIO.output(self.outPin, GPIO.LOW)
            self.logger.debug("Turning Pumps OFF")
            self.lastState = 'off'
            self.lastChange = currTime
        elif self.lastState == 'off' and currTime - self.lastChange > self.offCycle:
            GPIO.output(self.outPin, GPIO.HIGH)
            self.logger.debug("Turning Pumps ON")
            self.lastState = 'on'
            self.lastChange = currTime
