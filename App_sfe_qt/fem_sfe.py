

import numpy as np
from sfepy.base.base import IndexedStruct
from sfepy.discrete import (FieldVariable, Material, Integral,
                            Equation, Equations, Problem)
from sfepy.discrete.fem import Mesh, FEDomain, Field
from sfepy.terms import Term
from sfepy.discrete.conditions import Conditions, EssentialBC
from sfepy.mechanics.matcoefs import stiffness_from_youngpoisson
from sfepy.solvers.nls import Newton
from sfepy.solvers.ls import ScipyDirect
from sfepy.solvers.ls import ScipyIterative
from sfepy.base.base import Struct


# start = time.time()
# cube = pv.Cube().triangulate().subdivide(4)
# tet = cube.delaunay_3d()
# tet.clear_data()
# tet.save('App_sfe_qt/cube.vtk')

# mesh = Mesh.from_file('App_sfe_qt/cube.vtk')
# young = 200e9
# poisson = 0.3
# domain = FEDomain('domain', mesh)
# omega = domain.create_region('Omega', 'all')
# left = domain.create_region('Left', 'vertices in (x > 0.48)', 'facet')
# right = domain.create_region('Right', 'vertices in (x < -0.48)', 'facet')
# field = Field.from_args('fu', np.float64, 'vector', omega)
# u = FieldVariable('u', 'unknown', field)
# v = FieldVariable('v', 'test', field, primary_var_name='u')
# D = stiffness_from_youngpoisson(3, young, poisson)
# asphalt = Material('Asphalt', D=D)
# load = Material('Load', values={'.val': [0.0, 0.0, -1e5]})
# integral = Integral('i', order=2)
# integral0 = Integral('i', order=0)
# t1 = Term.new('dw_lin_elastic(Asphalt.D, v, u)', integral, omega, Asphalt=asphalt, v=v, u=u)
# t2 = Term.new('dw_point_load(Load.val, v)', integral0, left, Load=load, v=v)
# eq = Equation('balance', t1-t2)
# eqs = Equations([eq])
# fix = EssentialBC('fix', right, {'u.all': 0.0})
# ls = ScipyDirect({})
# nls_status = IndexedStruct()
# nls = Newton({}, lin_solver=ls, status=nls_status)
# pb = Problem('elasticity', equations=eqs)
# pb.set_bcs(ebcs=Conditions([fix]))
# pb.set_solver(nls)
# variables = pb.solve()
# out = variables.create_output()
# out = stress_strain(out, pb, variables, extend=True)
# pb.save_state('App_sfe_qt/elasticity.vtk', out=out)

# print(time.time()-start)
# obj =  pv.read('App_sfe_qt/elasticity.vtk')
# warped = obj.warp_by_vector('u', factor=50)
# plotter = pv.Plotter()
# plotter.add_mesh(warped, scalars='cauchy_stress')
# plotter.show_axes()
# plotter.show_grid()
# plotter.show()

class FEM:
    def __init__(self, poisson, young, forces, boundry):
        self.forces = forces
        self.boundry = boundry
        self.poisson = poisson
        self.young = young
        self.temp_path = 'App_sfe_qt/temp/elem.vtk'

    def run(self):
        mesh = Mesh.from_file(self.temp_path)
        domain = FEDomain('domain', mesh)
        omega = domain.create_region('Omega', 'all')
        load_regions = self.set_loads_regions('Force', domain, self.forces)
        boundry_regions = self.set_boundry_regions('Boundry', domain, self.boundry)

        field = Field.from_args('fu', np.float64, 'vector', omega)
        u = FieldVariable('u', 'unknown', field)
        v = FieldVariable('v', 'test', field, primary_var_name='u')
        D = stiffness_from_youngpoisson(3, self.young, self.poisson)
        Objmaterial = Material('Objmaterial', D=D)
        integral = Integral('i', order=3)
        materials = {}
        obj_t = Term.new('dw_lin_elastic(Objmaterial.D, v, u)', 
                         integral, omega, Objmaterial=Objmaterial, v=v, u=u)
        terms = self.set_terms_loads(materials, load_regions, integral, v)
        eq = Equation('balance', obj_t - sum(terms[1:], terms[0]))
        eqs = Equations([eq])
        fixed = EssentialBC('fixed', boundry_regions, {'u.all':0.0})
        # ls = ScipyDirect({})
        ls = ScipyIterative(Struct(name='cg', kind = 'ls.scipy_iterative', method='cg',
                                   i_max=1000, eps_a=1e-8, eps_r=1e-8))
        nls_status = IndexedStruct()
        nls = Newton({'i_max':1, 'eps_a':1e-8, 'lin_red':1e-2}, lin_solver=ls, status=nls_status)
        pb = Problem('elasticity', equations=eqs)
        pb.set_bcs(ebcs=Conditions([fixed]))
        pb.set_solver(nls)
        variables = pb.solve()
        out = variables.create_output()
        stress = pb.evaluate('ev_cauchy_stress.3.Omega(Objmaterial.D, u)', Objmaterial=Objmaterial, mode='el_avg')
        out['cauchy_stress'] = Struct(name='output_data', mode='cell', data=stress, dofs=None)

        pb.save_state(self.temp_path, out=out)
        


    def set_boundry_regions(self, name, domain, boundry):
        reg = domain.create_region(name, 
                                   'vertices by fn',
                                   'vertex',
                                   functions = {'fn': lambda coors, domain=None: boundry})
        return reg

    def set_loads_regions(self, name, domain, forces):
        regs = {}
        for e, f in enumerate(forces):
            regs[f'{name}{e}'] = (domain.create_region(f'{name}{e}',
                                       'vertices by fn',
                                       'vertex',
                                        functions = {'fn':lambda coors, domain=None: f.arr})
                                        , f.val)
            
        return regs

    def set_terms_loads(self, materials, load_regions, integral, v):
        terms = []
        for n, rv in load_regions.items():
            s=f'l_{n}'
            mat = Material(s, values={'.val':rv[1]})
            materials[s]=mat
            term = Term.new(f'dw_point_load({s}.val, v)',
                            integral,
                            rv[0],
                            **{s: mat},
                            v=v)
            terms.append(term)

        return terms