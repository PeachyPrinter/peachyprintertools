import inspect

from peachyprinter.domain.layer_generator import LayerGenerator
from peachyprinter.infrastructure import print_test_layer_generators


class TestPrintAPI(object):
    '''Api used for getting test prints
    Typical usage:
    
    API = TestPrintAPI()
    selected_print = API.test_print_names()[0]
    height = 30 
    width = 30 
    layer_height = 0.01

    test_print = API.get_test_print(selected_print,height,width,layer_height)
    '''

    def __init__(self):
        self.test_prints = self._get_test_prints()

    def test_print_names(self):
        '''Returns list of test prints by name'''

        return self.test_prints.keys()

    def get_test_print(self, name, height, width, layer_height, speed=100):
        '''Gets the layer generator for a print with the name with height, width, and layer height'''

        return self.test_prints[name](height, width, layer_height, speed)

    def _get_test_prints(self):
        available_prints = {}
        for name in dir(print_test_layer_generators):
            obj = getattr(print_test_layer_generators, name)
            if inspect.isclass(obj):
                if issubclass(obj, LayerGenerator):
                    if hasattr(obj, 'name'):
                        available_prints[obj.name] = obj
        return available_prints
