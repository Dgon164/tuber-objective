"""
goalB.py -- the goal row against what the vehicle's own record ever showed.

    python goalB.py RUN_DIR

The goal row (a given, in the vehicle's own fields): on the ground, and
still -- altitude 0, each turn rate under 0.5 deg/s, vertical speed under
5 m/s, horizontal speed under 5 m/s. The reader says, field by field,
whether the machine ever saw it, and whether the whole row was ever seen
together. No score: seen or not seen.
"""
import struct, sys, collections
GOAL = {'alt': lambda r: r['alt'] == 0, 'rates': lambda r: max(abs(r['wx']), abs(r['wy']), abs(r['wz'])) < 0.5,
        'vz': lambda r: abs(r['vz']) < 5, 'vx': lambda r: abs(r['vx']) < 5}
d = open(sys.argv[1].rstrip('/') + '/vehicle.bin', 'rb').read()
rows = []
for i in range(0, len(d) - 27, 28):
    f = struct.unpack('>HhhhhhhHhhHBBHH', d[i:i + 28])
    rows.append(dict(t=f[0] / 10, wx=f[4] / 1e4, wy=f[5] / 1e4, wz=f[6] / 1e4, alt=f[7], vx=f[8] / 10, vz=f[9] / 10,
                     thrust=f[10], jets5=f[11], jets6=f[12], engine=f[14]))
print(f"{len(rows)} vehicle rows, {rows[-1]['t']:.0f} s of machine time")
ever = {k: [r['t'] for r in rows if g(r)] for k, g in GOAL.items()}
for k, ts in ever.items():
    print(f"  {k:6s} satisfied in {len(ts):5d} rows" + (f"  (first at {ts[0]:.1f} s)" if ts else "  -- NEVER"))
whole = [r for r in rows if all(g(r) for g in GOAL.values())]
print(f"  the whole row: {'seen at %.1f s' % whole[0]['t'] if whole else 'NEVER seen together'}")
# what changed and what never did, over the whole run: the comparator on first row vs every row
first = rows[0]
moved = {k for r in rows for k in ('wx', 'wy', 'wz', 'alt', 'vx', 'vz', 'thrust', 'jets5', 'jets6', 'engine') if r[k] != first[k]}
print(f"  fields that ever changed: {sorted(moved)};  never changed: {sorted(set(first) - moved - {'t'})}")
g = [r for r in rows if r['alt'] == 0]
if g:
    print(f"  at the first altitude-0 row: vz = {g[0]['vz']:.1f} m/s, vx = {g[0]['vx']:.1f} m/s -- altitude 0 arrived by falling, not by landing")
