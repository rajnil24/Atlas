from pathlib import Path
import tempfile
import shutil
import os
import getpass
import socket

class TempWorkspace:
    def __init__(self , base_path: str = "/atlas/workspaces"):
        self.base_path = Path(base_path)
        self.workspace_path: Path | None = None

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
        print("base_path:", self.base_path)
        print("base exists:", self.base_path.exists())
        print("base parent exists:", self.base_path.parent.exists())
        print("base writable:", os.access(self.base_path, os.W_OK))
        print("parent writable:", os.access(self.base_path.parent, os.W_OK))
        print("=====================================")
        self.base_path.mkdir(parents=True, exist_ok=True)
        print("################## temp_workspace 30")
        self.workspace_path = Path(
            tempfile.mkdtemp(
                prefix="atlas_",
                dir=self.base_path
            )
        )
        print("################## temp_workspace 37")
        return self.workspace_path

    def write_code(self, code: str):
        """
        Writes generated python code into the workspace.
        """
        if self.workspace_path is None:
            raise RuntimeError("Workspace has not been created.")

        code_file = self.workspace_path / "generated_code.py"

        code_file.write_text(
            code,
            encoding="utf-8"
        )

        return code_file

    def cleanup(self):
        """
        Deletes the temporary workspace.
        """
        if self.workspace_path and self.workspace_path.exists():
            shutil.rmtree(self.workspace_path)

        self.workspace_path = None