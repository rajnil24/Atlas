import subprocess 
import json
from pathlib import Path
from backend.execution.temp_workspace import Workspace
class DockerClient :

    def create_container(self, workspace: Workspace) -> str:

       
        print("CONTAINER EXISTS:", workspace.container_path.exists())
        print("CONTAINER PATH:", workspace.container_path)

        print("HOST PATH:", workspace.host_path)

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
        f"{workspace.host_path}:/app",
        "atlas-python:3.13",
        "python",
        "generated_code.py",
        ]
        print("###################### temp_workspace 26")
        print(

            "DOCKER CREATE COMMAND:",

            command,

        )
        result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
        )
        print("###################### temp_workspace 33")
        return result.stdout.strip()

    def start_container(self, container_id: str) -> None:

            print("###################### docker_client 38")
            print("^^^^^^^^^^^^^^^ conainer id is " ,container_id )
            command = [
            "docker",
            "start",
            container_id,
            ]
            print("###################### docker_client 45")
            """
            subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            )
            """
            result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
)

            print("RETURN CODE:", result.returncode)
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)

            if result.returncode != 0:
                raise RuntimeError(
                f"Docker command failed.\n"
                f"Command: {command}\n"
                f"Return code: {result.returncode}\n"
                f"stdout: {result.stdout}\n"
                f"stderr: {result.stderr}"
            )

            print("###################### docker_client 74")
        

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

    def kill_container(self, container_id: str) -> None:

        subprocess.run(
            ["docker", "kill", container_id],
            capture_output=True,
            text=True,
            check=False,
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
        check = False,
        )