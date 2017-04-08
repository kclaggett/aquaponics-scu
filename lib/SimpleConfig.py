
class SimpleConfig(object):

    def __init__(self, file_list):
        self._generate(file_list)

    def _generate(self, file_list):
        self.data = {}

        for fname in file_list:
            try: 
                f = open(fname, 'r')
                for line in f:
                    line = line.strip()
                    if not '=' in line:
                        continue

                    pieces = line.split('=', 2)
                    key = pieces[0].strip()
                    value = pieces[1].strip()
                    if len(key) < 1:
                        continue

                    self.data[key] = value or ''
            except Exception:
                pass

    def get(self, key, default=None):
        return self.data.get(key, default)

    def getInt(self, key, default=None):
        value = self.data.get(key, default)
        try:
            return int(value)
        except ValueError:
            return default

    def getFloat(self, key, default=None):
        value = self.data.get(key, default)
        try:
            return float(value)
        except ValueError:
            return default

