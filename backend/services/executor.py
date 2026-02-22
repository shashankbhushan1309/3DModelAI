import os
import asyncio
import uuid
import time
import subprocess
from typing import Tuple
from core.config import settings
from core.logger import setup_logger
from core.errors import ExecutionError, TimeoutError

logger = setup_logger("cad_copilot.executor")

class FreeCADExecutor:
    def __init__(self):
        self.output_dir = settings.OUTPUT_DIR

    async def _cleanup_old_files(self):
        logger.debug("Cleaning up old files...")
        now = time.time()
        for filename in os.listdir(self.output_dir):
            file_path = os.path.join(self.output_dir, filename)
            if os.path.isfile(file_path):
                # Delete files older than 1 hour
                if os.stat(file_path).st_mtime < now - 3600:
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        logger.warning(f"Failed to delete old file {file_path}: {e}")

    async def execute_script(self, code: str) -> str:
        """
        Executes the validated Python script in FreeCADCmd.
        Returns the filename of the generated STL.
        """
        executable = settings.FREECAD_PATH
        if executable:
            executable = executable.strip("'\"")

        if not executable or not os.path.exists(executable):
            raise ExecutionError(f"FreeCAD executable path is not configured or not found: {executable}")

        # Trigger cleanup asynchronously
        asyncio.create_task(self._cleanup_old_files())

        task_id = str(uuid.uuid4())
        script_path = os.path.join(self.output_dir, f"{task_id}.py")
        stl_path = os.path.join(self.output_dir, f"{task_id}.stl")
        
        # Inject standard export logic at the end of the script to ensure uniformity
        # The prompt will be instructed to create a variable named `final_shape`
        export_snippet = f"\n\nif 'final_shape' in locals() and final_shape is not None:\n    final_shape.exportStl('{stl_path.replace(chr(92), '/')}')\n"
        final_code = code + export_snippet

        with open(script_path, "w", encoding="utf-8") as f:
            f.write(final_code)

        logger.info(f"Executing FreeCAD script: {script_path}")

        try:
            # We use asyncio.to_thread with subprocess.run to avoid Windows Event Loop NotImplementedErrors
            process = await asyncio.to_thread(
                subprocess.run,
                [executable, script_path],
                capture_output=True,
                text=True,
                timeout=settings.FREECAD_TIMEOUT
            )

            if process.returncode != 0:
                err_msg = process.stderr.strip() if process.stderr else process.stdout.strip()
                logger.error(f"FreeCAD execution failed. Code: {process.returncode}. Error: {err_msg}")
                raise ExecutionError("FreeCAD script execution failed.", details=err_msg)

            # Verification: Check if STL was actually created and has size
            if not os.path.exists(stl_path):
                raise ExecutionError("FreeCAD execution succeeded, but no STL file was generated.", details="Ensure 'final_shape' exists.")
            
            if os.path.getsize(stl_path) < 100: # Less than 100 bytes is likely empty or invalid
                 raise ExecutionError("Generated STL file is too small or invalid.")

            logger.info(f"Successfully generated STL: {stl_path}")
            return f"{task_id}.stl"

        finally:
             pass # We can keep the python script for debugging if needed, or remove it.

executor = FreeCADExecutor()
