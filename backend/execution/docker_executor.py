from backend.execution.docker_client import DockerClient
from pathlib import Path
import time
import subprocess
from backend.execution.execution_results import ExecutionResult
from backend.execution.execution_status import ExecutionStatus
class DockerExecutor:

    def __init__(self) :
        self.client = DockerClient()

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
    
    def execute(self, workspace: Path) -> ExecutionResult:

        start_time = time.perf_counter()
        container_id = None
        try:

            container_id = self.client.create_container(workspace)
            self.client.start_container(container_id)
            exit_code = self.client.wait_container(container_id)
            execution_time = time.perf_counter() - start_time
            container_info = self.client.inspect_container(container_id)
            oom_killed = container_info["State"]["OOMKilled"]
            stdout, stderr = self.client.logs_container(container_id)
            
            status = self.determine_status(
               exit_code=exit_code,
               timed_out=False,
               oom_killed=oom_killed,
               )
            return ExecutionResult(
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            timed_out=False,
            execution_time=execution_time,
            status = status 
            )
        except subprocess.TimeoutExpired:
            if container_id:
               self.client.stop_container(container_id)
               stdout, stderr = self.client.logs_container(container_id)
            else:
               stdout = ""
               stderr = ""
            execution_time = time.perf_counter() - start_time
            return ExecutionResult(
            stdout=stdout,
            stderr=stderr + "\nExecution timed out.",
            exit_code=137,
            timed_out=True,
            execution_time=execution_time,
            status=ExecutionStatus.TIME_LIMIT_EXCEEDED,
            )
        finally:
            if container_id:
               self.client.remove_container(container_id)


        