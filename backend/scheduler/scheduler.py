from backend.models.plan import Plan , StepStatus , PlanStep


class DependencyGraph:
    """Read-only view of which steps exist and who depends on whom."""

    def __init__(self, steps: list[PlanStep]):
        self.steps: dict[str, PlanStep] = {s.step_id: s for s in steps}

    def get_step(self, step_id: str) -> PlanStep:
        return self.steps[step_id]

    def all_step_ids(self) -> list[str]:
        return list(self.steps.keys())


class Scheduler:
    """Tracks execution state and decides which steps are ready to run."""

    def __init__(self, plan: Plan):
        self.graph = DependencyGraph(plan.steps)
        self.completed: set[str] = set()
        self.failed: set[str] = set()
        self.blocked: set[str] = set()     # skipped because a dependency failed
        self.dispatched: set[str] = set()  # currently running

    def get_ready_steps(self) -> list[PlanStep]:
        ready = []
        for step_id, step in self.graph.steps.items():
            if step_id in (self.completed | self.failed | self.blocked | self.dispatched):
                continue

            if any(dep in self.failed or dep in self.blocked for dep in step.depends_on):
                self.blocked.add(step_id)
                step.status = StepStatus.SKIPPED
                continue

            if all(dep in self.completed for dep in step.depends_on):
                ready.append(step)

        return ready

    def mark_dispatched(self, step_id: str):
        self.dispatched.add(step_id)

    def mark_completed(self, step_id: str):
        self.completed.add(step_id)
        self.dispatched.discard(step_id)

    def mark_failed(self, step_id: str):
        self.failed.add(step_id)
        self.dispatched.discard(step_id)

    def is_done(self) -> bool:
        total = len(self.graph.steps)
        return len(self.completed) + len(self.failed) + len(self.blocked) == total