from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator

class HeadingLabel(QLabel):
    def __init__(self, text, parent=None):
        super(HeadingLabel, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.setText('<b><u>'+text+'</b></u>')

class CommandBox(QWidget):
    def __init__(self, config, controller, parent=None):
        super(CommandBox, self).__init__(parent)

        self.config = config
        self.controller = controller

        self.createWidgets()

    def createWidgets(self):
        commands = self.config
        layout = QGridLayout()

        row = 0 
        layout.addWidget(HeadingLabel('Command'), row, 0)
        layout.addWidget(HeadingLabel('Inputs'), row, 1)
        layout.addWidget(HeadingLabel('Outputs'), row, 2)
        layout.addWidget(HeadingLabel('Send'), row, 3)
        layout.addWidget(HeadingLabel('Send'), row, 3)

        for command in commands:
            row += 1
            layout.addWidget(QLabel('<b>'+command['label']+'</b>'), row, 0)
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

            onSend = onSendCallback(command['command'], wInputs, wOutputs)

            if len(command['inputs']) > 0:
                wLayout = QHBoxLayout()
                for inp in command['inputs']:
                    wInput = QLineEdit(placeholderText=inp['name'])
                    wInput.returnPressed.connect(onSend)
                    wInput.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                    if inp['type'] == 'int':
                        wInput.setValidator(QIntValidator(0, 999999))

                    wInputs.append(wInput)
                    wLayout.addWidget(wInput, alignment=Qt.AlignLeft)
                layout.addLayout(wLayout, row, 1)

            if len(command['outputs']) > 0:
                wLayout = QHBoxLayout()
                for out in command['outputs']:
                    wOutput = QLineEdit(placeholderText=out['name'])
                    wOutput.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                    wOutput.setReadOnly(True)
                    wOutputs.append(wOutput)
                    wLayout.addWidget(wOutput, alignment=Qt.AlignLeft)
                layout.addLayout(wLayout, row, 2)

            wSend = QPushButton('->')
            wSend.clicked.connect(onSend)
            layout.addWidget(wSend, row, 3)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(layout)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)

    def showError(self, message):
        QMessageBox.critical(self, 'Error', message)

