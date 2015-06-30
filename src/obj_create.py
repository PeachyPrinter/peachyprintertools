from peachyprinter.infrastructure import print_test_layer_generators as lg
import inspect
from peachyprinter.domain.layer_generator import LayerGenerator
from peachyprinter.domain.commands import LateralMove
import re
import os

height = 1
width = 1
layer_height = 0.05
out_folder = os.path.join('..', '..', 'kivypeachyprinter', 'src', 'resources', 'objects')

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
    outfile = os.path.join(out_folder, file_name + '.obj')


    vertices = []
    breaks = []
    commands_per_layer = None
    layer_count = 0
    last_pos = None

    for layer in layers:
        last_pos = layer.commands[0].start
        layer_count += 1
        if commands_per_layer is None:
            commands_per_layer = len(layer.commands)
        if len(layer.commands) != commands_per_layer:
            print ("This aint going to work")
        for command in layer.commands:
            if command.start != last_pos or type(command) == LateralMove:
                breaks.append(True)
            else:
                breaks.append(False)
            x, y = command.end
            z = layer.z
            vertices.append([x, z, y])
            last_pos = command.end


    print "Layers: {}".format(layer_count)
    print "Verticies count: {}".format(len(vertices))
    print "Commands per layer: {}".format(commands_per_layer)
    faces = []
    current_layer = 0
    while current_layer < layer_count - 1:
        offset = current_layer * commands_per_layer
        for pos in range(0, commands_per_layer):
            if breaks[offset + pos + 1] == False:
                D = pos
                C = (pos + 1) if (pos < commands_per_layer - 1) else 0
                B = ((pos + 1) if (pos < commands_per_layer - 1) else 0) + commands_per_layer
                A = pos + commands_per_layer
                faces.append([offset + A + 1, offset + B + 1, offset + C + 1, offset + D + 1])
        current_layer += 1

    print "Faces aka polycount: {}".format(len(faces))

    normals = []

    def vminus(A, B):
        return [
            B[0]-A[0],
            B[1]-A[1],
            B[2]-A[2]
            ]

    def vcross(A, B):
        return [
            A[1]*B[2] - A[2]*B[1],
            A[2]*B[0] - A[0]*B[2],
            A[0]*B[1] - A[1]*B[0]
            ]


    for face in faces:
        A = vertices[face[0] - 1]
        B = vertices[face[1] - 1]
        C = vertices[face[2] - 1]
        D = vertices[face[3] - 1]

        normals.append(vcross(vminus(D,A),vminus(B,A)))
        normals.append(vcross(vminus(A,B),vminus(C,B)))
        normals.append(vcross(vminus(B,C),vminus(D,C)))
        normals.append(vcross(vminus(C,D),vminus(A,D)))

    with open(outfile, 'w') as out:
        out.write('o {}\n'.format(name))
        out.write('\n')
        for vertex in vertices:
            out.write("v\t{:.4f}\t{:.4f}\t{:.4f}\n".format(*vertex))
        out.write('\n')
        for normal in normals:
            out.write("vn\t{:.4f}\t{:.4f}\t{:.4f}\n".format(*normal))
        out.write('\n')
        for idx in range(0,len(faces)):
            face = faces[idx]
            norm = idx*4
            out.write("f\t{0}//{n1}\t{1}//{n2}\t{2}//{n3}\t{3}//{n4}\n".format(
                *face,
                n1=(norm + 1),
                n2=(norm + 2),
                n3=(norm + 3),
                n4=(norm + 4)
                ))
    print ""

