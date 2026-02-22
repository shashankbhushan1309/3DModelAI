import FreeCAD
import Part

# User wanted a 20x20x20 cube
final_shape = Part.makeBox(20, 20, 20)

if 'final_shape' in locals() and final_shape is not None:
    final_shape.exportStl('C:/Users/91906/Desktop/3DModelAI/outputs/6e839018-ea40-425a-9f1f-2771654376a1.stl')
