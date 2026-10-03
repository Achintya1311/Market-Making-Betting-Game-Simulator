# Deep-ML: Market-Making & Betting-Game Simulator — full spec

Source: https://www.deep-ml.com/projects/market-making-betting-game-simulator
Meta: Medium · Optimization · 14 steps · 70 pts total · 5 pts per step. Python, numpy.
Blurb: Build a market-making and betting-game simulator from the ground up: start with expected-value reasoning on dice and card games, then implement a quoting engine that trades against an informed counterparty while managing inventory, adverse selection, and P&L across many episodes.
Scaffold: one combined file `market-making-betting-game-simulator · scaffold.py`; each solved step fills in its function. Starter stubs in `scaffold.py` here.

Parts
- Part 1 Expected Value & Betting Games (001-004): EV computations and optimal stopping on dice/card games that mirror later quoting logic.
- Part 2 Core Market-Making Mechanics (005-007): fair value → bid/ask, execute counterparty trades, mark cash+inventory to market.
- Part 3 Risk-Aware Quoting & Belief Updates (008-012): adverse selection, uncertainty, inventory skew, fair-value updates from trades and revealed cards.
- Part 4 Episode Simulation & Evaluation (013-014): full episodes, aggregate P&L stats.

Every step page has: Description, Learn (Why / Concept / Approach / Tools / Pitfall), Example, Starter code.

---

## 001 expected_value
Implement `expected_value(values, probabilities)`: expected value of a discrete distribution from paired values and probabilities. Inputs 1D array-likes, same length, probabilities sum to 1. Return a single Python float.
Why: every later decision (reroll, keep drawing, is a quote profitable) reduces to comparing expected values.
Concept: E[X] = Σ v_i p_i. Caller supplies a valid distribution (p_i ≥ 0, sum 1).
Approach: arrays (or zip); multiply element-wise, sum; cast to Python float. One-liner: `float(np.sum(np.asarray(values) * np.asarray(probabilities)))`.
Tools: np.asarray(x, dtype=float); a*b; np.sum or (a*b).sum(); float(); np.dot alternative.
Pitfall: returning numpy scalar/0-d array breaks equality checks and JSON dumps. Do NOT renormalize probabilities.
Example:
```
>>> expected_value([1, 2, 3, 4, 5, 6], [1/6]*6)
3.5
>>> expected_value([10, -5], [0.2, 0.8])
-2.0
```

## 002 one_reroll_die_value
Implement `one_reroll_die_value(sides)`. Fair die faces 1..sides pays face value. After first roll keep, or discard and reroll exactly once (must take second roll). Return expected winnings under optimal policy and sorted list of first-roll faces on which policy rerolls. Must call `expected_value` at least once.
Return: `{'value': float, 'reroll_faces': [int,...]}`
Why: simplest optional-stopping problem; same compare-now-vs-alternative reasoning returns when quoter decides whether to update fair value.
Concept: μ = E[reroll] = (n+1)/2. Keep f if f ≥ μ else reroll. Payout max(f, μ). V = (1/n) Σ_{f=1}^n max(f, μ). Reroll faces = f < μ.
Approach: faces 1..n; μ via expected_value with probs 1/n; average max(f, μ) via expected_value; reroll set = faces strictly < μ as sorted Python ints.
Tools: expected_value; np.arange(1, n+1); np.maximum(faces, mu); `int(f)` so output prints `[1, 2, 3]` not `[np.int64(1), ...]`.
Pitfall: keep/reroll tie rule. Convention: reroll strictly when f < μ, so a face exactly equal to μ is kept. A face can equal μ=(n+1)/2 only when n is odd (μ is then an integer). For even n, μ is a half-integer and no face ties. (The original page text garbles this; this wording is the resolved rule.)
Example:
```
>>> one_reroll_die_value(2)
{'value': 1.75, 'reroll_faces': [1]}
>>> one_reroll_die_value(6)
{'value': 4.25, 'reroll_faces': [1, 2, 3]}
```

## 003 pay_per_reroll_die_game
Implement `pay_per_reroll_die_game(sides, reroll_cost)`. Roll fair die 1..sides; keep face value or pay `reroll_cost` and roll again, unlimited times. Return `{'threshold': int, 'value': float}`: keep any roll ≥ threshold, reroll otherwise; value = expected net winnings from start. Ties in value → smallest threshold.
Why: "take now vs pay and retry" is the market-maker trade-off; derives an optimal stopping rule used later for hold-inventory vs requote.
Concept: threshold policy. p_keep = (N−t+1)/N, p_re = (t−1)/N. V_t = p_keep·E[r|r≥t] + p_re·(V_t − c). Solve: V_t = (t+N)/2 − ((t−1)/(N−t+1))·c, since E[r|r≥t] = (t+N)/2.
Approach: loop t = 1..N (t = N+1 means never keep, diverges when c>0); closed form each t; track max V_t and smallest t achieving it; return value as plain float.
Tools: plain Python; range(1, sides+1); replace best only on strictly larger value so smallest tying t wins.
Pitfall: reroll pays cost every time and returns to same decision. Use V_t = p_keep·E[r|keep] + p_re(V_t − c), NOT V_t = p_keep·E[r|keep] − p_re·c. Solve for V_t before comparing.
Example:
```
>>> pay_per_reroll_die_game(6, 1.0)
{'threshold': 3, 'value': 4.0}
>>> pay_per_reroll_die_game(6, 0.0)
{'threshold': 6, 'value': 6.0}
```

## 004 red_black_card_game_value
Implement `red_black_card_game_value(num_red, num_black)`. Face-down deck; red pays +1, black −1; may stop any time (including immediately, payout 0). Return `{'value': float, 'stop_now': bool}`: expected payout under optimal play and whether optimal first action is stop. Ties (continuation == 0) → stop.
Why: classic optimal stopping; same logic as keep quoting vs step aside.
Concept: V(r,b) = expected ADDITIONAL payout, running score sunk. V(r,b) = max(0, r/(r+b)·(1+V(r−1,b)) + b/(r+b)·(−1+V(r,b−1))). Boundaries V(0,0)=0, V(0,b)=0, V(r,0)=r.
Approach: helper V(r,b); lru_cache or bottom-up 2D table over r+b; for initial state compute RAW continuation `cont` (before outer max with 0); value = max(0.0, cont); stop_now = (cont <= 0.0).
Tools: functools.lru_cache(maxsize=None); plain floats; max(0.0, cont).
Pitfall: expected payout ≠ running score; stopping is worth 0 additional. r=0, b>0 → stop_now True.
Example:
```
>>> red_black_card_game_value(1, 1)
{'value': 0.5, 'stop_now': False}
>>> red_black_card_game_value(0, 3)
{'value': 0.0, 'stop_now': True}
```

## 005 make_quotes
Implement `make_quotes(fair_value, spread_width)`: symmetric two-sided quote. Return `{'bid','ask'}`, each offset by half the total spread. spread_width is TOTAL distance, not half-spread. Width 0 → bid = ask = fair.
Why: market maker always willing to buy (bid) and sell (ask); later steps assume this primitive.
Concept: bid = F − w/2, ask = F + w/2; ask − bid = w; midpoint = F.
Approach: half = spread_width/2; bid = F−half; ask = F+half; exact keys.
Tools: plain arithmetic; dict literal (execute_trade reads keys by name).
Pitfall: treating spread_width as half-spread (skipping /2) doubles distance, ruins P&L.
Example:
```
>>> make_quotes(100.0, 2.0)
{'bid': 99.0, 'ask': 101.0}
>>> make_quotes(50.0, 0.0)
{'bid': 50.0, 'ask': 50.0}
```

## 006 execute_trade
Implement `execute_trade(state, side, bid, ask, size=1)`. State dict keys 'cash','inventory'. side=='buy': counterparty buys from you at your ask. side=='sell': counterparty sells to you at your bid. Return a NEW dict with updated cash and inventory; do not mutate input.
Why: bookkeeping for fills; signs are foundation for P&L.
Concept (you are the market maker; counterparty perspective is mirror image):
- Counterparty 'buy' at ask: you SELL size units. cash += size*ask; inventory −= size (shorter).
- Counterparty 'sell' at bid: you BUY size units. cash −= size*bid; inventory += size (longer).
Inventory can be negative; cash and inventory are floats.
Approach: read state; branch on side; return `{'cash': new_cash, 'inventory': new_inv}`.
Tools: arithmetic, dict literal; no numpy.
Pitfall: sign backwards. Counterparty BUYS → YOU sell → inventory DOWN, cash UP. Think from your own book's perspective first.
Example:
```
>>> execute_trade({'cash': 0.0, 'inventory': 0.0}, 'buy', 99.5, 100.5, size=1)
{'cash': 100.5, 'inventory': -1.0}
>>> execute_trade({'cash': 0.0, 'inventory': 0.0}, 'sell', 99.5, 100.5, size=2)
{'cash': -199.0, 'inventory': 2.0}
```

## 007 mark_to_market_pnl
Implement `mark_to_market_pnl(cash, inventory, settlement_value)`: total P&L of the book at settlement. Leftover inventory valued at settlement (true) value and added to cash. Long gains from high settlement; short gains from low settlement.
Why: raw cash hides inventory risk; at episode end reference price is revealed true value.
Concept: PnL = cash + inventory · settlement_value. Sign conventions: buy 1 at p → cash −p, inv +1; sell 1 at p → cash +p, inv −1. Bought 1 at 4, settle 5 → −4+5 = 1. Sold 1 at 4, settle 5 → 4−5 = −1.
Approach: `return cash + inventory * settlement_value`. No clamp, no abs; negative P&L is legitimate.
Tools: plain arithmetic, scalars.
Pitfall: abs(inventory)*settlement or subtracting. Straight sum; cash and inventory carry their signs.
Example:
```
>>> mark_to_market_pnl(10.0, 2.0, 5.0)
20.0
>>> mark_to_market_pnl(0.0, -3.0, 4.0)
-12.0
```

## 008 adverse_selection_loss
Implement `adverse_selection_loss(fair_value, bid, ask, informed_values, informed_probabilities)`: expected loss to an informed counterparty. Return E[(v−ask)·1{v>ask}] + E[(bid−v)·1{v<bid}] over informed_values weighted by informed_probabilities. Non-negative float.
Why: informed traders pick the mispriced side; this measures the hidden cost so spreads can widen.
Concept: informed trader knows v. Lifts ask when v>ask (earns v−ask); hits bid when v<bid (earns bid−v); no trade if bid ≤ v ≤ ask. L = Σ p_i max(v_i−ask, 0) + Σ p_i max(bid−v_i, 0).
Approach: numpy arrays; ask-side excess max(v−ask,0), bid-side excess max(bid−v,0); weight by p_i; sum; float. `fair_value` is part of shared API but unused in this formula.
Tools: np.asarray(x, dtype=float); np.maximum(a, 0.0) (elementwise); np.sum(a*p) or np.dot; float().
Pitfall: builtin max does not broadcast. Both terms are losses (non-negative); do not subtract one from the other.
Example:
```
>>> vals = [98.0, 100.0, 102.0]
>>> probs = [1/3, 1/3, 1/3]
>>> round(adverse_selection_loss(100.0, 99.0, 101.0, vals, probs), 4)
0.6667
```
Starter begins with `import numpy as np`.

## 009 uncertainty_spread
Implement `uncertainty_spread(base_spread, uncertainty)`: spread width ≥ base_spread, strictly larger when uncertainty is strictly larger. Non-negative float inputs; single float out. Mapping of uncertainty → extra width is your choice.
Why: wide spread is buffer against being wrong; fuzzier belief → wider quote or get picked off.
Concept: base_spread is a floor (still earn something per round trip); uncertainty e.g. std of belief distribution. Need S ≥ base_spread always; u1<u2 ⇒ S(u1)<S(u2).
Approach: PINNED FORMULA (owner decision, not open-ended): `S = base_spread + 1.0 * uncertainty`, i.e. linear with k = 1. Return it as a float. Do not use other forms. (Original page allowed any monotone map; pinned so runs are reproducible.)
Tools: arithmetic; max(a,b) to enforce floor defensively.
Pitfall: returning base_spread regardless of uncertainty breaks growth property; do not decrease with uncertainty (e.g. dividing).
Example:
```
>>> uncertainty_spread(1.0, 0.0) >= 1.0
True
>>> uncertainty_spread(1.0, 2.0) > uncertainty_spread(1.0, 0.5)
True
```
Starter has docstring `"""Return a spread width >= base_spread that grows with uncertainty."""`.

## 010 inventory_skewed_quotes
Implement `inventory_skewed_quotes(fair_value, spread_width, inventory, skew_strength)` → `{'bid','ask'}` shaped around fair_value, shifted to lean against inventory. Long (inv>0): shift DOWN (lower ask attracts buyers, offload). Short (inv<0): shift UP. Shift scales with inventory and skew_strength; zero of either → symmetric quote.
Why: continued two-sided trading builds inventory; tilt quotes so market pushes trades that shrink the position.
Concept: symmetric bid = F − s/2, ask = F + s/2. Shifted: mid' = F − κ·q; bid = mid' − s/2; ask = mid' + s/2. q>0 ⇒ mid'<F; q<0 ⇒ quote rises.
Approach: half = s/2; shift = κ·q; mid' = F − shift; return {'bid': mid'−half, 'ask': mid'+half}. Any monotonic odd function of inventory (linear, tanh-scaled) valid if sign right.
Tools: float arithmetic; dict literal.
Pitfall: sign flip (adding κq) amplifies risk. On long inventory, midpoint must drop below fair_value.
Example:
```
>>> inventory_skewed_quotes(100.0, 2.0, 0.0, 0.5)
{'bid': 99.0, 'ask': 101.0}
>>> q = inventory_skewed_quotes(100.0, 2.0, 4.0, 0.5)
>>> (q['bid'] + q['ask']) / 2 < 100.0
True
```

## 011 update_fair_value_from_trade
Implement `update_fair_value_from_trade(fair_value, side, bid, ask, adjustment)` → new fair value after a counterparty trade. Counterparty buys at ask ⇒ estimate moves UP; sells at bid ⇒ DOWN. `adjustment` ≥ 0 sets strength; adjustment=0 ⇒ unchanged.
Why: ignoring who trades with you gets you run over by informed flow; a lifted ask is weak evidence true value is higher.
Concept: F_new = F + sign(side)·step(adjustment, bid, ask); sign +1 for buy, −1 for sell; step grows with adjustment and scales with spread. adjustment==0 ⇒ F_new = F.
Approach: half_spread = (ask−bid)/2 (or full spread, any proportional); 'buy' → + adjustment·half_spread; 'sell' → − it; return float.
Tools: float arithmetic; simple if side == 'buy' branch.
Pitfall: reversed sign. `side` is the COUNTERPARTY's action; their paying the ask is bullish for fair value.
Example:
```
>>> update_fair_value_from_trade(100.0, 'buy', 99.0, 101.0, 0.0)
100.0
>>> up = update_fair_value_from_trade(100.0, 'buy', 99.0, 101.0, 0.5)
>>> up > 100.0
True
>>> down = update_fair_value_from_trade(100.0, 'sell', 99.0, 101.0, 0.5)
>>> down < 100.0
True
```

## 012 update_remaining_card_value
Implement `update_remaining_card_value(remaining_counts, revealed_value)`: dict value→count of face-down cards BEFORE reveal, plus revealed value. Decrement that count (drop entry at zero), recompute mean of uniformly drawn card. Return `{'remaining_counts': dict, 'expected_value': float}`; empty deck ⇒ expected_value 0.0. Reuse `expected_value`.
Why: fair value of a bet on next draw depends on which cards remain; this is the belief update for the quoter.
Concept: deck as multiset {v_i: n_i}; E[V] = Σ (n_i/N) v_i, N = Σ n_i. Reveal v_r: n_r −= 1; remove key at 0; recompute. N=0 ⇒ 0.0.
Approach: copy dict (no mutation); decrement; delete if ≤0; N = sum(values); if N==0 → 0.0 else lists of values and probs n_i/N → expected_value; return dict.
Tools: dict(remaining_counts); del d[key]; sum(d.values()); expected_value.
Pitfall: leaving zero-count keys (e.g. {1.0: 0, −1.0: 2}) — mean fine but downstream treats 1.0 as still possible. Prune.
Example:
```
>>> res = update_remaining_card_value({1.0: 2, -1.0: 2}, 1.0)
>>> res['remaining_counts']
{1.0: 1, -1.0: 2}
>>> round(res['expected_value'], 4)
-0.3333
```

## 013 run_market_making_episode
Implement `run_market_making_episode(true_value, counterparty_sides, initial_fair_value, config)`: one full episode. For each side: quote from current fair value, uncertainty, inventory; execute counterparty trade; update fair-value belief; next round. After final round settle at true_value and report P&L. Output dict keys: 'pnl','cash','inventory','fair_value','history' (history = one dict per round with keys 'bid','ask','side','cash','inventory','fair_value'). Reuse make_quotes / uncertainty_spread / inventory_skewed_quotes / execute_trade / update_fair_value_from_trade / mark_to_market_pnl. Config keys 'base_spread','uncertainty','skew_strength','belief_adjustment'. RESOLVED RULE: every missing key defaults to 0, including 'base_spread' (use `config.get(key, 0.0)`). The original page's Tools list showed `config.get('base_spread', 1.0)`; that example is overridden by this rule. A missing 'base_spread' therefore gives a zero-width quote.
Why: wires every block into one loop: quote, trade, learn, requote; only final P&L matters.
Concept: hidden true_value revealed at settlement. Start: initial_fair_value belief, cash 0, inventory 0. Per side: spread from uncertainty; (fair, spread, inventory) → skewed (bid, ask); execute (buy hits ask → short one; sell hits bid → long one); update belief toward trade. End: PnL = cash + inventory·true_value.
Approach pseudocode:
```
cash, inv, fv = 0.0, 0.0, initial_fair_value
for side in counterparty_sides:
    sw = uncertainty_spread(base_spread, uncertainty)
    q  = inventory_skewed_quotes(fv, sw, inv, skew_strength)
    st = execute_trade({'cash': cash, 'inventory': inv}, side, q['bid'], q['ask'])
    cash, inv = st['cash'], st['inventory']
    fv = update_fair_value_from_trade(fv, side, q['bid'], q['ask'], belief_adjustment)
    history.append({...})
pnl = mark_to_market_pnl(cash, inv, true_value)
```
Use config.get(key, default). Keep running cash/inventory/fair_value; append snapshot each iteration; do NOT reimplement helpers.
Pitfall: quote using inventory BEFORE this round's trade, then execute, then update belief. Skewing on post-trade inventory or updating belief before executing changes numbers.
Example:
```
>>> cfg = {'base_spread': 2.0, 'uncertainty': 0.0, 'skew_strength': 0.0, 'belief_adjustment': 0.0}
>>> res = run_market_making_episode(100.0, ['buy', 'sell'], 100.0, cfg)
>>> res['cash'], res['inventory'], res['pnl']
(2.0, 0.0, 2.0)
>>> len(res['history'])
2
```

## 014 summarize_episode_pnls
Implement `summarize_episode_pnls(pnls)` → `{'mean': float, 'std': float (population, ddof=0), 'worst': float (min)}`. Input any 1D array-like of floats.
Why: one episode is noisy; evaluate a strategy on the distribution over many episodes.
Concept: mean μ = (1/n)Σx_i (edge); population std σ = sqrt((1/n)Σ(x_i−μ)²) (volatility); worst = min x_i (tail-risk proxy / drawdown).
Approach: np.asarray(pnls, dtype=float); compute three stats; cast each to float; pack in dict.
Tools: arr.mean(); arr.std() (default ddof=0, which is wanted); arr.min(); float().
Pitfall: np.std defaults ddof=0 (population) vs statistics.stdev ddof=1 (sample). Use ddof=0.
Example:
```
>>> summarize_episode_pnls([1.0, 2.0, 3.0, 4.0])
{'mean': 2.5, 'std': 1.118033988749895, 'worst': 1.0}
>>> summarize_episode_pnls([-5.0, 0.0, 5.0])
{'mean': 0.0, 'std': 4.08248290463863, 'worst': -5.0}
```

---

## Property checks (REQUIRED in every step's tests, in addition to the page examples)

Added by owner because the original grader's hidden tests are not available. Each step's test file must assert the properties below with plain `assert` loops over a fixed grid of inputs (no new dependencies, no randomness; if random inputs are used, seed them with `np.random.default_rng(0)`).

- 001: EV of a uniform die over 1..n is (n+1)/2. EV of a constant distribution equals the constant. Linearity: E[aX+b] = a·E[X] + b. Return type is `float`.
- 002: value ≥ (n+1)/2 and ≤ n. Every reroll face < (n+1)/2. List is sorted and holds Python `int`. sides=1 gives value 1.0 and `[]`. Value equals brute-force average of max(f, (n+1)/2).
- 003: cost 0 gives threshold = sides and value = sides. Threshold in 1..sides. Value is non-increasing as cost rises. Value ≥ (sides+1)/2 (threshold 1 is always available). Result matches a brute-force scan over all thresholds with the smallest-tie rule.
- 004: value ≥ 0. (r,0) with r>0 gives value r and stop_now False. (0,b) gives 0.0 and True. Value ≤ num_red. Value is non-decreasing in num_red and non-increasing in num_black.
- 005: (bid+ask)/2 == fair_value. ask − bid == spread_width. bid ≤ ask. Width 0 gives bid == ask == fair.
- 006: Input dict is not mutated. A buy then a sell of equal size at the same quotes returns inventory to start and raises cash by size·(ask−bid). Inventory change is −size for 'buy' and +size for 'sell'.
- 007: inventory 0 gives pnl == cash. P&L is linear in settlement_value. A buy-then-sell round trip of equal size has P&L size·(ask−bid) for every settlement value.
- 008: result ≥ 0. Result is 0.0 when every informed value lies in [bid, ask]. A point mass at v > ask gives exactly v − ask; at v < bid gives exactly bid − v. Narrowing the quotes never lowers the loss.
- 009: result == base_spread + uncertainty (pinned formula). Result ≥ base_spread. Strictly increasing in uncertainty. Returns `float`.
- 010: inventory 0 or skew 0 gives the symmetric quote. ask − bid == spread_width for every inventory. Midpoint equals fair_value − skew_strength·inventory exactly and is strictly decreasing in inventory when skew_strength > 0.
- 011: adjustment 0 returns fair_value unchanged. 'buy' then 'sell' with the same quotes and adjustment returns the original fair_value. Result is strictly monotone in adjustment (up for 'buy', down for 'sell').
- 012: Total count falls by exactly 1. Input dict is not mutated. No zero-count keys remain. expected_value lies within [min, max] of remaining keys. Revealing every card in turn ends with `{}` and 0.0.
- 013: history length == len(counterparty_sides). Final cash and inventory equal the last history entry. With unit size, inventory == (#sells − #buys). pnl == mark_to_market_pnl(cash, inventory, true_value). Empty sides gives pnl 0.0 and empty history. With uncertainty, skew and belief_adjustment all 0, an equal number of buys and sells gives inventory 0. A missing config key behaves exactly as 0.0.
- 014: min ≤ mean ≤ max. std ≥ 0. A constant series gives std 0.0 and worst equal to the constant. worst ≤ mean. Adding a constant c shifts mean and worst by c and leaves std unchanged. Scaling by k>0 scales all three by k. All three values are Python `float`.

---

## Not scraped
Hidden test cases, Run/Submit grader, "Ask deep-0" AI assistant, reference solutions. Step pages loaded without login (Premium badge shown on site header).
