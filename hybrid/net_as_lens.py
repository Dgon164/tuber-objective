"""
net_as_lens.py -- a net in front of Discovery.

A reservoir is a fixed, random, recurrent net.  It is never trained.  It
is driven by a signal and its state changes with every step.  Here the
reservoir is fed the bytes of a text, one byte per step, and after every
step the sign of each unit is written out as one bit.  The result is a
new signal: the net's view of the text.  Discovery then reads that new
signal exactly as it reads any other file.

    python net_as_lens.py ../examples/text/alice.txt

Writes  hybrid/alice.txt.reservoir   (the net's states, as bits)
        hybrid/alice.txt.reservoir.record.txt / .json   (Discovery's record of it)

Needs numpy for the net.  Discovery itself does not.
"""

import sys, os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import discovery

UNITS = 32          # one bit of output per unit; a 32-bit state per step
STEPS = 20000       # bytes of input fed through the net
SEED = 7


def run_reservoir(data, units=UNITS, seed=SEED):
    rng = np.random.default_rng(seed)
    W_in = rng.normal(0, 1.0, (units, 8))          # the byte comes in as 8 bits
    W = rng.normal(0, 1.0, (units, units))
    W *= 0.9 / max(abs(np.linalg.eigvals(W)))     # keep the loop from blowing up
    state = np.zeros(units)
    out = bytearray()
    for b in data:
        x = np.array([(b >> (7 - i)) & 1 for i in range(8)], dtype=float)
        state = np.tanh(W @ state + W_in @ x)
        bits = (state > 0).astype(np.uint8)
        out += np.packbits(bits).tobytes()         # units/8 bytes per step
    return bytes(out)


def main(path):
    data = open(path, 'rb').read()[:STEPS]
    states = run_reservoir(data)
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            os.path.basename(path) + '.reservoir')
    open(out_path, 'wb').write(states)
    print('wrote %s: %d steps, %d bytes' % (os.path.basename(out_path), len(data), len(states)))
    discovery.discover(out_path, lens='raw', quiet=True)
    print(open(out_path + '.record.txt').read()[:6000])


if __name__ == '__main__':
    main(sys.argv[1])
