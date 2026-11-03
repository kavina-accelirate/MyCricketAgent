"""Multi-agent cricket assistant backed by the OpenAI Agents SDK."""

import os
from typing import Any

from agents import Agent, ModelSettings, Runner
from dotenv import load_dotenv

from .tools.activity import current_tool_activity
from .tools.cricket_tools import (
    calculate_required_run_rate,
    calculate_strike_rate,
    lookup_player_stats,
    search_cricket_rules,
)

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

BASE_STYLE = (
    "Respond in the user's language in 1 to 3 short plain-text lines, at most 60 words. "
    "Do not invent facts, live scores, or recent results."
)
MEDIUM_REASONING = ModelSettings(reasoning={"effort": "medium"})


def build_coordinator(model: str) -> Agent:
    rules_agent = Agent(
        name="Cricket Rules Specialist",
        model=model,
        model_settings=MEDIUM_REASONING,
        instructions=(
            "Answer cricket rules questions using only the search_cricket_rules tool. "
            "Call the tool first. Explain when the local rules dataset has no match. "
            "Do not answer statistics questions. " + BASE_STYLE
        ),
        tools=[search_cricket_rules],
    )
    stats_agent = Agent(
        name="Cricket Stats Analyst",
        model=model,
        model_settings=MEDIUM_REASONING,
        instructions=(
            "Handle player statistics and cricket calculations. Use lookup_player_stats "
            "for every player named in the question. The bundled player profiles are "
            "synthetic demo data, never present them as real-world records. Use the "
            "calculation tools for requested strike rates and required run rates. "
            "State clearly when a player is absent from the demo dataset. " + BASE_STYLE
        ),
        tools=[lookup_player_stats, calculate_strike_rate, calculate_required_run_rate],
    )
    reviewer = Agent(
        name="Cricket Answer Reviewer",
        model=model,
        model_settings=MEDIUM_REASONING,
        instructions=(
            "Review the supplied draft and evidence. Keep only claims supported by the "
            "evidence, correct arithmetic if the tool outputs make the correction clear, "
            "and make unsupported or missing data explicit. Return only the corrected "
            "user-facing answer. Never add new cricket facts. " + BASE_STYLE
        ),
    )
    return Agent(
        name="Cricket Coordinator",
        model=model,
        model_settings=MEDIUM_REASONING,
        instructions=(
            "You coordinate a cricket assistant workflow. For a factual rules question, "
            "call the rules_research specialist. For player data or calculations, call "
            "the stats_research specialist. For questions that need both rules and stats, "
            "call both and combine their evidence. For greetings or conversational requests, "
            "you may answer directly. Before returning any factual answer, call "
            "review_answer with the original question, specialist evidence, and your draft. "
            "Use the reviewer's result as the final answer. Do not claim access to live "
            "scores or current match data. " + BASE_STYLE
        ),
        tools=[
            rules_agent.as_tool(
                tool_name="rules_research",
                tool_description="Research a cricket rules question using the local rules dataset.",
            ),
            stats_agent.as_tool(
                tool_name="stats_research",
                tool_description="Look up demo player stats and calculate cricket rates.",
            ),
            reviewer.as_tool(
                tool_name="review_answer",
                tool_description="Check a draft answer against the gathered evidence before replying.",
            ),
        ],
    )


class CricketAgent:
    """Run the cricket multi-agent workflow using the configured model and API key."""

    def __init__(self) -> None:
        self.coordinator = build_coordinator(OPENAI_MODEL)

    async def answer(
        self,
        question: str,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        if not OPENAI_API_KEY:
            raise RuntimeError("Set OPENAI_API_KEY in the project .env file or environment.")

        activity: list[str] = []
        activity_token = current_tool_activity.set(activity)
        try:
            result = await Runner.run(
                self.coordinator,
                question,
                previous_response_id=session_id,
                max_turns=12,
            )
        finally:
            current_tool_activity.reset(activity_token)

        text = (result.final_output or "").strip()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            raise ValueError("The agent workflow returned an empty answer.")

        usage = result.context_wrapper.usage
        return {
            "answer": "\n".join(lines[:3]),
            "session_id": result.last_response_id or "",
            "activity": activity,
            "model": OPENAI_MODEL,
            "usage": {
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
                "total_tokens": usage.total_tokens,
            },
        }

    async def close(self) -> None:
        """The Agents SDK manages model clients for each run."""
