import FreeCAD
import Part

# User wanted a 20x20x20 mm box
final_shape = Part.makeBox(20, 20, 20)

if 'final_shape' in locals() and final_shape is not None:
    final_shape.exportStl('C:/Users/91906/Desktop/3DModelAI/outputs/fac46f5f-05f5-4a15-85b7-72d89fea818f.stl')
