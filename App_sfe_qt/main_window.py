from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QMenuBar, QAction, QFileDialog
from left_view import LeftView
from right_view import RightView
from center_view import CenterView
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from utils import Material
import pickle
from pathlib import Path

class MainWindow(QMainWindow):
    sendFile = pyqtSignal(str)
    loadFileSig = pyqtSignal()
    drawBoundrySig = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.initialize()

    def initialize(self):
        self.setWindowTitle('FEM')
        self.showMaximized()       
        self.material = Material()
        menubar = QMenuBar()
        new_file = menubar.addMenu('File')
        new_action = QAction('New', self)
        load_action = QAction('Load', self)
        save_action = QAction('Save', self)       

        self.setMenuBar(menubar)

        new_action.triggered.connect(lambda: self.openNewFile())
        save_action.triggered.connect(lambda: self.saveFile())
        load_action.triggered.connect(lambda: self.loadFile())

        new_file.addAction(new_action)
        new_file.addAction(load_action)
        new_file.addAction(save_action)

    def loadFile(self):
        dial, _ = QFileDialog.getOpenFileName(directory='./App_sfe_qt/saved/', filter='*.pkl')
        if dial:
            with open(dial, 'rb') as f:
                self.material = pickle.load(f)
        wrapper = WrapperView(self.material)
        self.setCentralWidget(wrapper)
        self.drawBoundrySig.connect(wrapper.drawBoundrySig)
        self.sendFile.connect(wrapper.sendFile)
        self.loadFileSig.connect(wrapper.loadFileSig)
        self.sendFile.emit(self.material.path)
        self.loadFileSig.emit()
        self.drawBoundrySig.emit()

    def saveFile(self):
        folder = Path('./App_sfe_qt/saved')
        path = folder / f'{self.material.name}.pkl'
        with open(path, 'wb') as f:
            pickle.dump(self.material, f)
        print('Saved')

    def openNewFile(self):
        wrapper = WrapperView(self.material)
        self.setCentralWidget(wrapper)
        self.sendFile.connect(wrapper.sendFile)
        dial, _ = QFileDialog.getOpenFileName(directory='./models/', filter='*.stl')
        if dial:
            self.material.path = dial
            self.sendFile.emit(dial)
        

class WrapperView(QWidget):
    sendFile = pyqtSignal(str)
    loadFileSig = pyqtSignal()
    drawBoundrySig = pyqtSignal()
    def __init__(self, material):
        super().__init__()
        self.initialize(material)

    def initialize(self, material):
        layout = QHBoxLayout(self)
        left_view = LeftView(material)
        center_view = CenterView(material)
        right_view = RightView()
        layout.addWidget(left_view, 2)
        layout.addWidget(center_view, 8)
        layout.addWidget(right_view, 2)

        self.setLayout(layout)
        self.loadFileSig.connect(left_view.loadState)
        self.sendFile.connect(center_view.readFromFileSlot)
        left_view.drawBoundrySig.connect(center_view.drawBoundryForces)
        self.drawBoundrySig.connect(center_view.drawBoundryForces)
        right_view.computeFEMSig.connect(center_view.computeFEMSlot)
        center_view.sendDisplSig.connect(right_view.sendDisplSig)
        right_view.sendCheckSig.connect(center_view.manageMesh)