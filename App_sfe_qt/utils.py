
class Material:
    def __init__(self):
        self.name = ''
        self.young = ''
        self.poisson = ''
        self.path = ''
        self.boundries = []
        self.forces = []


class Boundry:
    def __init__(self, id, x,y,z):
        self.id = id
        self.x = x
        self.y = y
        self.z = z

class Force:
    def __init__(self, id, x,y,z, value):
        self.id = id
        self.x = x
        self.y = y
        self.z = z
        self.value = value

class Region:
    def __init__(self, arr, val):
        self.arr = arr
        self.val = val

