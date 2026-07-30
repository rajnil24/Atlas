HUMAN_ANS_PROMPT = """

The user's request was:
{message}

The agent executed these steps:

{plan}

The final result is:

{final_result}

Answer naturally.

Return ONLY the answer intended for the user.
Do not mention internal execution steps unless they help explain the answer.
"""