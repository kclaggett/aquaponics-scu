import RPi.GPIO as GPIO
import datetime


class LightController(object):
    def __init__(self, config):
        self._initialize(config)

    def _initialize(self, config):
        self.onTime = config.getInt('lights.ontime', 0730)
        self.offTime = config.getInt('lights.offtime', 1930)
        self.outPin = config.get('lights.output_board_pin')

        if GPIO.getmode() is None:
            raise Exception("GPIO mode not initialized")

        try:
            GPIO.cleanup(self.outPin)
        except:
            pass  # need to do for reinit, so don't bother with exceptions

        GPIO.setup(self.outPin, GPIO.OUT)
        self.lastState = 'off'

    def runModule(self):
        currTime = datetime.datetime.now()

        testTime = currTime.hour * 100 + currTime.minute

        # FIXME: there is a shitty inherent assumption that lights should be on during the day
        if self.lastState == 'off' and testTime > self.onTime and testTime < self.offTime:
            GPIO.output(self.outPin, GPIO.HIGH)
            self.lastState = 'on'
        elif self.lastState == 'on' and (testTime > self.offTime or testTime < self.onTime):
            GPIO.output(self.outPin, GPIO.LOW)
            self.lastState = 'off'