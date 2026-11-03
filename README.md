# Cricket agent workflow demo

Requires Python 3.10+. The backend uses FastAPI and the OpenAI Agents SDK. The page in
`frontend/index.html` is served by the same FastAPI app.

## Run

From the project folder:

```powershell
python -m pip install -r requirements.txt
```

Put your OpenAI API key in the project-root `.env` file as `OPENAI_API_KEY=your-key`.
The `.env` file is ignored by Git. You can alternatively set `$env:OPENAI_API_KEY = "your-key"`.
The default model is `gpt-4.1-mini`; override with `OPENAI_MODEL` if needed.

```powershell
python -m uvicorn backend.apihandling:app --reload --port 8000
```

Open the chat at http://localhost:8000. Interactive Swagger docs are at
http://localhost:8000/docs. `GET /health` checks process liveness only.

## Agent workflow

The coordinator can call three specialist agents: a rules specialist, a stats analyst,
and an answer reviewer. The rules and stats specialists have local function tools.
The stats analyst can look up sample profiles and calculate strike rates or required
run rates. The reviewer checks factual answers against gathered evidence.

The sample player profiles in `backend/data/sample_player_stats.json` are synthetic
and are only intended to demonstrate tool calls. Rule summaries in
`backend/data/rules.json` are a small demo subset, not a complete rules reference.
There is no live score or web search tool.

Try questions like:

- `What is LBW?`
- `What is Asha Sharma's strike rate in the demo data?`
- `Compare Asha Sharma and Dev Patel by T20 demo strike rate.`
- `What is Virat Kohli's strike rate in your demo dataset?`

`evals/cricket_workflow_cases.json` is optional starter input for your AcceliQA evaluation;
the app does not run evaluations locally. The Agents SDK also records traces for model
and tool activity.

## Ask a question

`POST /chat` accepts a `question` query parameter:

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/chat?question=What%20is%20an%20LBW%3F"
```

Alternatively, send JSON:

```powershell
$reply = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/chat" -ContentType "application/json" -Body '{"question":"What is an LBW?"}'
$reply
```

Example response (the exact answer varies):

```json
{"answer":"LBW means leg before wicket: a batter may be out if their body blocks a ball that would hit the stumps, subject to the LBW rules.","session_id":"resp_..."}
```

For follow-ups, pass the **latest returned** `session_id` with the next question:

```powershell
$body = @{ question = "Can it happen when the ball pitches outside leg stump?"; session_id = $reply.session_id } | ConvertTo-Json
$reply = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/chat" -ContentType "application/json" -Body $body
```

Omit `session_id` to start a new conversation. It is the preceding OpenAI response
ID, not a fixed session identifier. Conversation context uses OpenAI's stored
responses, so no local session database is required. Do not mix JSON and query
parameters in one request.

The agent instructions request 1-3 short lines (at most 60 words); the backend caps
output at three nonempty newline-delimited lines. Visual wrapping depends on the client.

Validation errors return 422; missing/rejected credentials return 503; upstream
limits return 429; upstream timeouts return 504; connection/model failures return
502. An upstream rejected request returns 400. Error details do not expose keys.

This demo service has no inbound authentication; real answers require a valid API key
and model access.

OpenAI integration reference: [Conversation state](https://developers.openai.com/api/docs/guides/conversation-state).
