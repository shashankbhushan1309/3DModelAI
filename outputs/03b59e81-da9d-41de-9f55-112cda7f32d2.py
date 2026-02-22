import FreeCAD
import Part

# User wanted a 20x20x20mm box
final_shape = Part.makeBox(20, 20, 20)

if 'final_shape' in locals() and final_shape is not None:
    final_shape.exportStl('C:/Users/91906/Desktop/3DModelAI/outputs/03b59e81-da9d-41de-9f55-112cda7f32d2.stl')
