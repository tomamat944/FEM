from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
                            QHBoxLayout, QHeaderView)

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from utils import Material, Boundry, Force


class LeftView(QWidget):
    loadMaterialSig  = pyqtSignal()
    drawBoundrySig = pyqtSignal()
    def __init__(self, material):
        super().__init__()
        self.initialize(material)
    
    def initialize(self, material):
        self.material = material
        layout = QVBoxLayout(self)
        material_view = MaterialView(material)

        layout.addWidget(material_view, alignment=Qt.AlignTop)        
        self.setLayout(layout)
        self.loadMaterialSig.connect(material_view.loadMaterials)
        material_view.drawBoundrySig.connect(self.drawBoundrySig)

    @pyqtSlot()
    def loadState(self):
        self.loadMaterialSig.emit()

        
class MaterialView(QWidget):
    loadMaterialSig = pyqtSignal()
    drawBoundrySig = pyqtSignal()
    def __init__(self, material):
        super().__init__()
        self.initialize(material)

    def initialize(self, material):
        self.materials = material
        layout = QVBoxLayout(self)

        label_material = QLabel('Material name')
        self.text_material = QLineEdit()
        label_young = QLabel('Young')
        self.text_young = QLineEdit()
        label_poisson = QLabel('Poisson')
        self.text_poisson = QLineEdit()
        bdry_view = BoundryView(material)
        force_view = ForceView(material)
        btn_confirm = QPushButton('Confirm')
        
        layout.addWidget(label_material)
        layout.addWidget(self.text_material)
        layout.addWidget(label_young)
        layout.addWidget(self.text_young)
        layout.addWidget(label_poisson)
        layout.addWidget(self.text_poisson)
        layout.addWidget(bdry_view)
        layout.addWidget(force_view)
        layout.addWidget(btn_confirm)
        self.setLayout(layout)

        btn_confirm.clicked.connect(lambda: self.confirm_params(material, self.text_material, self.text_young, self.text_poisson))
        self.loadMaterialSig.connect(bdry_view.loadMaterials)
        self.loadMaterialSig.connect(force_view.loadMaterials)


    def confirm_params(self, material, tm, ty, tp):
        material.name = tm.text()
        material.young = float(ty.text())
        material.poisson = float(tp.text())
        self.drawBoundrySig.emit()
    
    @pyqtSlot()
    def loadMaterials(self):
        self.text_material.setText(self.materials.name)
        self.text_young.setText(str(self.materials.young))
        self.text_poisson.setText(str(self.materials.poisson))

        self.loadMaterialSig.emit()

class BoundryView(QWidget):
    
    def __init__(self, material):
        super().__init__()
        self.initialize(material)

    def initialize(self, material):
        self.material = material
        self.layout = QVBoxLayout(self)
        self.content_layout = QHBoxLayout()
        self.x_view = RangeView('X')
        self.y_view = RangeView('Y')
        self.z_view = RangeView('Z')
        self.btn_add = QPushButton('Add')
        self.btn_remove = QPushButton('Remove')
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['id', self.x_view.getName(), self.y_view.getName(), self.z_view.getName()])

        self.layout.addLayout(self.content_layout)
        self.layout.addWidget(self.x_view)
        self.layout.addWidget(self.y_view)
        self.layout.addWidget(self.z_view)
        self.layout.addWidget(self.btn_add)
        self.layout.addWidget(self.btn_remove)
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)

        self.btn_add.clicked.connect(lambda: self.add_boundry())
        self.btn_remove.clicked.connect(lambda: self.remove_boundry())
    
    def setRowsInTable(self, elems):
        header = self.table.horizontalHeader()
        row = self.table.rowCount()
        self.table.insertRow(row)
        for i, e in enumerate(elems):
            self.table.setItem(row, i, QTableWidgetItem(str(e)))
            self.table.resizeColumnToContents(i)
            if i == len(elems)-1:
                header.setSectionResizeMode(i, QHeaderView.Stretch)
            
    @pyqtSlot()
    def loadMaterials(self):
        for b in self.material.boundries:
            self.setRowsInTable([b.id, b.x, b.y, b.z])


    def add_boundry(self):
        id = 0
        s = sorted([i.id for i in self.material.boundries])
        for i in s:
            if id==i:
                id+=1
            else:
                break
        self.setRowsInTable([id, self.x_view.getRange(), self.y_view.getRange(), self.z_view.getRange()])
        boundry = Boundry(id, self.x_view.getRange(), self.y_view.getRange(), self.z_view.getRange())
        self.material.boundries.append(boundry)

    def remove_boundry(self):
        idx = self.table.currentRow()
        if idx is None:
            return
        val = int(self.table.item(idx, 0).text())
        for j in self.material.boundries:
            if val == j.id:
                self.material.boundries.remove(j)
        self.table.removeRow(idx)

class ForceView(BoundryView):
    def __init__(self, material):
        super().__init__(material)
        
        label_value = QLabel('Value(X,Y,Z)')
        self.text_value_x = QLineEdit()
        self.text_value_y = QLineEdit()
        self.text_value_z = QLineEdit()
        self.content_layout.addWidget(label_value)
        self.content_layout.addWidget(self.text_value_x)
        self.content_layout.addWidget(self.text_value_y)
        self.content_layout.addWidget(self.text_value_z)
        col = self.table.columnCount()
        self.table.insertColumn(col)
        self.table.setHorizontalHeaderItem(col, QTableWidgetItem(label_value.text()))
        
    
    @pyqtSlot()
    def loadMaterials(self):
        for b in self.material.forces:
            self.setRowsInTable([b.id, b.x, b.y, b.z, b.value])


    def add_boundry(self):
        id = 0
        s = sorted([i.id for i in self.material.forces])
        for i in s:
            if id==i:
                id+=1
            else:
                break

        self.setRowsInTable([id, self.x_view.getRange(), self.y_view.getRange(), self.z_view.getRange(), 
                             (float(self.text_value_x.text()), float(self.text_value_y.text()), float(self.text_value_z.text()))])
        boundry = Force(id, self.x_view.getRange(), self.y_view.getRange(), self.z_view.getRange(), 
                        (float(self.text_value_x.text()), float(self.text_value_y.text()), float(self.text_value_z.text())))
        self.material.forces.append(boundry)

    def remove_boundry(self):
        idx = self.table.currentRow()
        if idx is None:
            return

        val = int(self.table.item(idx, 0).text())
        for j in self.material.forces:
            if val == j.id:
                self.material.forces.remove(j)
        self.table.removeRow(idx)
    

class RangeView(QWidget):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.initialize()

    def initialize(self):
        layout = QHBoxLayout(self)

        label_name = QLabel(self.name)
        self.text_from = QLineEdit()
        label_to = QLabel('to')
        self.text_to = QLineEdit()

        layout.addWidget(label_name)
        layout.addWidget(self.text_from)
        layout.addWidget(label_to)
        layout.addWidget(self.text_to)

        self.setLayout(layout)

    def getRange(self):
        return (float(self.text_from.text()), float(self.text_to.text()))
    
    def getName(self):
        return self.name
    
