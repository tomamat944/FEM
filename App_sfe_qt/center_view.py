from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from pyvistaqt import QtInteractor
from triangulation import ModelAccess
import pyvista as pv

class CenterView(QWidget):
    sendDisplSig = pyqtSignal(list)
    def __init__(self, material):
        super().__init__()
        self.initialize(material)

    def initialize(self, material):
        layout = QVBoxLayout(self)
        self.model_access = ModelAccess(material)
        self.material = material
        self.interactor = QtInteractor(self)
        self.interactor.show_grid()
        self.interactor.show_axes()
        self.boundry = []
        self.forces = []
        layout.addWidget(self.interactor)
        self.setLayout(layout)
           
    @pyqtSlot(str)
    def readFromFileSlot(self, file):
        model = self.model_access.initialize(file)
        self.main_acctor = self.interactor.add_mesh(model, style='wireframe')

    @pyqtSlot()
    def drawBoundryForces(self):
        self.refreshBoundryForces()                                                                 
        bdry_points = self.model_access.setBoundry()
        cloud = pv.PolyData(bdry_points)
        cube = pv.Cube(x_length=0.02, y_length=0.02, z_length=0.02)
        glyphs = cloud.glyph(geom=cube, scale=False, orient=False)
        actor = self.interactor.add_mesh(glyphs, color='black')
        self.boundry.append(actor)

        force_points = self.model_access.setForces()
        for reg in force_points:
            cloud = pv.PolyData(reg.arr)
            arrow = pv.Arrow(direction=reg.val, scale=0.1)
            glyphs = cloud.glyph(geom=arrow, scale=False,orient=False)
            actor = self.interactor.add_mesh(glyphs, color='black')
            self.forces.append(actor)
        

    @pyqtSlot()
    def computeFEMSlot(self):
        obj = self.model_access.compute_fem()
        warp = obj.warp_by_vector('u')
        self.warpped = self.interactor.add_mesh(warp, scalars='cauchy_stress', cmap='coolwarm')
        self.interactor.enable_point_picking(callback=lambda p: self.pointPicking(p, obj))

    def pointPicking(self, point, obj):
        id = self.interactor.iren.picker.GetPointId()
        u = obj['u'][id]
        stress = obj['cauchy_stress'][id]
        self.sendDisplSig.emit([id, u[0], u[1], u[2], stress[0]])

    @pyqtSlot(dict)
    def manageMesh(self, d):
        if 'forces' in d:
            for f in self.forces:
                f.SetVisibility(d['forces'])
            for b in self.boundry:
                b.SetVisibility(d['forces'])
        elif 'original' in d:
            self.main_acctor.SetVisibility(d['original'])
        elif 'computed' in d:
            self.warpped.SetVisibility(d['computed'])

    def refreshBoundryForces(self):
        for b in self.boundry:
            self.interactor.remove_actor(b)
        for f in self.forces:
            self.interactor.remove_actor(f)
        self.boundry=[]
        self.forces=[]