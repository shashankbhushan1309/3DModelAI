import ast
import re
from typing import Set, List
from core.config import settings
from core.logger import setup_logger
from core.errors import ValidationError

logger = setup_logger("cad_copilot.validator")

# Critical built-in functions / modules that should absolutely not be in generated scripts
BANNED_BUILTINS = {
    'exec', 'eval', 'open', 'compile', '__import__', 'getattr', 'setattr', 'delattr',
    'globals', 'locals', 'vars', 'memoryview', 'SystemExit'
}

BANNED_IMPORTS = {
    'os', 'sys', 'subprocess', 'shutil', 'socket', 'urllib', 'requests', 'http', 'asyncio', 'threading', 'multiprocessing'
}

class SecurityNodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.errors: List[str] = []
        self.found_export = False
        self.has_none_shape = False

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            if alias.name.split('.')[0] in BANNED_IMPORTS:
                self.errors.append(f"Banned import detected: {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module and node.module.split('.')[0] in BANNED_IMPORTS:
            self.errors.append(f"Banned import detected: {node.module}")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            if node.func.id in BANNED_BUILTINS:
                self.errors.append(f"Banned function call detected: {node.func.id}()")
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in BANNED_BUILTINS:
                 self.errors.append(f"Banned attribute call detected: {node.func.attr}")
            # Try to detect if export is called. In FreeCAD, it's often shape.exportStl or Mesh.export
            if node.func.attr in ['exportStl', 'export', 'exportStep']:
                self.found_export = True
        self.generic_visit(node)
        
    def visit_Assign(self, node: ast.Assign):
        # Check if someone assigns None to a shape intentionally (basic check)
        if isinstance(node.value, ast.Constant) and node.value.value is None:
            for target in node.targets:
                if isinstance(target, ast.Name) and 'shape' in target.id.lower():
                    self.has_none_shape = True
        self.generic_visit(node)


def validate_code(code: str) -> str:
    """
    Validates FreeCAD Python script for security, length, syntax, and required logic.
    Raises ValidationError if any checks fail.
    Returns the sanitized code if successful.
    """
    code = code.strip()

    # 1. Normalize line endings
    code = code.replace('\r\n', '\n')
    lines = code.split('\n')

    # 2. Length check
    if len(lines) > settings.MAX_SCRIPT_LENGTH:
        raise ValidationError(f"Script exceeds maximum allowed length of {settings.MAX_SCRIPT_LENGTH} lines.", details=f"Actual length: {len(lines)}")
    if len(lines) == 0 or not code:
        raise ValidationError("Generated script is empty.")

    # 3. Syntax and AST validation
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        raise ValidationError("Generated script contains syntax errors.", details=str(e))

    visitor = SecurityNodeVisitor()
    visitor.visit(tree)

    if visitor.errors:
        raise ValidationError("Security violation detected in script.", details="; ".join(visitor.errors))

    if visitor.has_none_shape:
        raise ValidationError("Script appears to assign None to a shape variable.")

    # 4. Extraneous basic checks (Regex fallback for absolute paths)
    # Block any hardcoded absolute paths to 'C:\' or '/'
    if re.search(r"['\"]([A-Za-z]:\\[^'\"]*|/[^'\"]+)['\"]", code):
        logger.warning("Hardcoded absolute path detected, although might be benign. Allowing but warning.")

    logger.info("Script validation passed successfully.")
    return code
