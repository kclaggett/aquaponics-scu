import RPi.GPIO as GPIO
import datetime


class LightController(object):
    def __init__(self, config, logger):
        self._initialize(config, logger)

    def _initialize(self, config, logger):
        self.logger = logger
        self.onTime = config.getInt('lights.ontime', 0730)
        self.offTime = config.getInt('lights.offtime', 1930)
        self.outPin = config.getInt('lights.output_board_pin')

        if GPIO.getmode() is None:
            raise Exception("GPIO mode not initialized")

        try:
            GPIO.cleanup(self.outPin)
        except:
            pass  # need to do for reinit, so don't bother with exceptions

        GPIO.setup(self.outPin, GPIO.OUT)
        GPIO.output(self.outPin, GPIO.LOW)
        self.lastState = 'off'

    def runModule(self):
        currTime = datetime.datetime.now()
        testTime = currTime.hour * 100 + currTime.minute

        self.logger.debug("last state of lights: %s on-time: %s off-time: %s current-time: %s", self.lastState, self.onTime, self.offTime, testTime)

        # FIXME: there is a shitty inherent assumption that lights should be on during the day
        if self.lastState == 'off' and testTime > self.onTime and testTime < self.offTime:
            GPIO.output(self.outPin, GPIO.HIGH)
            self.logger.debug("Turning Lights ON")
            self.lastState = 'on'
        elif self.lastState == 'on' and (testTime > self.offTime or testTime < self.onTime):
            GPIO.output(self.outPin, GPIO.LOW)
            self.logger.debug("Turning Lights OFF")
            self.lastState = 'off'

