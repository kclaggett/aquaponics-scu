import RPi.GPIO as GPIO
import time


class PumpController(object):

    def __init__(self, config):
        self._initialize(config)
    
    def _initialize(self, config):
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
        
        if self.lastState == 'on' and currTime - self.lastChange > self.onCycle:
            GPIO.output(self.outPin, GPIO.LOW)
            self.lastState = 'off'
            self.lastChange = currTime
        elif self.lastState == 'off' and currTime - self.lastChange > self.offCycle:
            GPIO.output(self.outPin, GPIO.HIGH)
            self.lastState = 'off'
            self.lastChange = currTime
