"""Deep-ML Market-Making & Betting-Game Simulator: combined scaffold (14 steps).

Starter stubs scraped verbatim from the step editors. See SPEC.md for instructions.
Source: https://www.deep-ml.com/projects/market-making-betting-game-simulator
"""
import numpy as np
from functools import lru_cache


# ── Step 001  expected_value ──
def expected_value(values, probabilities):
    v = np.asarray(values, dtype=float)
    p = np.asarray(probabilities, dtype=float)
    return float(np.sum(v * p))


# ── Step 002  one_reroll_die_value ──
def one_reroll_die_value(sides):
    n = sides
    faces = np.arange(1, n + 1)
    mu = expected_value(faces, [1.0 / n] * n)
    payouts = np.maximum(faces, mu)
    value = expected_value(payouts, [1.0 / n] * n)
    reroll_faces = sorted(int(f) for f in faces if f < mu)
    return {'value': value, 'reroll_faces': reroll_faces}


# ── Step 003  pay_per_reroll_die_game ──
def pay_per_reroll_die_game(sides, reroll_cost):
    n = sides
    best_t, best_v = 1, None
    for t in range(1, n + 1):
        v = (t + n) / 2.0 - ((t - 1) / (n - t + 1)) * reroll_cost
        if best_v is None or v > best_v:
            best_v = v
            best_t = t
    return {'threshold': int(best_t), 'value': float(best_v)}


# ── Step 004  red_black_card_game_value ──
def red_black_card_game_value(num_red, num_black):
    @lru_cache(maxsize=None)
    def V(r, b):
        if r == 0:
            return 0.0
        if b == 0:
            return float(r)
        red_term = (r / (r + b)) * (1.0 + V(r - 1, b))
        black_term = (b / (r + b)) * (-1.0 + V(r, b - 1))
        return max(0.0, red_term + black_term)

    r, b = num_red, num_black
    if r + b == 0 or r == 0:
        cont = 0.0
    elif b == 0:
        cont = float(r)
    else:
        red_term = (r / (r + b)) * (1.0 + V(r - 1, b))
        black_term = (b / (r + b)) * (-1.0 + V(r, b - 1))
        cont = red_term + black_term
    value = max(0.0, cont)
    stop_now = cont <= 0.0
    return {'value': value, 'stop_now': stop_now}


# ── Step 005  make_quotes ──
def make_quotes(fair_value, spread_width):
    half = spread_width / 2.0
    return {'bid': fair_value - half, 'ask': fair_value + half}


# ── Step 006  execute_trade ──
def execute_trade(state, side, bid, ask, size=1):
    cash = state['cash']
    inventory = state['inventory']
    if side == 'buy':
        cash = cash + size * ask
        inventory = inventory - size
    else:
        cash = cash - size * bid
        inventory = inventory + size
    return {'cash': float(cash), 'inventory': float(inventory)}


# ── Step 007  mark_to_market_pnl ──
def mark_to_market_pnl(cash, inventory, settlement_value):
    return cash + inventory * settlement_value


# ── Step 008  adverse_selection_loss ──
def adverse_selection_loss(fair_value, bid, ask, informed_values, informed_probabilities):
    v = np.asarray(informed_values, dtype=float)
    p = np.asarray(informed_probabilities, dtype=float)
    ask_side = np.maximum(v - ask, 0.0)
    bid_side = np.maximum(bid - v, 0.0)
    return float(np.sum(p * (ask_side + bid_side)))


# ── Step 009  uncertainty_spread ──
def uncertainty_spread(base_spread, uncertainty):
    """Return a spread width >= base_spread that grows with uncertainty."""
    return float(max(base_spread, base_spread + 1.0 * uncertainty))


# ── Step 010  inventory_skewed_quotes ──
def inventory_skewed_quotes(fair_value, spread_width, inventory, skew_strength):
    half = spread_width / 2.0
    shift = skew_strength * inventory
    mid = fair_value - shift
    return {'bid': mid - half, 'ask': mid + half}


# ── Step 011  update_fair_value_from_trade ──
def update_fair_value_from_trade(fair_value, side, bid, ask, adjustment):
    half_spread = (ask - bid) / 2.0
    if side == 'buy':
        return float(fair_value + adjustment * half_spread)
    else:
        return float(fair_value - adjustment * half_spread)


# ── Step 012  update_remaining_card_value ──
def update_remaining_card_value(remaining_counts, revealed_value):
    counts = dict(remaining_counts)
    counts[revealed_value] = counts.get(revealed_value, 0) - 1
    if counts[revealed_value] <= 0:
        del counts[revealed_value]

    total = sum(counts.values())
    if total == 0:
        ev = 0.0
    else:
        values = list(counts.keys())
        probs = [n / total for n in counts.values()]
        ev = expected_value(values, probs)
    return {'remaining_counts': counts, 'expected_value': ev}


# ── Step 013  run_market_making_episode ──
def run_market_making_episode(true_value, counterparty_sides, initial_fair_value, config):
    base_spread = config.get('base_spread', 0.0)
    uncertainty = config.get('uncertainty', 0.0)
    skew_strength = config.get('skew_strength', 0.0)
    belief_adjustment = config.get('belief_adjustment', 0.0)

    cash, inventory, fair_value = 0.0, 0.0, initial_fair_value
    history = []
    for side in counterparty_sides:
        spread_width = uncertainty_spread(base_spread, uncertainty)
        quotes = inventory_skewed_quotes(fair_value, spread_width, inventory, skew_strength)
        state = execute_trade({'cash': cash, 'inventory': inventory}, side, quotes['bid'], quotes['ask'])
        cash, inventory = state['cash'], state['inventory']
        fair_value = update_fair_value_from_trade(fair_value, side, quotes['bid'], quotes['ask'], belief_adjustment)
        history.append({
            'bid': quotes['bid'],
            'ask': quotes['ask'],
            'side': side,
            'cash': cash,
            'inventory': inventory,
            'fair_value': fair_value,
        })

    pnl = mark_to_market_pnl(cash, inventory, true_value)
    return {
        'pnl': pnl,
        'cash': cash,
        'inventory': inventory,
        'fair_value': fair_value,
        'history': history,
    }


# ── Step 014  summarize_episode_pnls ──
def summarize_episode_pnls(pnls):
    # TODO: return a dict with keys 'mean', 'std' (ddof=0), and 'worst' for the given P&L sequence.
    pass
