# FreeCAD Part Module: Complex Shape Patterns

## Pattern: Hollow Box (Enclosure/Housing)
Create an outer box, then cut a slightly smaller inner box from it, leaving walls of specified thickness.

```python
import FreeCAD, Part
from FreeCAD import Vector

wall = 3  # wall thickness in mm
outer = Part.makeBox(100, 60, 40)
inner = Part.makeBox(100 - 2*wall, 60 - 2*wall, 40 - wall, Vector(wall, wall, wall))
final_shape = outer.cut(inner)
```

## Pattern: Cylinder with Multiple Radial Holes
Create a main cylinder body, then cut smaller cylinders at angular intervals around it.

```python
import FreeCAD, Part, math
from FreeCAD import Vector

body = Part.makeCylinder(30, 50)
bolt_circle_radius = 20
num_holes = 6
result = body
for i in range(num_holes):
    angle = i * (360 / num_holes)
    rad = math.radians(angle)
    x = bolt_circle_radius * math.cos(rad)
    y = bolt_circle_radius * math.sin(rad)
    hole = Part.makeCylinder(3, 50)
    hole.translate(Vector(x, y, 0))
    result = result.cut(hole)
final_shape = result
```

## Pattern: Stepped Shaft
Fuse multiple cylinders of decreasing radius to create a stepped shaft.

```python
import FreeCAD, Part
from FreeCAD import Vector

steps = [(15, 20), (12, 30), (8, 25), (6, 15)]  # (radius, length)
result = None
z_offset = 0
for radius, length in steps:
    cyl = Part.makeCylinder(radius, length)
    cyl.translate(Vector(0, 0, z_offset))
    if result is None:
        result = cyl
    else:
        result = result.fuse(cyl)
    z_offset += length
final_shape = result
```

## Pattern: T-Bracket
Two rectangular bars fused at a right angle (T-junction).

```python
import FreeCAD, Part
from FreeCAD import Vector

vertical = Part.makeBox(10, 10, 80)
horizontal = Part.makeBox(60, 10, 10, Vector(-25, 0, 70))
final_shape = vertical.fuse(horizontal)
```

## Pattern: Rounded Plate with Center Hole
A plate with filleted edges and a central through-hole.

```python
import FreeCAD, Part
from FreeCAD import Vector

plate = Part.makeBox(80, 50, 8)
hole = Part.makeCylinder(10, 8, Vector(40, 25, 0))
plate_with_hole = plate.cut(hole)
final_shape = plate_with_hole.makeFillet(3, plate_with_hole.Edges)
```

## Pattern: Cone Frustum
A truncated cone (frustum) with different top and bottom radii.

```python
import FreeCAD, Part
final_shape = Part.makeCone(30, 15, 50)  # bottom_r=30, top_r=15, height=50
```

## Pattern: Cross-shaped Extrusion
Define a cross-shaped 2D profile and extrude it.

```python
import FreeCAD, Part
from FreeCAD import Vector

w, h, t = 40, 40, 8  # total width, height, arm thickness
# Horizontal bar
bar_h = Part.makeBox(w, t, 20, Vector(-w/2, -t/2, 0))
# Vertical bar
bar_v = Part.makeBox(t, h, 20, Vector(-t/2, -h/2, 0))
final_shape = bar_h.fuse(bar_v)
```
