import json

from comm.control import STATE_STORE_LOCAL, STATE_STORE_REMOTE

class ControlState():
    def __init__(self, controller, stateFile):
        self.controls = []
        self.controller = controller
        self.controlStates = {}
        self.stateFile = stateFile
        self.controller.addConnectionCallback(self._onConnectCallback)

    def _onConnectCallback(self, connected):
        if connected:
            self.applyControlStates()

    def _onChangeCallback(self, control, value):
        self.controlStates[control.control.id] = value
        self.writeStatesToFile()

    def readStatesFromFile(self):
        with open(self.stateFile, "r") as f:
            self.controlStates = json.loads(f.read())

    def writeStatesToFile(self):
        with open(self.stateFile, "w") as f:
            obj = json.dumps(self.controlStates)
            f.write(obj)

    def addControl(self, control):
        self.controls.append(control)
        if control.lastValue is not None:
            self.controlStates[control.control.id] = control.lastValue
        else:
            self.controlStates[control.control.id] = control.control.defaultValue
        control.addOnChangeCallback(lambda v: self._onChangeCallback(control, v))

    def getControls(self):
        return self.controls

    def getControlStates(self):
        return self.controlStates

    def applyControlStates(self):
        for control in self.controls:
            if control.stateStore == STATE_STORE_LOCAL:
                if control.control.id not in self.controlStates:
                    self.controlStates[control.control.id] = control.control.defaultValue
                control.writeValue(self.controlStates[control.control.id])

