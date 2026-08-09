from enum import Enum
from pydantic import BaseModel


class FeedbackVerdict(str, Enum):
    PASS = "pass"
    NEEDS_REVISION = "needs_revision"
    FAIL = "fail"

class Feedback(BaseModel):
    verdict: FeedbackVerdict
    reason: str
    retryable: bool = False
    suggested_fix: str | None = None