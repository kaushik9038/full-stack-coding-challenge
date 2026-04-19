"""Tool registry for the task runner."""

from app.agent.tool_definitions import ToolDefinition
from app.tools.calculator import CALCULATOR_TOOL
from app.tools.text_processor import TEXT_PROCESSOR_TOOL
from app.tools.weather_mock import WEATHER_TOOL


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {
            TEXT_PROCESSOR_TOOL.name: TEXT_PROCESSOR_TOOL,
            CALCULATOR_TOOL.name: CALCULATOR_TOOL,
            WEATHER_TOOL.name: WEATHER_TOOL,
        }

    def get(self, name: str) -> ToolDefinition:
        return self._tools[name]

    def all(self) -> list[ToolDefinition]:
        return list(self._tools.values())

    def names(self) -> list[str]:
        return list(self._tools.keys())
