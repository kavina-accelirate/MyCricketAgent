"""Deterministic local cricket tools for the multi-agent demo."""

import json
import re
from pathlib import Path

from agents import function_tool

from .activity import record_tool

DATA_DIR = Path(__file__).parent.parent / "data"


def _load_json(name: str):
    with (DATA_DIR / name).open(encoding="utf-8") as data_file:
        return json.load(data_file)


@function_tool
def search_cricket_rules(query: str) -> str:
    """Find relevant rule summaries in the local cricket rules dataset."""
    record_tool("search_cricket_rules")
    rules = _load_json("rules.json")
    terms = set(re.findall(r"[a-z0-9]+", query.lower()))
    ranked = []
    for rule in rules:
        searchable = " ".join([rule["name"], rule["summary"], *rule["keywords"]]).lower()
        searchable_terms = set(re.findall(r"[a-z0-9]+", searchable))
        score = len(terms & searchable_terms)
        if score:
            ranked.append((score, rule))
    ranked.sort(key=lambda item: item[0], reverse=True)
    matches = [rule for _, rule in ranked[:3]]
    return json.dumps({"found": bool(matches), "matches": matches}, ensure_ascii=False)


@function_tool
def lookup_player_stats(player: str) -> str:
    """Look up a player in the bundled synthetic T20 demo dataset."""
    record_tool("lookup_player_stats")
    records = _load_json("sample_player_stats.json")
    normalized = re.sub(r"[^a-z0-9]", "", player.lower())
    for record in records:
        aliases = [record["name"], *record["aliases"]]
        if any(re.sub(r"[^a-z0-9]", "", alias.lower()) == normalized for alias in aliases):
            return json.dumps({"found": True, "source": "synthetic demo data", "player": record}, ensure_ascii=False)
    return json.dumps({"found": False, "source": "synthetic demo data", "requested_player": player})


@function_tool
def calculate_strike_rate(runs: int, balls: int) -> str:
    """Calculate batting strike rate as runs per 100 balls."""
    record_tool("calculate_strike_rate")
    if runs < 0 or balls <= 0:
        return json.dumps({"error": "runs must be nonnegative and balls must be greater than zero"})
    return json.dumps({"runs": runs, "balls": balls, "strike_rate": round(runs * 100 / balls, 2)})


@function_tool
def calculate_required_run_rate(runs_needed: int, balls_remaining: int) -> str:
    """Calculate required runs per over from runs and balls remaining."""
    record_tool("calculate_required_run_rate")
    if runs_needed < 0 or balls_remaining <= 0:
        return json.dumps({"error": "runs_needed must be nonnegative and balls_remaining must be greater than zero"})
    return json.dumps({
        "runs_needed": runs_needed,
        "balls_remaining": balls_remaining,
        "required_run_rate": round(runs_needed * 6 / balls_remaining, 2),
    })
