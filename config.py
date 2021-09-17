import json

class ControlConfig():
    """ControlConfig represents the configuration for a particular control"""
    def __init__(self, config):
        self.config = config

        # mandatory configs
        self.id = self.get('id', type_='str', required=True)
        self.name = self.get('name', type_='str', required=True)
        self.controlType = self.get('type', type_='str', required=True)

        # other well known configs
        self.pin = self.get('pin')
        self.min = self.get('min')
        self.max = self.get('max')
        self.on = self.get('on')
        self.off = self.get('off')
        self.refreshRate = self.get('refreshRate')

    def get(self, key, type_=None, required=False):
        if key not in self.config:
            if required:
                raise Exception('{} is not present in config'.format(key))
            else:
                return None

        if type_:
            if type(self.config[key]).__name__ != type_:
                raise Exception('{} should be of type {} (was {})'.format(key, type_, type(self.config[key])))

        return self.config[key]

class Config():
    def __init__(self):
        self.meta = {}
        self.controls = []
        self.commands = []

class JsonConfig():
    def __init__(self, configFile):
        self.configFile = configFile

        with open(self.configFile, 'r') as f:
            data = f.read()
        
        config = json.loads(data)

        self.config = Config()
        self.config.meta = config['meta']
        self.config.controls = [ ControlConfig(c) for c in config['controls'] ]
        self.config.commands = config['commands']

        seenIds = set()
        for c in self.config.controls:
            if c.id in seenIds:
                raise Exception("Duplicate control ID: {}".format(c.id))
            seenIds.add(c.id)

    def getCommands(self):
        return self.config.commands

    def getControls(self):
        return self.config.controls

