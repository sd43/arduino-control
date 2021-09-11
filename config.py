import json

class JsonConfig():
    def __init__(self, commandsFile='commands.json'):
        self.commands = []
        self.commandsFile = commandsFile

    def getCommands(self):
        with open(self.commandsFile, 'r') as f:
            data = f.read()

        if not self.commands:
            self.commands = json.loads(data)

        return self.commands

