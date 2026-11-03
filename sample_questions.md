# Cricket Agent: Sample Questions and Expected Tool Paths

Use these prompts to explore the agent workflow. The example answers are illustrative; model wording may vary. Every factual answer should pass through the **Cricket Answer Reviewer** before the coordinator returns it.

> **Demo data note:** Asha Sharma, Dev Patel, and Maya Khan are synthetic sample profiles, not real player records. The rules lookup contains only a few short summaries, not a complete cricket rulebook. The app has no live scores.

| # | Sample question | Example answer | Expected agent and tool path |
|---:|---|---|---|
| 1 | What is LBW? | A batter may be out LBW if a non-no-ball delivery hits their person and would have hit the stumps, subject to the other LBW conditions. | Coordinator → `rules_research` → `search_cricket_rules` → `review_answer` |
| 2 | What is a wide ball? | A wide is a delivery too far from the striker to hit with a normal stroke, subject to the playing conditions. It adds an extra and is not a legal delivery. | Coordinator → `rules_research` → `search_cricket_rules` → `review_answer` |
| 3 | What is a no-ball? | A no-ball is called for certain delivery infringements. It adds an extra and does not count as a legal delivery. | Coordinator → `rules_research` → `search_cricket_rules` → `review_answer` |
| 4 | How does a Super Over work? | In competitions that use one, each side gets one over. The side with the higher Super Over score wins, subject to that competition’s tie-break rules. | Coordinator → `rules_research` → `search_cricket_rules` → `review_answer` |
| 5 | Does a wide count as a legal delivery? | No. The bundled rules summary says a wide adds an extra and does not count as a legal delivery. | Coordinator → `rules_research` → `search_cricket_rules` → `review_answer` |
| 6 | How many extras does the wide add according to the rules data? | The sample rules summary says a wide adds one extra to the batting side. | Coordinator → `rules_research` → `search_cricket_rules` → `review_answer` |
| 7 | What are examples of reasons a bowler might be called for a no-ball? | The sample summary mentions an illegal delivery stride or an unfair delivery. It is not a complete list of no-ball conditions. | Coordinator → `rules_research` → `search_cricket_rules` → `review_answer` |
| 8 | What happens if the Super Over is tied? | Further tie-break rules depend on the competition’s playing conditions. The local summary does not specify those details. | Coordinator → `rules_research` → `search_cricket_rules` → `review_answer` |
| 9 | How many matches and runs are in Asha Sharma’s demo profile? | Asha Sharma’s synthetic T20 demo profile lists 12 matches and 286 runs. | Coordinator → `stats_research` → `lookup_player_stats` → `review_answer` |
| 10 | What is Asha Sharma’s strike rate in the demo data? | Her sample strike rate is 144.44 runs per 100 balls (286 runs from 198 balls). These are synthetic figures. | Coordinator → `stats_research` → `lookup_player_stats` → `calculate_strike_rate` → `review_answer` |
| 11 | What is Dev Patel’s strike rate in the demo data? | His sample strike rate is 155.48 runs per 100 balls (241 runs from 155 balls). These are synthetic figures. | Coordinator → `stats_research` → `lookup_player_stats` → `calculate_strike_rate` → `review_answer` |
| 12 | What is Maya Khan’s strike rate in the demo data? | Her sample strike rate is 141.15 runs per 100 balls (319 runs from 226 balls). These are synthetic figures. | Coordinator → `stats_research` → `lookup_player_stats` → `calculate_strike_rate` → `review_answer` |
| 13 | Compare Asha Sharma and Dev Patel by T20 demo strike rate. | Dev’s sample strike rate is 155.48; Asha’s is 144.44. The profiles are synthetic demo data. | Coordinator → `stats_research` → two `lookup_player_stats` calls → two `calculate_strike_rate` calls → `review_answer` |
| 14 | What is Virat Kohli’s strike rate in your demo dataset? | Virat Kohli is not listed in this synthetic demo dataset, so the app cannot calculate a demo strike rate for him. | Coordinator → `stats_research` → `lookup_player_stats` → `review_answer` |
| 15 | What run rate is needed to score 45 runs in the next 30 balls? | The required rate is 9.00 runs per over. | Coordinator → `stats_research` → `calculate_required_run_rate` → `review_answer` |
| 16 | We need 30 runs from 24 balls. What is the required run rate? | The required rate is 7.50 runs per over. | Coordinator → `stats_research` → `calculate_required_run_rate` → `review_answer` |
| 17 | We need 120 runs from 60 balls. What is the required run rate? | The required rate is 12.00 runs per over. | Coordinator → `stats_research` → `calculate_required_run_rate` → `review_answer` |
| 18 | What is Asha’s demo strike rate, and how does a Super Over work? | Asha’s synthetic sample strike rate is 144.44. A Super Over gives each side one over when the competition’s rules call for that tie-break. | Coordinator → `stats_research` → player lookup + strike-rate calculation; `rules_research` → `search_cricket_rules` → `review_answer` |
| 19 | Can a batter be out LBW if the ball would not have hit the stumps? | The sample LBW summary says the ball must have been going on to hit the stumps, along with the other LBW conditions. | Coordinator → `rules_research` → `search_cricket_rules` → `review_answer` |
| 20 | Does this rules dataset explain DRS? | DRS is not covered in the local rules summaries, so the app should say it cannot answer from this dataset. | Coordinator → `rules_research` → `search_cricket_rules` (no match) → `review_answer` |

## Tool reference

- `search_cricket_rules` searches the local rules summaries.
- `lookup_player_stats` looks up one synthetic demo player profile.
- `calculate_strike_rate` calculates runs per 100 balls.
- `calculate_required_run_rate` calculates required runs per over from runs and balls remaining.
- The coordinator calls specialists as tools; the reviewer is also exposed as a coordinator tool.
