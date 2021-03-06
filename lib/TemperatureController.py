
import os
import glob
import time
import RPi.GPIO as GPIO


class TemperatureController(object):
    def __init__(self, config, logger):
        # TODO: there has to be another way this is horrible
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')

        self._initialize(config, logger)

    def _initialize(self, config, logger):
        self.logger = logger
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
        GPIO.output(self.heatOutPin, GPIO.LOW)
        GPIO.setup(self.coolOutPin, GPIO.OUT)
        GPIO.output(self.coolOutPin, GPIO.LOW)

    def runModule(self):
        waterTemp, airTemp = self.getTemp()
        self.logger.info("water temp: {} air temp: {}".format(waterTemp, airTemp))

        water_error = self.setPoint - waterTemp
        air_error = self.setPoint - airTemp

# Maybe Someday...
#        if self.runPID:
#            error = self.getPIDValue(error)

        self.logger.debug("water-error: %s air-error: %s error-margin: %s", water_error, air_error, self.errorMargin)

        if (abs(water_error) > self.errorMargin and water_error > 0) or (abs(water_error) < self.errorMargin and abs(air_error) > self.errorMargin and air_error > 0):
            self.logger.debug("turning heat ON")
            GPIO.output(self.heatOutPin, GPIO.HIGH)
        else:
            self.logger.debug("turning heat OFF")
            GPIO.output(self.heatOutPin, GPIO.LOW)

        if (abs(air_error) > self.errorMargin and air_error < 0) or (abs(air_error) < self.errorMargin and abs(water_error) > self.errorMargin and water_error < 0):
            self.logger.debug("turning cooling ON")
            GPIO.output(self.coolOutPin, GPIO.HIGH)
        else:
            self.logger.debug("turning cooling OFF")
            GPIO.output(self.coolOutPin, GPIO.LOW)
            
    def getTemp(self, device_list=None):
        total_temp_water = 0
        total_temp_air = 0
        count_water = 0
        count_air = 0

        temp_devices = device_list or glob.glob(self.basedir + '28*')
        for device in temp_devices:
            self.logger.debug("getting temp from device %s", device)

            lines = self.getRawLines(device + "/w1_slave")
            while lines[0].find('YES') == -1:
                self.logger.debug('FAILED getting good data from %s trying again in .2 seconds', device)
                time.sleep(0.2)
                lines = self.getRawLines(device)

            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos + 2:]
                temp_c = float(temp_string) / 1000.0
                temp_f = temp_c * 9.0 / 5.0 + 32.0

                # FIXME horrible horrible hack
                if "28-000008a3d594" in device: 
                    self.logger.debug("temp %s from device %s was added to air total", temp_f, device)
                    total_temp_air += temp_f
                    count_air += 1
                else:
                    self.logger.debug("temp %s from device %s was added to water total", temp_f, device)
                    total_temp_water += temp_f
                    count_water += 1
            else:
                self.logger.debug("Couldn't get good temp from device %s", device)

        if count_water < 1:
            count_water = 1
        if count_air < 1:
            count_air = 1

        return total_temp_water / count_water, total_temp_air / count_air

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
