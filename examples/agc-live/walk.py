"""
walk.py -- from a goal, backward through the machine's own map, to the actions.

The loop wrote memory.pkl: the map `went` of (context, action, next context)
with counts, the contexts themselves, and the channel pool. A context is what
the machine showed (the set of values on each steady channel). A goal is
either a context (by its 4-hex-digit tag from the log) or a channel word
(CHANNEL:VALUE in octal) that should be showing.

The walk: start from every context that satisfies the goal; step backward
through `went` to the contexts that lead there and the actions that do it;
stop at the rest context (the one the machine shows with nothing pressed) or
when nothing leads further. Shortest path first. Prints the action sequence,
or where it stopped.

    python walk.py RUN_DIR ctx:6bdc
    python walk.py RUN_DIR word:010:60400
    python walk.py RUN_DIR map            (print the map as the machine has it)
"""
import pickle, sys, collections

M = pickle.load(open(sys.argv[1].rstrip("/") + "/memory.pkl", "rb"))
went, contexts = M['went'], M['contexts']
tag = lambda c: f"{hash(c) & 0xffff:04x}"

# the rest context: the one most often arrived at (the machine keeps going back to it)
arrivals = collections.Counter()
for (a, act, b), n in went.items():
    arrivals[b] += n
rest = arrivals.most_common(1)[0][0] if arrivals else ()


def satisfies(ctx, goal):
    kind, _, rest_ = goal.partition(':')
    if kind == 'ctx':
        return tag(ctx) == rest_
    if kind == 'word':
        ch, val = rest_.split(':')
        return any(k[0] == int(ch, 8) and v == int(val, 8) for k, v in ctx)
    return False


def walk(goal, max_depth=6):
    goals = [c for c in contexts.values() if satisfies(c, goal)]
    if not goals:
        return None, f"no context the machine has seen satisfies {goal}"
    # backward breadth-first: frontier of contexts, each with the action path that reaches the goal from it
    best = {}
    frontier = [(g, []) for g in goals]
    for g, _ in frontier:
        best[g] = []
    depth = 0
    while frontier and depth < max_depth:
        nxt = []
        for ctx, path in frontier:
            if ctx == rest:
                return path, f"reached the rest context in {len(path)} steps"
            for (a, act, b), n in went.items():
                if b == ctx and a not in best:
                    best[a] = [act] + path
                    nxt.append((a, [act] + path))
        frontier = nxt
        depth += 1
    if rest in best:
        return best[rest], 'reached rest'
    stop = sorted(best.items(), key=lambda kv: len(kv[1]))[:5]
    return None, 'stopped: nothing in the map leads from the rest context to ' + goal + '; nearest known starts: ' + \
        ', '.join(f"{tag(c)} ({len(p)} steps away)" for c, p in stop)


if __name__ == '__main__':
    goal = sys.argv[2] if len(sys.argv) > 2 else 'map'
    if goal == 'map':
        print(f"rest context {tag(rest)}; {len(contexts)} contexts seen; {len(went)} transitions")
        by_from = collections.defaultdict(list)
        for (a, act, b), n in sorted(went.items(), key=lambda kv: -kv[1]):
            by_from[a].append((act, b, n))
        for a, lst in sorted(by_from.items(), key=lambda kv: -sum(n for _, _, n in kv[1]))[:12]:
            print(f"  from {tag(a)}:")
            for act, b, n in lst[:40]:
                print(f"     {act[0]}{act[1]:>3} -> {tag(b)}  x{n}" + ('   (stays)' if a == b else ''))
    else:
        path, why = walk(goal)
        print(why)
        if path:
            print('press, from rest:', ' '.join(f"{a[0]}{a[1]}" for a in path))
