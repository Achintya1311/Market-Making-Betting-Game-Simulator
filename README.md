# Market-Making & Betting-Game Simulator

A market-making and betting-game simulator built step by step: expected-value reasoning on dice and card games, then a quoting engine that trades against an informed counterparty while managing inventory, adverse selection and P&L across many episodes.

- `SPEC.md`: the full 14-step specification (descriptions, concepts, approach, pitfalls, examples). The source of truth.
- `scaffold.py`: one module holding all 14 functions. Starts as stubs; steps are filled in order.
- `tests/`: one test file per step, built from that step's examples in `SPEC.md`.
- `PROGRESS.md`: step checklist, run log, and improvement ideas.

Run the tests with bare `pytest` from the repo root.

Pure Python plus numpy. No network, no keys, no spend.
