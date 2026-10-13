import pyvista as pv
from utils import Region
import numpy as np
from fem_sfe import FEM
from time import time
import tetgen

class ModelAccess:
    def __init__(self, material):
        self.material = material
        self.mesh = None
        self.file = None
        self.boundry = None
        self.boundry_idcs = None
        self.forces = []
        self.forces_idcs = []
        self.temp_path = 'App_sfe_qt/temp/elem.vtk'

    def initialize(self, file):
        self.file = file
        self.mesh = pv.read(file)

        return self.mesh
        
    def setBoundry(self):
        points = self.mesh.points
        flags = np.zeros(points.shape[0], dtype=np.bool)
        for r in self.material.boundries:
            temp = self.compute_points_inside(r)
            flags = np.logical_or(flags, temp)
        self.boundry = points[flags]
        self.boundry_idcs = np.where(flags)[0]

        return self.boundry

    def setForces(self):
        points = self.mesh.points
        for r in self.material.forces:
            temp = self.compute_points_inside(r)
            self.forces.append(Region(points[temp], r.value))
            self.forces_idcs.append(Region(np.where(temp)[0], r.value))

        return self.forces

    def compute_points_inside(self, region):
        points = self.mesh.points
        flags = np.zeros(points.shape[0], dtype=np.bool)
        for e,p in enumerate(range(points.shape[0])):
            if region.x[0]<=points[p][0]<=region.x[1] and \
                region.y[0]<=points[p][1]<=region.y[1] and \
                region.z[0]<=points[p][2]<=region.z[1]:
                flags[e]=True

        return flags
    
    def compute_fem(self):
        start = time()
        tet = tetgen.TetGen(self.mesh)
        tet.tetrahedralize()
        tetra = tet.grid
        end = time()
        tetra.save(self.temp_path)
        fem = FEM(self.material.poisson, self.material.young, self.forces_idcs, self.boundry_idcs)
        fem.run()
        obj = pv.read(self.temp_path)
        print(f'Tetgen: tetrahedralization: {end-start:.2f} [s]')

        return obj
        
