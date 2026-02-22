import os
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import FileResponse
from pydantic import ValidationError as PydanticValidationError

from api.models import GenerateRequest, RefineRequest, GenerationResponse, SystemStatusResponse
from services.llm import llm_service
from services.validator import validate_code
from services.executor import executor
from services.rag import rag_service
from core.config import settings
from core.logger import setup_logger

logger = setup_logger("cad_copilot.routes")
router = APIRouter()

SYSTEM_PROMPT = """You are an expert FreeCAD Python script generator functioning as an advanced parametric CAD copilot.
Your objective is to generate ONLY valid Python code that runs headlessly inside FreeCADCmd.exe.
Output ONLY the python code. No markdown fences, no explanations, no comments outside the code.

═══════════════════════════════════════════
  ABSOLUTE RULES (violating any = failure)
═══════════════════════════════════════════
1. The LAST line of your script MUST assign the finished solid to `final_shape`.
2. `final_shape` must be a Part.Shape (TopoShape) — a true BRep solid.
3. DO NOT call `exportStl`, `exportStep`, or any file I/O — the executor handles export.
4. DO NOT import `os`, `sys`, `subprocess`, or any system module.
5. DO NOT use FreeCAD GUI modules (`FreeCADGui`, `Gui`). This runs headlessly.
6. DO NOT call `App.newDocument()` or `doc.addObject()` — you only need shapes, not documents.
7. All dimensions from the user prompt must be used EXACTLY as given.
8. When the user says "diameter", use radius = diameter / 2.
9. When the user says "centered", translate the shape so its center of mass is at origin.

═══════════════════════════════════════════
  FREECAD PART MODULE API REFERENCE
═══════════════════════════════════════════

## Standard Imports (always start with these)
import FreeCAD
import Part
from FreeCAD import Vector

## Primitive Constructors
Part.makeBox(length, width, height)                         → box at origin
Part.makeBox(length, width, height, Vector(x,y,z))          → box at position
Part.makeCylinder(radius, height)                            → cylinder along Z
Part.makeCylinder(radius, height, Vector(x,y,z), Vector(dx,dy,dz))  → positioned + directed
Part.makeSphere(radius)                                      → sphere at origin
Part.makeSphere(radius, Vector(x,y,z))                       → sphere at position
Part.makeCone(radius1, radius2, height)                      → cone/frustum along Z
Part.makeTorus(majorRadius, minorRadius)                      → torus at origin
Part.makeWedge(xmin, ymin, zmin, z2min, x2min, xmax, ymax, zmax, z2max, x2max)  → wedge

## Boolean Operations (return new Shape, original is unchanged)
shape_a.fuse(shape_b)     → union (add material)
shape_a.cut(shape_b)      → subtraction (remove material)
shape_a.common(shape_b)   → intersection (keep overlap only)

## Transformations (MODIFY shape in-place, return None)
shape.translate(Vector(dx, dy, dz))
shape.rotate(Vector(cx,cy,cz), Vector(ax,ay,az), angle_degrees)
shape.transformShape(matrix)

## Create Shape from 2D Profile (Extrusion / Revolution)
# Step 1: Make edges
edge1 = Part.makeLine(Vector(0,0,0), Vector(10,0,0))
edge2 = Part.makeLine(Vector(10,0,0), Vector(10,5,0))
# Step 2: Make wire from edges
wire = Part.Wire([edge1, edge2, ...])
# Step 3: Make face from wire
face = Part.Face(wire)
# Step 4: Extrude face into solid
solid = face.extrude(Vector(0, 0, height))
# Or revolve:
# solid = face.revolve(Vector(0,0,0), Vector(0,1,0), 360)

## Fillets and Chamfers (on solid shapes)
# shape.makeFillet(radius, edges_list)
# shape.makeChamfer(size, edges_list)
# edges_list = shape.Edges  or specific edges like [shape.Edges[0], shape.Edges[1]]

## Useful Properties
shape.Edges       → list of all edges
shape.Faces       → list of all faces
shape.Vertexes    → list of all vertices
shape.BoundBox    → bounding box (XMin, YMin, ZMin, XMax, YMax, ZMax)

═══════════════════════════════════════════
  STRATEGY FOR COMPLEX SHAPES
═══════════════════════════════════════════
Decompose the user's request into simple primitives + boolean operations:
  • L-bracket = two boxes fused together
  • Pipe = large cylinder with small cylinder cut from center
  • Flange = cylinder fused with a wider disk, with bolt holes cut
  • Enclosure = hollow box = outer box minus inner box (with wall thickness)
  • Gear-like = many cylinders arranged in a circle, fused, then cut from a disk
  • Rounded cube = box with fillets applied to edges
  • Shelf bracket = L-shape cut from a box, with a triangular support
  • Plate with holes = flat box with multiple cylinders cut from it
  • Stepped shaft = multiple cylinders of decreasing radius, fused together

For positioning: always compute x,y,z offsets from the user's dimensions.
For centering holes: translate cylinder to (width/2, depth/2, 0).
For arrays: use a for-loop with translate.

═══════════════════════════════════════════
  EXAMPLE 1 — Box with centered hole
═══════════════════════════════════════════
import FreeCAD
import Part
from FreeCAD import Vector

box = Part.makeBox(30, 30, 20)
hole = Part.makeCylinder(5, 20)
hole.translate(Vector(15, 15, 0))
final_shape = box.cut(hole)

═══════════════════════════════════════════
  EXAMPLE 2 — L-Bracket
═══════════════════════════════════════════
import FreeCAD
import Part
from FreeCAD import Vector

# Vertical arm
arm1 = Part.makeBox(10, 40, 60)
# Horizontal arm
arm2 = Part.makeBox(50, 40, 10)
final_shape = arm1.fuse(arm2)

═══════════════════════════════════════════
  EXAMPLE 3 — Hollow cylinder (pipe)
═══════════════════════════════════════════
import FreeCAD
import Part
from FreeCAD import Vector

outer = Part.makeCylinder(20, 50)
inner = Part.makeCylinder(15, 50)
final_shape = outer.cut(inner)

═══════════════════════════════════════════
  EXAMPLE 4 — Plate with 4 bolt holes
═══════════════════════════════════════════
import FreeCAD
import Part
from FreeCAD import Vector

plate = Part.makeBox(100, 60, 5)
offsets = [(15,15), (85,15), (15,45), (85,45)]
result = plate
for ox, oy in offsets:
    hole = Part.makeCylinder(4, 5)
    hole.translate(Vector(ox, oy, 0))
    result = result.cut(hole)
final_shape = result

═══════════════════════════════════════════
  EXAMPLE 5 — Custom L-profile via extrusion
═══════════════════════════════════════════
import FreeCAD
import Part
from FreeCAD import Vector

# Draw L-shaped 2D profile
points = [Vector(0,0,0), Vector(50,0,0), Vector(50,5,0),
          Vector(5,5,0), Vector(5,30,0), Vector(0,30,0), Vector(0,0,0)]
edges = [Part.makeLine(points[i], points[i+1]) for i in range(len(points)-1)]
wire = Part.Wire(edges)
face = Part.Face(wire)
final_shape = face.extrude(Vector(0, 0, 100))

═══════════════════════════════════════════
  EXAMPLE 6 — Flanged shaft with keyway
═══════════════════════════════════════════
import FreeCAD
import Part
from FreeCAD import Vector

shaft = Part.makeCylinder(10, 80)
flange = Part.makeCylinder(25, 8)
flange.translate(Vector(0, 0, 0))
body = shaft.fuse(flange)
keyway = Part.makeBox(4, 20, 40, Vector(-2, -10, 40))
final_shape = body.cut(keyway)
"""

@router.get("/status", response_model=SystemStatusResponse)
async def get_status():
    """Health check endpoint to verify component availability."""
    ollama_ok = await llm_service.check_health()
    freecad_ok = settings.FREECAD_PATH is not None and os.path.exists(settings.FREECAD_PATH)
    
    # Check if we can write to output dir
    output_writable = os.access(settings.OUTPUT_DIR, os.W_OK)
    
    rag_status = rag_service.check_health()
    
    overall = "ok"
    if not ollama_ok or not freecad_ok or not output_writable:
         overall = "error"
    elif not rag_status["initialized"] and settings.ENABLE_RAG:
         overall = "warning"
         
    return SystemStatusResponse(
        status=overall,
        ollama_reachable=ollama_ok,
        freecad_available=freecad_ok,
        freecad_executable=settings.FREECAD_PATH,
        rag_status=rag_status,
        output_dir_writable=output_writable
    )

@router.post("/generate", response_model=GenerationResponse)
async def generate_model(request: GenerateRequest, http_request: Request):
    logger.info(f"Generating new model. Prompt: {request.prompt[:50]}...")
    
    # 1. Retrieve RAG context
    context = rag_service.retrieve_context(request.prompt)
    prompt_with_context = request.prompt + context
    
    # 2. Call LLM
    raw_code = await llm_service.generate_code(prompt_with_context, SYSTEM_PROMPT)
    
    # 3. Validate code (will raise CopilotException if failed, caught by handler)
    validated_code = validate_code(raw_code)
    
    # 4. Execute FreeCAD
    stl_filename = await executor.execute_script(validated_code)
    
    # 5. Build URL (relative path — Vite proxy routes /outputs to this server)
    stl_url = f"/outputs/{stl_filename}"
    
    return GenerationResponse(status="success", stl_url=stl_url, code=validated_code)

@router.post("/refine", response_model=GenerationResponse)
async def refine_model(request: RefineRequest, http_request: Request):
    logger.info("Refining existing model.")
    
    refine_system_prompt = SYSTEM_PROMPT + f"\n\nHere is the PREVIOUS CODE you must modify based on the new instruction:\n```python\n{request.original_code}\n```"
    
    # LLM
    raw_code = await llm_service.generate_code(request.instruction, refine_system_prompt)
    
    # Validate
    validated_code = validate_code(raw_code)
    
    # Execute
    stl_filename = await executor.execute_script(validated_code)
    
    # URL (relative path — Vite proxy routes /outputs to this server)
    stl_url = f"/outputs/{stl_filename}"
    
    return GenerationResponse(status="success", stl_url=stl_url, code=validated_code)
