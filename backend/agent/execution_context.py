import re
from typing import Any


class ExecutionContext:
    """
    Stores outputs of previously executed steps.

    Used by the Agent while executing one plan.
    """

    def __init__(self):
        self.results: dict[str, Any] = {}

    def set_result(
        self,
        step_id: str,
        output: Any
    ) -> None:

        self.results[step_id] = output

    def get_result(
        self,
        step_id: str
    ) -> Any:

        return self.results.get(step_id)

    def resolve(
        self,
        value: Any
    ) -> Any:
        """
        Replace references like

        {{step_1.output}}

        with their actual values.
        """

        if isinstance(value, str):
            #print("value inside exeution context is VV")
            #print(value)
            pattern = r"\{\{(step_\d+\.output(?:\.[a-zA-Z_]\w*)*)\}\}"
            matches = re.findall(pattern, value)
            #print(matches)
            for match in matches:
                parts = match.split(".")
                step_id = parts[0]
                if step_id not in self.results:
                    raise ValueError(
                        f"No output found for {step_id} , execution_context.py line53"
                    )
                current = self.results[step_id]

                for key in parts[2:]:
                    if not isinstance(current, dict):
                        raise ValueError(
                            f"{key} cannot be accessed ,execution_context.py line60"
                        )
                    current = current[key]
                value = value.replace(
                    "{{" + match + "}}",
                    str(current)
                )
            return value

        elif isinstance(value, dict):

            return {
                k: self.resolve(v)
                for k, v in value.items()
            }

        elif isinstance(value, list):

            return [
                self.resolve(v)
                for v in value
            ]

        return value