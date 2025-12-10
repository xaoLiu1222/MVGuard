from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class CheckResult:
    """Detection result for a single rule."""
    rule_id: int
    rule_name: str
    passed: bool
    reason: str = ""


class BaseChecker(ABC):
    """Base class for all rule checkers."""

    rule_id: int = 0
    rule_name: str = ""

    @abstractmethod
    def check(self, video_path: str, **kwargs) -> CheckResult:
        """Check video against this rule."""
        pass

    def _pass(self, reason: str = "") -> CheckResult:
        return CheckResult(self.rule_id, self.rule_name, True, reason)

    def _fail(self, reason: str) -> CheckResult:
        return CheckResult(self.rule_id, self.rule_name, False, reason)
