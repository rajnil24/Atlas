from pathlib import Path
import tempfile
import shutil
import os
from dataclasses import dataclass
import getpass
import socket

@dataclass
class Workspace:

    container_path: Path
    host_path: Path

class TempWorkspace:
    def __init__(self ,
                 container_base: str = "/atlas/workspaces" ,
                 host_base: str = "/Users/rajnil/Documents/i/atlas/sandbox_workspaces",):
        
        self.container_base = Path(container_base)
        self.host_base = Path(host_base)
        self.workspace: Workspace | None = None

    def create(self):
        """
        Creates a temporary directory.
        """
        print("################## temp_workspace 14")
        print("========== WORKSPACE DEBUG ==========")
        print("cwd:", os.getcwd())
        print("user:", getpass.getuser())
        print("uid:", os.getuid())
        print("hostname:", socket.gethostname())
        print("=====================================")
        self.container_base.mkdir(parents=True, exist_ok=True)
        print("################## temp_workspace 30")

        container_path = Path(
            tempfile.mkdtemp(
                prefix="atlas_",
                dir=self.container_base,
            )
        )

        relative_path = container_path.relative_to(self.container_base)

        host_path = self.host_base / relative_path

        self.workspace = Workspace(
            container_path=container_path,
            host_path=host_path,
        )

        return self.workspace

    def write_code(self, code: str):
        """
        Writes generated python code into the workspace.
        """
        if self.workspace is None:
            raise RuntimeError("Workspace has not been created.")

        code_file = self.workspace.container_path / "generated_code.py"

        code_file.write_text(
            code,
            encoding="utf-8"
        )

        return code_file

    def cleanup(self)-> None:
        """
        Deletes the temporary workspace.
        """
        if self.workspace is not None:
            if self.workspace.container_path.exists():
                shutil.rmtree(self.workspace.container_path)

        self.workspace = None