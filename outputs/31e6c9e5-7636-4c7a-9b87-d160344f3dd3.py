import FreeCAD
import Part

# User wanted a 20x20x20 cube
final_shape = Part.makeBox(20, 20, 20)

if 'final_shape' in locals() and final_shape is not None:
    final_shape.exportStl('C:/Users/91906/Desktop/3DModelAI/outputs/31e6c9e5-7636-4c7a-9b87-d160344f3dd3.stl')
