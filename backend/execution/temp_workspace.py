from pathlib import Path
import tempfile
import shutil

class TempWorkspace:
    def __init__(self , base_path: str = "/atlas/workspaces"):
        self.base_path = Path(base_path)
        self.workspace_path: Path | None = None

    def create(self):
        """
        Creates a temporary directory.
        """
        self.base_path.mkdir(parents=True, exist_ok=True)

        self.workspace_path = Path(
            tempfile.mkdtemp(
                prefix="atlas_",
                dir=self.base_path
            )
        )

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