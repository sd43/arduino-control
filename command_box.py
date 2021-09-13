from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator

class CommandBox(QWidget):
    def __init__(self, config, controller, parent=None):
        super(CommandBox, self).__init__(parent)

        self.config = config
        self.controller = controller

        self.createWidgets()

    def createWidgets(self):
        items = self.config
        layout = QGridLayout()
        row = 0 

        layout.addWidget(QLabel('<i>Command</i>'), row, 0)
        layout.addWidget(QLabel('<i>Inputs</i>'), row, 1)
        layout.addWidget(QLabel('<i>Outputs</i>'), row, 2)
        layout.addWidget(QLabel('<i>Send</i>'), row, 3)

        for item in items:
            row += 1
            layout.addWidget(QLabel('<b>'+item['label']+'</b>'), row, 0)
            wInputs = []
            wOutputs = []

            def onSendCallback(command, wInputs, wOutputs):
                def fn():
                    try:
                        args = [ w.text() for w in wInputs ]
                        output = self.controller.command(command, args)
                        for (wOutput, output) in zip(wOutputs, output.results):
                            wOutput.setText(output)

                    except Exception as e:
                        self.showError('Failed to send command: ' + str(e))
                return fn

            onSend = onSendCallback(item['command'], wInputs, wOutputs)

            if len(item['inputs']) > 0:
                wLayout = QHBoxLayout()
                for inp in item['inputs']:
                    wInput = QLineEdit(placeholderText=inp['name'])
                    wInput.returnPressed.connect(onSend)
                    if inp['type'] == 'int':
                        wInput.setValidator(QIntValidator(0, 999999))

                    wInputs.append(wInput)
                    wLayout.addWidget(wInput)
                layout.addLayout(wLayout, row, 1)

            if len(item['outputs']) > 0:
                wLayout = QHBoxLayout()
                for out in item['outputs']:
                    wOutput = QLineEdit(placeholderText=out['name'])
                    wOutput.setReadOnly(True)
                    wOutputs.append(wOutput)
                    wLayout.addWidget(wOutput)
                layout.addLayout(wLayout, row, 2)

            wSend = QPushButton('->')
            wSend.clicked.connect(onSend)
            layout.addWidget(wSend, row, 3)

            self.setLayout(layout)

