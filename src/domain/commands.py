
class Command(object):
    pass

class LateralDraw(Command):
    def __init__(self,x,y,speed):
        self.x = x
        self.y = y
        self.speed = speed

    def __str__(self):
     return "DRAW[X:%s,Y:%s,Speed:%s]" % (self.x,self.y,self.speed)

class LateralMove(Command):
    def __init__(self,x,y,speed):
        self.x = x
        self.y = y
        self.speed = speed

    def __str__(self):
     return "MOVE[X:%s,Y:%s,Speed:%s]" % (self.x,self.y,self.speed)

class VerticalMove(Command):
    def __init__(self,z,speed):
        self.z = z
        self.speed = speed

class Layer(object):
    def __init__(self, z_posisition , commands = None):
        if commands:
            self.commands = commands
        else:
            self.commands = [ ]
        self.z_posisition = z_posisition

    def get_commands(self):
        self.commands
        # yields commands