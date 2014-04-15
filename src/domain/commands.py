
class Command(object):
    pass

class LateralDraw(Command):
    def __init__(self,start,end,speed):
        self.start = start
        self.end = end
        self.speed = speed

    def __str__(self):
     return "DRAW[Start: %s,End:%s,Speed:%f]" % (self.start,self.end,self.speed)

class LateralMove(Command):
    def __init__(self,start,end,speed):
        self.start = start
        self.end = end
        self.speed = speed

    def __str__(self):
     return "MOVE[Start: %s,End:%s,Speed:%f]" % (self.start,self.end,self.speed)

class VerticalMove(Command):
    def __init__(self,start,end,speed):
        self.start = start
        self.end = end
        self.speed = speed
    def __str__(self):
        return "MOVEVERTICAL[Start:%s,Stop:%s,Speed:%f]" % (self.start,self.end,self.speed)

class Layer(object):
    def __init__(self, z , commands = None):
        if commands:
            self.commands = commands
        else:
            self.commands = [ ]
        self.z = z

    def __str__(self):
        return "Layer[Z:%f,Commands: %s]" % (self.z,[str(command) for command in self.commands])