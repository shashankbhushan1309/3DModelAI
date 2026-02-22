import FreeCAD
import Part

# User wanted a 20x20x20mm box
final_shape = Part.makeBox(20, 20, 20)

if 'final_shape' in locals() and final_shape is not None:
    final_shape.exportStl('C:/Users/91906/Desktop/3DModelAI/backend/outputs/8ae36a47-e139-4bd5-bfc9-f9380a9d4b41.stl')
