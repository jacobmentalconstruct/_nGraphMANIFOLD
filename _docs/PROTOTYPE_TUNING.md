# Prototype Tuning And Scoring

_Status: Seed-search tuning candidate ready_

This document records the first post-prototype tuning harness. It is subordinate
to `builder_constraint_contract.md`.

## Purpose

The tuning harness evaluates whether the completed prototype spine is useful to
a builder or agent.

It does this by running repeatable builder-task fixtures through:

```text
source content
  -> semantic objects
  -> relation enrichment
  -> cartridge persistence
  -> traversal
  -> execution report
  -> MCP usefulness scoring
```

## Runtime Owner

- `src/core/coordination/prototype_scoring.py`
- `src/core/coordination/builder_task_scoring.py`
- `src/core/coordination/history_inspector.py`
- `src/core/coordination/seed_search.py`

This is a local evaluation harness, not a network adapter or MCP server.

## Default Fixtures

- `relation_evidence_trace`
- `execution_report_trace`
- `persistence_round_trip`

Each fixture uses a temporary semantic cartridge during tests and scoring.

## Current Scores

Acceptance threshold: `0.7`

| Fixture | Score | Accepted |
| --- | ---: | --- |
| `relation_evidence_trace` | `0.91` | yes |
| `execution_report_trace` | `0.91` | yes |
| `persistence_round_trip` | `0.91` | yes |

The current recommendation is to expose or adapt:

- `analysis.traverse_cartridge`

## Real Builder-Task Scores

Real project-document scoring now runs through:

```bat
python -m src.app mcp-score-tasks --dump-json
```

Current real-project score:

| Run | Score | Accepted |
| --- | ---: | --- |
| real project docs | `0.93` | yes |

Current real tasks:

- `current_tranche_lookup`
- `mcp_surface_lookup`
- `strangler_next_work_lookup`
- `operator_command_lookup`

The history-aware inspector now summarizes recent calls and keeps raw JSON:

```bat
python -m src.app mcp-history-view
```

Seed search can now select traversal seeds before calling the registered tool:

```bat
python -m src.app mcp-search-seeds --query "Current Park Point" --dump-json
```

## Interpretation

The seam is now tunable and scoreable through local code and real project docs.
It is still not a full MCP protocol server. The next architectural pressure is
scoring whether search-selected traversal seeds improve task fit,
actionability, and friction reduction against the existing builder tasks.

## Next Scoring Work

- Score traversal search and seed selection against the real builder tasks.
- Track whether search improves task-fit and actionability scores.
- Keep the history-aware inspector attached to every scoring run.
- Decide whether better search is enough or a second registered tool is needed.
