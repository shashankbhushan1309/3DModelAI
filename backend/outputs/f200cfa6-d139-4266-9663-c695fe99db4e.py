import FreeCAD
import Part

# User wanted a 20x20x20 mm box
final_shape = Part.makeBox(20, 20, 20)

if 'final_shape' in locals() and final_shape is not None:
    final_shape.exportStl('C:/Users/91906/Desktop/3DModelAI/backend/outputs/f200cfa6-d139-4266-9663-c695fe99db4e.stl')
