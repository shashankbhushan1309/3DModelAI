import FreeCAD
import Part

# User wanted a 20x20x20 mm box
final_shape = Part.makeBox(20, 20, 20)

if 'final_shape' in locals() and final_shape is not None:
    final_shape.exportStl('C:/Users/91906/Desktop/3DModelAI/outputs/542bb2b3-fb20-4d12-88b2-a5afa1248bd6.stl')
