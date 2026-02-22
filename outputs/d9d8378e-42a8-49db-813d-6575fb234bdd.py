import FreeCAD
import Part

# User wanted a 20x20x20mm box
final_shape = Part.makeBox(20, 20, 20)

if 'final_shape' in locals() and final_shape is not None:
    final_shape.exportStl('C:/Users/91906/Desktop/3DModelAI/outputs/d9d8378e-42a8-49db-813d-6575fb234bdd.stl')
