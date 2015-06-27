from peachyprinter.infrastructure import print_test_layer_generators as lg
import inspect
from peachyprinter.domain.layer_generator import LayerGenerator
import re

height = 1
width = 1
layer_height = 0.01
out_folder = '/opt/git/kivypeachyprinter/src/resources/objects/'

pattern = re.compile('[\W_]+')

available_prints = {}
for name in dir(lg):
    obj = getattr(lg, name)
    if inspect.isclass(obj):
        if issubclass(obj, LayerGenerator):
            if hasattr(obj, 'name'):
                available_prints[obj.name] = obj

for name, cls in available_prints.items():
    print "Building: {}".format(name)
    layers = cls(height, width, layer_height)
    file_name = pattern.sub('', name)
    outfile = out_folder + file_name + '.obj'


    vertices = []
    commands_per_layer = None
    layer_count = 0

    for layer in layers:
        layer_count += 1
        if commands_per_layer is None:
            commands_per_layer = len(layer.commands)
        if len(layer.commands) != commands_per_layer:
            print ("This aint going to work")
        for command in layer.commands:
            x, y = command.end
            z = layer.z
            vertices.append([x, y, z])

    print "Layers: {}".format(layer_count)
    print "Verticies count: {}".format(len(vertices))
    print "Commands per layer: {}".format(commands_per_layer)
    faces = []
    current_layer = 0
    while current_layer < layer_count - 1:
        offset = current_layer * commands_per_layer
        for pos in range(0, commands_per_layer):
            D = pos
            C = (pos + 1) if (pos < commands_per_layer - 1) else 0
            B = ((pos + 1) if (pos < commands_per_layer - 1) else 0) + commands_per_layer
            A = pos + commands_per_layer
            faces.append([offset + A + 1, offset + B + 1, offset + C + 1, offset + D + 1])
        current_layer += 1

    print "Faces aka polycount: {}".format(len(faces))

    with open(outfile, 'w') as out:
        out.write('o {}\n'.format(name))
        for vertex in vertices:
            out.write("v\t{:.4f}\t{:.4f}\t{:.4f}\n".format(*vertex))
        out.write('\n')
        for face in faces:
            out.write("f\t{}\t{}\t{}\t{}\n".format(*face))
    print ""

