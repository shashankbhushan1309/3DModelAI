import FreeCAD
import Part
from FreeCAD import Vector

arm1 = Part.makeBox(10, 40, 60)
arm2 = Part.makeBox(50, 40, 10)
hole_radius = 3.5
hole_depth = 6

# Vertical arm hole
hole1 = Part.makeCylinder(hole_radius, hole_depth)
hole1.translate(Vector(10/2, 40/2, 60/2))
arm1 = arm1.cut(hole1)

# Horizontal arm hole
hole2 = Part.makeCylinder(hole_radius, hole_depth)
hole2.translate(Vector(50/2, 40/2, 10/2))
arm2 = arm2.cut(hole2)

final_shape = arm1.fuse(arm2)

if 'final_shape' in locals() and final_shape is not None:
    final_shape.exportStl('C:/Users/91906/Desktop/3DModelAI/backend/outputs/14ede333-b7f1-41a2-9604-f01a19e26833.stl')
