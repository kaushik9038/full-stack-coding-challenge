"""Task routing and execution."""

import re
from typing import Any, Optional

from app.agent.audit_logger import AuditLogger
from app.agent.registry import ToolRegistry
from app.agent.tool_definitions import ToolScore


class TaskController:
    CONFIDENCE_THRESHOLD = 0.40
    MULTI_INTENT_THRESHOLD = 2

    def __init__(self, registry: Optional[ToolRegistry] = None) -> None:
        self.registry = registry or ToolRegistry()

    def run_task(self, task: str) -> dict:
        audit_logger = AuditLogger()
        audit_logger.record_step("received", "Task received by controller", task=task)
        clean_task = self._validate_task_text(task, audit_logger)

        tool_pick = self._choose_tool(task, clean_task, audit_logger)
        tool_name = tool_pick["selected_tool"]
        tool_definition = self.registry.get(tool_name)

        audit_logger.record_step(
            "execute",
            "Executing selected tool",
            selected_tool=tool_name,
            confidence=tool_pick["confidence"],
            selection_reason=tool_pick["selection_reason"],
            fallback_used=tool_pick["fallback_used"],
        )
        result = tool_definition.handler(task)
        audit_logger.record_step(
            "complete",
            "Tool execution completed",
            output=result["final_output"],
            metadata=result["metadata"],
            confidence=tool_pick["confidence"],
            selection_reason=tool_pick["selection_reason"],
        )

        return {
            "task": task,
            "final_output": result["final_output"],
            "selected_tool": tool_name,
            "tools_used": [tool_name],
            "execution_steps": audit_logger.export_steps(),
        }

    def _validate_task_text(self, task: str, audit_logger: AuditLogger) -> str:
        clean_text = task.strip()
        if not clean_text:
            raise ValueError("Task cannot be empty.")

        if len(clean_text) > 500:
            raise ValueError("Task must be 500 characters or fewer.")

        if not re.search(r"[A-Za-z0-9]", clean_text):
            raise ValueError("Task must include letters or numbers.")

        audit_logger.record_step(
            "validate",
            "Pre-execution validation passed",
            task_length=len(clean_text),
            has_alphanumeric=True,
        )
        return clean_text.lower()

    def _choose_tool(self, task: str, clean_task: str, audit_logger: AuditLogger) -> dict[str, Any]:
        tool_scores = [tool.score(task, clean_task) for tool in self.registry.all()]
        sorted_scores = sorted(tool_scores, key=lambda tool_score: tool_score.confidence, reverse=True)
        best_score = sorted_scores[0]

        task_intents = {score.tool: score.intent_detected for score in tool_scores}
        if self._has_multiple_intents(tool_scores):
            audit_logger.record_step(
                "compound",
                "Task matched more than one tool; using the highest-confidence match",
                intents=task_intents,
                selected_tool=best_score.tool,
                confidence=best_score.confidence,
            )

        audit_logger.record_step(
            "route",
            "Scored candidate tools",
            candidates=[self._serialize_tool_score(tool_score) for tool_score in sorted_scores],
            confidence_threshold=self.CONFIDENCE_THRESHOLD,
        )

        if best_score.confidence >= self.CONFIDENCE_THRESHOLD:
            audit_logger.record_step(
                "select",
                "Selected highest-confidence tool",
                selected_tool=best_score.tool,
                confidence=best_score.confidence,
                reason=best_score.reason,
            )
            return {
                "selected_tool": best_score.tool,
                "confidence": best_score.confidence,
                "selection_reason": best_score.reason,
                "fallback_used": False,
            }

        audit_logger.record_step(
            "unvalidated_intent",
            "Intent could not be validated with enough confidence",
            top_candidate=best_score.tool,
            top_confidence=best_score.confidence,
            confidence_threshold=self.CONFIDENCE_THRESHOLD,
            determination="No intent passed the minimum confidence threshold",
        )
        raise ValueError("Intent cannot be validated with the current level of confidence. Please clarify the task.")

    def _has_multiple_intents(self, tool_scores: list[ToolScore]) -> bool:
        return sum(1 for tool_score in tool_scores if tool_score.intent_detected) >= self.MULTI_INTENT_THRESHOLD

    def _serialize_tool_score(self, tool_score: ToolScore) -> dict[str, Any]:
        return {
            "tool": tool_score.tool,
            "confidence": tool_score.confidence,
            "signals": tool_score.signals,
            "reason": tool_score.reason,
            "intent_detected": tool_score.intent_detected,
        }
