from controller  import WRITE_PIN, READ_PIN

class BaseOutputControl():
    def __init__(self, control, controller):
        self.controller = controller
        self.control = control

    def writeValue(self, value):
        res = self.controller.command(WRITE_PIN, [ self.control.pin, value ])
        if not res.isSuccess():
            raise Exception('writing control value failed: {}'.format(res.errorMessage))

        return res.isSuccess()

    def readValue(self):
        res = self.controller.command(READ_PIN, [ self.control.pin ])
        if not res.isSuccess():
            raise Exception('reading control value failed: {}'.format(res.errorMessage))

        return res.results[0]

class AnalogOutputControl(BaseOutputControl):
    def __init__(self, control, controller):
        super(AnalogOutputControl, self).__init__(control, controller)

    def setValue(self, value):
        return self.writeValue(self, value)

    def getValue(self):
        return self.readValue()

class DigitalOutputControl(BaseOutputControl):
    def __init__(self, control, controller):
        super(AnalogOutputControl, self).__init__(control, controller)

    def setHigh(self):
        self.writeValue(1)

    def setLow(self):
        self.writeValue(0)


