"""Per-request collection of locally executed tool names."""

from contextvars import ContextVar

current_tool_activity: ContextVar[list[str] | None] = ContextVar("current_tool_activity", default=None)


def record_tool(name: str) -> None:
    activity = current_tool_activity.get()
    if activity is not None:
        activity.append(name)
