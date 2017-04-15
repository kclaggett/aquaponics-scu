
import os
import glob
import time
import RPi.GPIO as GPIO


class TemperatureController(object):
    def __init__(self, config):
        # TODO: there has to be another way this is horrible
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')

        self._initialize(config)

    def _initialize(self, config):
        self.setPoint = config.getInt('temp.setpoint', 70)
        self.errorMargin = config.getInt('temp.error.margin', 2)
        self.heatOutPin = config.getInt('temp.heat.output_board_pin')
        self.coolOutPin = config.getInt('temp.cool.output_board_pin')
        self.basedir = config.get('temp.sensor.basedir', '/sys/bus/w1/devices/')
        self.runPID = config.getBool('temp.runpid', False)

        self.errorSum = 0
        self.maxErrorBound = config.getInt('temp.max.integrator.value', 20)
        self.minErrorBound = config.getInt('temp.min.integrator.value', -20)

        if GPIO.getmode() is None:
            raise Exception("GPIO mode not initialized")

        try:
            GPIO.cleanup(self.heatOutPin)
        except:
            pass  # need to do for reinit, so don't bother with exceptions

        try:
            GPIO.cleanup(self.coolOutPin)
        except:
            pass  # need to do for reinit, so don't bother with exceptions

        GPIO.setup(self.heatOutPin, GPIO.OUT)
        GPIO.setup(self.coolOutPin, GPIO.OUT)

    def runModule(self):
        currTemp = self.getTemp()

        error = self.setPoint - currTemp

        if self.runPID:
            error = self.getPIDValue(error)

        if abs(error) > self.errorMargin and error < 0:
            GPIO.output(self.heatOutPin, GPIO.HIGH)
            GPIO.output(self.coolOutPin, GPIO.LOW)
        elif abs(error) > self.errorMargin and error > 0:
            GPIO.output(self.heatOutPin, GPIO.LOW)
            GPIO.output(self.coolOutPin, GPIO.HIGH)

    def getTemp(self, device_list=None):
        total_temp = 0
        count = 0
        temp_devices = device_list or glob.glob(self.basedir + '28*')
        for device in temp_devices:

            lines = self.getRawLines(device + "/w1_slave")
            while lines[0].find('YES') == -1:
                time.sleep(0.2)
                lines = self.getRawLines(device)

            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos + 2:]
                temp_c = float(temp_string) / 1000.0
                temp_f = temp_c * 9.0 / 5.0 + 32.0
                total_temp += temp_f
                count += 1

        return total_temp / count

    def getRawLines(self, filename):
        f = open(filename, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def getPIDValue(self, error):
        kp = 1
        ki = .2
        # Just PI for now
        # kd = .1

        self.errorSum = self.errorSum + error

        if self.errorSum > self.maxErrorBound:
            self.errorSum = self.maxErrorBound
        elif self.errorSum < self.minErrorBound:
            self.errorSum = self.minErrorBound

        return kp * error + ki * self.errorSum
