"""Run from MyCricketAgent: python -m uvicorn backend.apihandling:app --port 8000"""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Any

from fastapi import Body, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    RateLimitError,
)
from pydantic import BaseModel, Field, StringConstraints

from .cricketagnet import CricketAgent

Question = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]
SessionID = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


class ChatRequest(BaseModel):
    question: Question
    session_id: SessionID | None = None


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    activity: list[str] = Field(default_factory=list)
    model: str
    usage: dict[str, int]


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.agent = CricketAgent()
    try:
        yield
    finally:
        await app.state.agent.close()


app = FastAPI(title="Cricket Conversational Agent", version="1.0.0", lifespan=lifespan)


@app.get("/", include_in_schema=False)
async def frontend() -> FileResponse:
    """Serve the simple chat UI from the same origin as the API."""
    return FileResponse(
        Path(__file__).parent.parent / "frontend" / "index.html",
        headers={"Cache-Control": "no-store"},
    )


@app.get("/health")
async def health() -> dict[str, str]:
    """Process liveness only; this does not call OpenAI."""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(
    payload: Annotated[ChatRequest | None, Body()] = None,
    question: Annotated[Question | None, Query()] = None,
    session_id: Annotated[SessionID | None, Query()] = None,
) -> dict[str, Any]:
    """Send question as JSON or a query parameter; reuse the latest session_id."""
    if payload is not None and (question is not None or session_id is not None):
        raise HTTPException(422, "Use either JSON or query parameters, not both.")
    if payload is None:
        if question is None:
            raise HTTPException(422, "The question parameter is required.")
        payload = ChatRequest(question=question, session_id=session_id)

    try:
        return await app.state.agent.answer(payload.question, payload.session_id)
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc
    except AuthenticationError as exc:
        raise HTTPException(503, "The configured OpenAI API key was rejected.") from exc
    except RateLimitError as exc:
        raise HTTPException(429, "OpenAI rate limit or quota reached. Try again later.") from exc
    except APITimeoutError as exc:
        raise HTTPException(504, "OpenAI timed out. Try again.") from exc
    except APIConnectionError as exc:
        raise HTTPException(502, "Unable to connect to OpenAI.") from exc
    except BadRequestError as exc:
        raise HTTPException(400, "OpenAI rejected the request. Check the question and session_id.") from exc
    except (APIStatusError, ValueError) as exc:
        raise HTTPException(502, "Unable to generate an answer from OpenAI.") from exc
