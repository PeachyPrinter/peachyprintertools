from math import sin, cos, tan, pi, radians

z_height = 0.1
build_vol = (20,20,32767)

z_template = 'G1 X%.2f Y%.2f Z%.2f F2000\n'
m_template_i = 'G1 X%.2f Y%.2f E%.6f F2000\n'
m_template = 'G1 X%.2f Y%.2f E%.6f\n'

x,y = (30,0)
layer = 0
extrude = 0.0
extrude_inc = 0.1


def circle(afile, start_z, end_z, build_vol):
    global layer,x,y,extrude
    radius = max(build_vol[:2])
    current_z = start_z
    while (current_z <= end_z):
        afile.write(";LAYER: %s\n" % layer)
        afile.write(z_template % (x,y,current_z))
        first = True
        for theta in range(0,360, 4):
            extrude += extrude_inc
            x = cos(radians(theta)) * radius
            y = sin(radians(theta)) * radius 
            if first:
                first = False
                afile.write(m_template_i % (x,y,extrude))
            else:
                afile.write(m_template % (x,y,extrude))
        current_z += z_height
        layer += 1
        

def square(afile, start_z, end_z, build_vol):
    global layer,x,y,extrude
    radius = max(build_vol[:2])
    current_z = start_z
    while (current_z <= end_z):
        extrude += 0.01
        afile.write(";LAYER: %s\n" % layer)
        afile.write(z_template % (x,y,current_z))
        x,y = radius, radius
        extrude += extrude_inc
        afile.write(m_template_i % (x,y,extrude))
        x,y = radius, -radius
        extrude += extrude_inc
        afile.write(m_template %   (x,y,extrude))
        x,y = -radius, -radius
        extrude += extrude_inc
        afile.write(m_template %   (x,y,extrude))
        x,y = -radius, radius
        extrude += extrude_inc
        afile.write(m_template %   (x,y,extrude))
        current_z += z_height
        layer += 1


def buildAreaSpiral(afile, start_z, end_z, build_vol):
    global layer,x,y,extrude
    start = max(build_vol[:2])
    print(start)
    current_z = start_z
    for poso in range(0,2*start*10,1):
        pos = (poso - (start * 10))  / 10.0
        if (current_z <= end_z):
            afile.write(";LAYER: %s\n" % layer)
            afile.write(z_template % (x,y,current_z))
            x,y = pos, build_vol[1]
            extrude += extrude_inc
            afile.write(m_template_i % (x,y,extrude))
            x,y = build_vol[0], -1.0 * pos
            extrude += extrude_inc
            afile.write(m_template %   (x,y,extrude))
            x,y = -1.0 * pos, -build_vol[1]
            extrude += extrude_inc
            afile.write(m_template %   (x,y,extrude))
            x,y = -build_vol[0], pos
            extrude += extrude_inc
            afile.write(m_template %   (x,y,extrude))
            current_z += z_height
            layer += 1

with open ('gcode_test.gcode' , 'w') as afile:
    afile.write('G21\nG01 F1500\n') #mm
    # circle(afile, 0.00,50.0, build_vol)
    # square(afile, 0,50.0, build_vol)
    buildAreaSpiral(afile,0,45.0,build_vol)