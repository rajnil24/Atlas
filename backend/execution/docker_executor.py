from backend.execution.docker_client import DockerClient
from backend.execution.execution_results import ExecutionResult
from backend.execution.execution_status import ExecutionStatus
from backend.execution.temp_workspace import Workspace
from pathlib import Path
import time
import subprocess

class DockerExecutor:

    def __init__(self , timeout: int = 10, ) :
        self.client = DockerClient()
        self.timeout = timeout

    def determine_status(self,
    exit_code: int,
    timed_out: bool,
    oom_killed: bool,
    ) -> ExecutionStatus:
        
        if timed_out:
            return ExecutionStatus.TIME_LIMIT_EXCEEDED
        
        if oom_killed:
            return ExecutionStatus.MEMORY_LIMIT_EXCEEDED
        
        if exit_code == 0:
            return ExecutionStatus.SUCCESS
        
        return ExecutionStatus.RUNTIME_ERROR
    
    def execute(self, workspace: Workspace) -> ExecutionResult:

        start_time = time.perf_counter()

        container_id: str | None = None

        print("#####################docker_executor.py 37")
        print(type(workspace))
        print(workspace)

        try:

            container_id = (
                self.client.create_container(
                    workspace
                )
            )

            print("#################docker_executor.py 50 ")
            
            self.client.start_container(container_id)

            print("#################docker_executor.py 49 ")

            print(type(container_id))
            print((container_id))
            exit_code = self.client.wait_container(container_id , timeout=self.timeout,)

            execution_time = time.perf_counter() - start_time

            container_info = self.client.inspect_container(container_id)

            oom_killed = container_info["State"]["OOMKilled"]

            stdout, stderr = self.client.logs_container(container_id)
            
            status = self.determine_status(
               exit_code=exit_code,
               timed_out=False,
               oom_killed=oom_killed,
               )

            print("#################docker_executor.py 69 ")
            
            return ExecutionResult(
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            timed_out=False,
            oom_killed=oom_killed,
            execution_time=execution_time,
            status = status 
            )

        
        except subprocess.TimeoutExpired:

            execution_time = (
                time.perf_counter() - start_time
            )

            stdout = ""

            stderr = ""

            if container_id:

                self.client.stop_container(container_id)

                self.client.kill_container(container_id)

                print("#################docker_executor.py 97 ")

                try :
                    print("#################docker_executor.py 100 ")
                    stdout, stderr = (self.client.logs_container
                   (
                    container_id
                                )
                    )

                except Exception:
                    print("#################docker_executor.py 108 ")

                    pass
            print("#################docker_executor.py 111 ")
            return ExecutionResult(
                stdout=stdout,
                stderr=(
                    stderr +
                    "\nExecution timed out."
                ),
                status=ExecutionStatus.TIME_LIMIT_EXCEEDED,
                exit_code=137,
                timed_out=True,
                oom_killed=False,
                execution_time=execution_time,
            )

        except Exception as exc:

            execution_time = (
                time.perf_counter() - start_time
            )
            print("#################docker_executor.py 130 ")
            return ExecutionResult(
                stdout="",
                stderr=str(exc),
                status=ExecutionStatus.INTERNAL_ERROR,
                exit_code=-1,
                timed_out=False,
                oom_killed=False,
                execution_time=execution_time,
            )
        
        finally:
            if container_id:
               self.client.remove_container(container_id)


        