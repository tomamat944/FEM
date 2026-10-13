from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt

class RightView(QWidget):
    sendCheckSig = pyqtSignal(dict)
    sendDisplSig = pyqtSignal(list)
    computeFEMSig = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.initialize()

    def initialize(self):
        self.layout = QVBoxLayout(self)

        btn = QPushButton('Compute FEM')
        self.layout.addWidget(btn, alignment=Qt.AlignTop)
        self.setLayout(self.layout)
        
        btn.clicked.connect(lambda: self.btn_compute())

    def btn_compute(self):
        self.computeFEMSig.emit()
        side = SideView()
        self.layout.addWidget(side)
        self.sendDisplSig.connect(side.addTableSlot)
        side.sendCheckSig.connect(self.sendCheckSig)

class SideView(QWidget):
    sendCheckSig = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.initialize()

    def initialize(self):
        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['id', 'X', 'Y', 'Z', 'stress'])
        self.check_force_boundry = QCheckBox('Hide forces/boundry')
        self.check_original = QCheckBox('Hide original mesh')
        self.check_computed = QCheckBox('Hide computed mesh')
        self.check_force_boundry.setChecked(True)
        self.check_original.setChecked(True)
        self.check_computed.setChecked(True)

        layout.addWidget(self.table)
        layout.addWidget(self.check_force_boundry)
        layout.addWidget(self.check_original)
        layout.addWidget(self.check_computed)

        self.setLayout(layout)
        self.check_force_boundry.clicked.connect(lambda: self.changeState({'forces': self.check_force_boundry.isChecked()}))
        self.check_original.clicked.connect(lambda: self.changeState({'original': self.check_original.isChecked()}))
        self.check_computed.clicked.connect(lambda: self.changeState({'computed': self.check_computed.isChecked()}))

    def insertElement(self, elem):
        header = self.table.horizontalHeader()
        row = self.table.rowCount()
        self.table.insertRow(row)
        elem = [str(elem[0])] + [f'{e:.4f}' for e in elem[1:]]
        for i, e in enumerate(elem):
            item = QTableWidgetItem(e)
            self.table.setItem(row, i, item)
            self.table.resizeColumnToContents(i)
            if i == len(elem)-1:
                header.setSectionResizeMode(i, QHeaderView.Stretch)

    @pyqtSlot(list)
    def addTableSlot(self, elem):
        self.insertElement(elem)

    def changeState(self, val):
        self.sendCheckSig.emit(val)