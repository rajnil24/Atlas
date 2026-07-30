import subprocess
from pathlib import Path

class DockerExecutor:

    def execute(self, workspace: Path):
        """
        Executes generated_code.py inside Docker.
        """
        command = [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{workspace}:/app",
            "-w",
            "/app",
            "python:3.13-slim",
            "python",
            "generated_code.py",
        ]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
        }