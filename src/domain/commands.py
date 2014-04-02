
class Command(object):
    pass

class LateralDraw(Command):
    def __init__(self,x,y,speed):
        self.x = x
        self.y = y
        self.posisition=[x,y]
        self.speed = speed

    def __str__(self):
     return "DRAW[X:%f,Y:%f,Speed:%f]" % (self.x,self.y,self.speed)

class LateralMove(Command):
    def __init__(self,x,y,speed):
        self.x = x
        self.y = y
        self.posisition=[x,y]
        self.speed = speed

    def __str__(self):
     return "MOVE[X:%f,Y:%f,Speed:%f]" % (self.x,self.y,self.speed)

class VerticalMove(Command):
    def __init__(self,z,speed):
        self.z = z
        self.speed = speed
    def __str__(self):
        return "MOVEVERTICAL[Z:%f,Speed:%f]" % (self.z,self.speed)

class Layer(object):
    def __init__(self, z_posisition , commands = None):
        if commands:
            self.commands = commands
        else:
            self.commands = [ ]
        self.z_posisition = z_posisition

    def __str__(self):
        return "Layer[Z:%f,Commands: %s]" % (self.z_posisition,[str(command) for command in self.commands])