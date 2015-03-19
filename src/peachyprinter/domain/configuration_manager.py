class ConfigurationManager(object):

    def list(self):
        raise NotImplementedException("Abstract Class")

    def load(self, printer_name):
        raise NotImplementedException("Abstract Class")

    def save(self, configuration):
        raise NotImplementedException("Abstract Class")

    def new(self, printer_name):
        raise NotImplementedException("Abstract Class")

    def get_current_config(self):
        raise NotImplementedException("Abstract Class")

