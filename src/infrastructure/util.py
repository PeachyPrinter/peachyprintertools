class ConsoleLog(object):
    def __init__(self,on):
        self.on = on

    def info(self, message):
        if self.on:
            print(message)