"""Genetic algorithm with greedy repair (port of kp_algo_ga_main.m)."""
from __future__ import annotations

import numpy as np

from ...helpers.rng import lcg, seed_state


def kp_algo_ga_main(v, w, C, acfg, seed, mark=None) -> tuple[list[int], dict]:
    """Generational GA, bit-string chromosomes, one elite kept per generation.

    Repair of every chromosome (start, child): while overweight drop the taken item with the lowest
    v/w, then add, in decreasing v/w, every item that still fits. All children are feasible, so the
    fitness is the packing value. Parent selection: tournament of `tournament` random individuals
    (best value wins, first drawn on ties); uniform crossover with probability `crossover_rate`
    (otherwise the child copies the first parent); each bit flips with probability
    `mutation_factor / n`. Each child uses ONE call of the portable LCG: 2 * tournament selection
    draws, 1 crossover draw, n mask draws, n mutation draws (all drawn even if unused).
    """
    v = np.asarray(v, float)
    w = np.asarray(w, float)
    n = v.size
    vl, wl = v.tolist(), w.tolist()
    asc = np.argsort(-(v / w), kind="stable").tolist()   # decreasing ratio
    drop_order = asc[::-1]
    size, gens, tour = acfg["pop_size"], acfg["generations"], acfg["tournament"]
    cross, mrate = acfg["crossover_rate"], acfg["mutation_factor"] / n
    state = seed_state(seed)

    def repair(x):
        W = sum(wl[i] for i in range(n) if x[i])
        if W > C:
            for i in drop_order:
                if x[i]:
                    x[i] = 0
                    W -= wl[i]
                    if W <= C:
                        break
        for i in asc:
            if not x[i] and W + wl[i] <= C:
                x[i] = 1
                W += wl[i]
        return sum(vl[i] for i in range(n) if x[i])

    pop, fit = [], []
    u, state = lcg(state, size * n)
    for k in range(size):
        x = [1 if ui < 0.5 else 0 for ui in u[k * n:(k + 1) * n]]
        fit.append(repair(x))
        pop.append(x)
    evaluations = size
    best = int(np.argmax(fit))
    best_x, best_v = pop[best][:], fit[best]
    for _ in range(gens):
        new_pop, new_fit = [pop[best][:]], [fit[best]]       # elite
        while len(new_pop) < size:
            u, state = lcg(state, 2 * tour + 1 + 2 * n)
            parents = []
            for p in range(2):
                cand = [min(int(ui * size), size - 1) for ui in u[p * tour:(p + 1) * tour]]
                win = cand[0]
                for c in cand[1:]:
                    if fit[c] > fit[win]:
                        win = c
                parents.append(win)
            a, b = pop[parents[0]], pop[parents[1]]
            off = 2 * tour
            if u[off] < cross:
                mask = u[off + 1:off + 1 + n]
                x = [a[i] if mask[i] < 0.5 else b[i] for i in range(n)]
            else:
                x = a[:]
            mut = u[off + 1 + n:]
            for i in range(n):
                if mut[i] < mrate:
                    x[i] ^= 1
            new_fit.append(repair(x))
            new_pop.append(x)
            evaluations += 1
        pop, fit = new_pop, new_fit
        best = int(np.argmax(fit))
        if fit[best] > best_v:
            best_x, best_v = pop[best][:], fit[best]
    items = [i + 1 for i in range(n) if best_x[i]]
    info = {"evaluations": evaluations, "generations": gens,
            "working_memory_bytes": int(v.nbytes + w.nbytes + 2 * size * n)}
    return items, info
