import subprocess 
import json

from pathlib import Path

class DockerClient :

    def create_container(self, workspace: Path) -> str:

        command = [
        "docker",
        "create",

        "--cpus" , "1" ,
        "--memory" , "512m" ,
        "--pids-limit", "64",
        "--network", "none",
        "--read-only",
        "--tmpfs", "/tmp",

        "-v",
        f"{workspace}:/app",
        "atlas-python:3.13",
        "python",
        "generated_code.py",
        ]
        result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
        )
        return result.stdout.strip()

    def start_container(self, container_id: str) -> None:
    
            command = [
            "docker",
            "start",
            container_id,
            ]
            subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            )

    def wait_container(self, container_id: str, timeout: int = 10) -> int:

        command = [
        "docker",
        "wait",
        container_id,
        ]
        result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout,
       
        )
        return int(result.stdout.strip())

    def logs_container(self, container_id: str) -> tuple[str, str]:

        command = [
        "docker",
        "logs",
        container_id,
        ]
        result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
        )
        return result.stdout, result.stderr

    def stop_container(self, container_id: str) -> None:

        command = [
        "docker",
        "stop",
        container_id,
        ]
        subprocess.run(
        command,
        capture_output=True,
        text=True,
        check = False ,
        )

    def inspect_container(self, container_id: str) -> dict:

        command = [
        "docker",
        "inspect",
        container_id,
        ]
        result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
        )
        return json.loads(result.stdout)[0]

    def remove_container(self, container_id: str) -> None:

        command = [
        "docker",
        "rm",
        "-f",
        container_id,
        ]
        subprocess.run(
        command,
        capture_output=True,
        text=True,
        )