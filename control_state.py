class ControlState():
    def __init__(self, config, controller):
        self.config = dict()
        for c in config:
            self.config[c.id] = c
        self.state = { c.id: None for c in self.config }
        self.controller = controller

    def readState(self, controlId):
        if controlId not in self.config:
            raise Exception("Unknown control ID: {}".format(controlId))
        c = self.config[controlId]
        o = self.controller.command('read', c.id)


