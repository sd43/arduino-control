from comm.controller import WRITE, READ

class BaseOutputControl:
    def __init__(self, control, controller):
        self.controller = controller
        self.control = control
        self.lastValue = None
        self.onChangeCallbacks = []
        self.controller.addConnectionCallback(self._onControllerConnection)
        self.idSuffix = '_'+control.id

    def fixValue(self, value):
        if isinstance(value, str):
            if value.isnumeric():
                return int(value)
        return value

    def writeValue(self, value):
        value = self.fixValue(value)

        res = self.controller.command(WRITE, [ self.control.pin, value ], idSuffix=self.idSuffix)
        if not res.isSuccess():
            raise Exception('writing control value failed: {}'.format(res.errorMessage))

        if self.lastValue is None or self.lastValue != value:
            self.lastValue = value
            self._callOnChangeCallbacks(value)

        return res.isSuccess()

    def readValue(self):
        res = self.controller.command(READ, [ self.control.pin ], idSuffix=self.idSuffix)
        if not res.isSuccess():
            raise Exception('reading control value failed: {}'.format(res.errorMessage))

        value = self.fixValue(res.results[0])
        if self.lastValue is None or self.lastValue != value:
            self.lastValue = value
            self._callOnChangeCallbacks(value)

        return value

    def addOnChangeCallback(self, fn):
        self.onChangeCallbacks.append(fn)

    def removeOnChangeCallback(self, fn):
        self.onChangeCallbacks.remove(fn)

    def _callOnChangeCallbacks(self, value):
        for fn in self.onChangeCallbacks:
            fn(value)

    def _onControllerConnection(self, connected):
        if connected:
            self.readValue()

class AnalogOutputControl(BaseOutputControl):
    def __init__(self, control, controller):
        super(AnalogOutputControl, self).__init__(control, controller)

    def setValue(self, value):
        return self.writeValue(value)

    def getValue(self):
        return self.readValue()

class DigitalOutputControl(BaseOutputControl):
    def __init__(self, control, controller):
        super(DigitalOutputControl, self).__init__(control, controller)

    def setHigh(self):
        self.writeValue(1)

    def setLow(self):
        self.writeValue(0)

    def setOn(self, on):
        if on:
            self.setHigh()
        else:
            self.setLow()


