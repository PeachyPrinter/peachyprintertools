from math import sin, cos, tan, pi, radians

z_height = 0.01
build_vol = (100,100,32767)

z_template = 'G0 F15000 X%.2f Y%.2f Z%.2f\n'
m_template_i = 'G1 F12000 X%.2f Y%.2f E0.11104\n'
m_template = 'G1 X%.2f Y%.2f E0.20125\n'

x,y = (30,0)
layer = 0

def circle(afile, start_z, end_z, build_vol):
    global layer,x,y
    radius = max(build_vol[:2])
    current_z = start_z
    while (current_z <= end_z):
        afile.write(";LAYER: %s\n" % layer)
        afile.write(z_template % (x,y,current_z))
        first = True
        for theta in range(0,360, 6):
            x = cos(radians(theta)) * radius
            y = sin(radians(theta)) * radius 
            if first:
                first = False
                afile.write(m_template_i % (x,y))
            else:
                afile.write(m_template % (x,y))
        current_z += z_height
        layer += 1
        

def square(afile, start_z, end_z, build_vol):
    global layer,x,y
    radius = max(build_vol[:2])
    current_z = start_z
    while (current_z <= end_z):
        afile.write(";LAYER: %s\n" % layer)
        afile.write(z_template % (x,y,current_z))
        x,y = radius, radius
        afile.write(m_template_i % (x,y))
        x,y = radius, -radius
        afile.write(m_template %   (x,y))
        x,y = -radius, -radius
        afile.write(m_template %   (x,y))
        x,y = -radius, radius
        afile.write(m_template %   (x,y))
        current_z += z_height
        layer += 1


def spiral():
    pass

with open ('gcode_test.gcode' , 'w') as afile:
    afile.write('G21\n') #mm
    circle(afile, 0.00,2.0, build_vol)
    square(afile, 2.00,4.0, build_vol)