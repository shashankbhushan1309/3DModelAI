import FreeCAD
import Part

# User wanted a 20x20x20mm box
final_shape = Part.makeBox(20, 20, 20)

if 'final_shape' in locals() and final_shape is not None:
    final_shape.exportStl('C:/Users/91906/Desktop/3DModelAI/outputs/eb8bcf0e-5059-4702-8746-fa878a1d43e5.stl')
