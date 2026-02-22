import FreeCAD
import Part

# User wanted a 30x30x30 cube
final_shape = Part.makeBox(30, 30, 30)

if 'final_shape' in locals() and final_shape is not None:
    final_shape.exportStl('C:/Users/91906/Desktop/3DModelAI/backend/outputs/6296d0ab-2fc6-4b88-a70a-4959f01c4587.stl')
