# Progress

The routine owns this file. It ticks a step only after the step's code is in `scaffold.py`, its tests in `tests/` pass, and the work is committed.

## Part 1: Expected Value & Betting Games
- [x] 001 expected_value
- [x] 002 one_reroll_die_value
- [x] 003 pay_per_reroll_die_game
- [x] 004 red_black_card_game_value

## Part 2: Core Market-Making Mechanics
- [x] 005 make_quotes
- [x] 006 execute_trade
- [x] 007 mark_to_market_pnl

## Part 3: Risk-Aware Quoting & Belief Updates
- [x] 008 adverse_selection_loss
- [ ] 009 uncertainty_spread
- [ ] 010 inventory_skewed_quotes
- [ ] 011 update_fair_value_from_trade
- [ ] 012 update_remaining_card_value

## Part 4: Episode Simulation & Evaluation
- [ ] 013 run_market_making_episode
- [ ] 014 summarize_episode_pnls

## Run log
(one line per routine run: steps done, tests passed, anything blocked)
- 2026-10-03 UTC: implemented steps 001 (expected_value), 002 (one_reroll_die_value); pytest 12 passed; nothing blocked.
- 2026-10-03 UTC: implemented steps 003 (pay_per_reroll_die_game), 004 (red_black_card_game_value); pytest 27 passed; nothing blocked.
- 2026-10-03 UTC: implemented steps 005 (make_quotes), 006 (execute_trade); pytest 36 passed; nothing blocked.
- 2026-10-03 UTC: implemented steps 007 (mark_to_market_pnl), 008 (adverse_selection_loss); pytest 49 passed; nothing blocked.

## Improvement ideas (not implemented, awaiting owner approval)
(routine appends observations here; it never acts on them)
- SPEC.md 002's pitfall note says "A face can equal μ=(n+1)/2 only when n is odd" but never states what the property-check grid should do for sides=0 or negative sides; scaffold has no guard and relies on callers passing sides>=1. Worth an explicit note in SPEC.md that sides is a positive integer.
- SPEC.md 003 never states the sides=0 edge case; `range(1, sides+1)` is empty there so the natural closed-form loop has no threshold to pick and would need an explicit guard. Same gap as 002's sides=0/negative note. Worth pinning sides>=1 as a precondition across all die-game steps.
- SPEC.md 004's boundary list gives V(0,0)=0, V(0,b)=0, V(r,0)=r but never states what `red_black_card_game_value(0, 0)` itself should return at the top level (an empty deck with nothing to draw). The implementation treats it as value 0.0, stop_now True by extension of the V(0,b) boundary, but this case isn't in the Example or Property-checks sections, so it's unverified against any reference behavior.
- SPEC.md 006 never states what `execute_trade` should do for a `side` value other than `'buy'`/`'sell'` (typo, `None`, etc.) or for `size <= 0`; the implementation treats anything not equal to `'buy'` as a sell, which is silent and could mask a caller bug. Worth pinning either an explicit `ValueError` on an unrecognized `side` or stating the "anything else is sell" fallback as intentional.
- SPEC.md 007's property-check list (unlike 001/002/014) never requires a Python `float` return type. `cash + inventory * settlement_value` returns whatever type those inputs are, so int-typed cash/inventory/settlement_value (plausible if a caller forwards raw ints) would silently return an `int` instead of `float`. Worth pinning an explicit `float(...)` cast and adding it to the property-check list for consistency with the other numeric steps.
- SPEC.md 008 never states whether `informed_probabilities` must sum to 1, unlike step 001 which explicitly guarantees this and forbids renormalizing. `adverse_selection_loss` is a weighted sum rather than a true expectation if weights don't sum to 1 (e.g. raw trade-arrival rates instead of a normalized distribution); worth pinning the same "caller guarantees a valid distribution, do not renormalize" convention as 001 for consistency.
