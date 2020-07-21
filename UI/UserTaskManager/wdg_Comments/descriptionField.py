from PySide2.QtWidgets import *
from PySide2.QtCore import Qt


class DescriptionFieldWidget():
    def __init__(self, parent):
        # super(DescriptionFieldWidget, self).__init__(parent)

        self.lay_grpBoxVertical = QVBoxLayout()

        self.groupBoxDescription = QGroupBox("Description")
        self.groupBoxDescription.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        self.description_lable = QLabel()
        self.description_lable.setMinimumSize(300, 200)
        self.description_lable.setWordWrap(True)
        self.description_lable.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.description_lable.setStyleSheet("QLabel {font: 15px;}")
        self.description_lable.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.lay_grpBoxVertical.addSpacerItem(QSpacerItem(0, 8))
        self.lay_grpBoxVertical.addWidget(self.description_lable)
        self.groupBoxDescription.setLayout(self.lay_grpBoxVertical)

    def setDescriptionText(self, text):
        self.description_lable.setText(text)
