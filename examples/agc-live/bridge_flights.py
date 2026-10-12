"""
bridge_flights.py -- two flights, same window: what is in one record and not the other.

    python bridge_flights.py WINDOW_DIR names.txt

WINDOW_DIR holds held-writes.bin, quiet-writes.bin (10-byte records, clock stripped),
and the Discovery records for held-/quiet-channels.bin run with --frame 32.
Set operations on the words, same as examples/german/bridge.py. The names file is
a lens: it is read only to print names next to the numbers the comparator found.
"""
import json, bisect, collections, sys, re, os
os.chdir(sys.argv[1]); N=sys.argv[2]
eras=collections.defaultdict(list); fixed=[]
for line in open(N):
    p=line.split()
    if len(p)<3: continue
    idx=int(p[1],8)
    if p[2]=='fixed': fixed.append((idx,p[0]))
    elif p[2] in ('erasable','equals') and idx<4096: eras[idx].append(p[0])
fixed.sort(); fidx=[i for i,_ in fixed]
def routine(ia):
    k=bisect.bisect_right(fidx,ia)-1
    return fixed[k][1] if k>=0 and ia-fidx[k]<200 else '?'
def cell(ea): return '/'.join(eras.get(ea,['?'])[:2])

def load(name):
    j=json.load(open(name)); L=j['levels'][0]
    return {int(k):v for k,v in L['words'].items()}, L['parts'], L['runs'], j['frame']

def bridge(sig, suffix=''):
    hw,hp,hr,fr=load(f'held-{sig}.bin{suffix}.record.json'); qw,qp,qr,_=load(f'quiet-{sig}.bin{suffix}.record.json')
    only_h=set(hw)-set(qw); only_q=set(qw)-set(hw); both=set(hw)&set(qw)
    ph=set(hp); pq=set(qp)
    print(f"\n==== {sig}: words  held {len(hw)}  quiet {len(qw)}  shared {len(both)}  only-held {len(only_h)}  only-quiet {len(only_q)}")
    print(f"     parts  held {len(ph)}  quiet {len(pq)}  shared {len(ph&pq)}  only-held {len(ph-pq)}  only-quiet {len(pq-ph)}")
    return hw,qw,only_h,only_q,both,hp,qp,fr

# ---- writes: the words table straight from the binary (same table Discovery writes; the JSON is 4 GB)
import struct
def words_from_bin(path):
    d=open(path,'rb').read(); c=collections.Counter()
    for i in range(0,len(d)-9,10): c[int.from_bytes(d[i:i+10],'big')]+=1
    return c
hw=words_from_bin('held-writes.bin'); qw=words_from_bin('quiet-writes.bin')
oh=set(hw)-set(qw); oq=set(qw)-set(hw); both=set(hw)&set(qw)
print(f"\n==== writes: words  held {len(hw)}  quiet {len(qw)}  shared {len(both)}  only-held {len(oh)}  only-quiet {len(oq)}")
import subprocess
for f in ('held','quiet'):
    t=open(f'{f}-writes.bin.record.txt').read()
    m=re.search(r'PARTS BY DENSITY[^\n]*\n', t); print('    ',f, m.group(0).strip() if m else '')
def dec(w): return ((w>>64)&0xffff,(w>>48)&0xffff,(w>>32)&0xffff,(w>>16)&0xffff,w&0xffff)
cells=collections.Counter(); routs=collections.Counter(); cellsq=collections.Counter()
for w in oh:
    ia,iw,ea,o,n=dec(w); cells[ea]+=hw[w]; routs[routine(ia)]+=hw[w]
for w in both:
    ia,iw,ea,o,n=dec(w); cellsq[ea]+=1
print("\n  cells written ONLY in the held flight (by number of such writes), with the names lens:")
for ea,n in cells.most_common(30): print(f"    {ea:04o} {cell(ea):18s} {n:7d}")
print("\n  routines (nearest label at or below the instruction address) doing writes seen ONLY in the held flight:")
for r,n in routs.most_common(30): print(f"    {r:12s} {n:7d}")
print("\n  cells written ONLY in the quiet flight:")
cq=collections.Counter()
for w in oq:
    ia,iw,ea,o,n=dec(w); cq[ea]+=qw[w]
for ea,n in cq.most_common(10): print(f"    {ea:04o} {cell(ea):18s} {n:7d}")

# ---- channels (whole packets)
hw,qw,oh,oq,both,hp,qp,fr=bridge('channels','.frame32')
def chdec(w):
    b=[(w>>24)&255,(w>>16)&255,(w>>8)&255,w&255]
    return ((b[0]<<3)|((b[1]>>3)&7), ((b[1]&7)<<12)|((b[2]&0x3f)<<6)|(b[3]&0x3f))
ch=collections.Counter(); chv=collections.defaultdict(collections.Counter)
for w in oh:
    c,v=chdec(w); ch[c]+=hw[w]; chv[c][v]+=hw[w]
print("\n  channel packets seen ONLY in the held flight, by channel (count of packets), and their most common values:")
for c,n in ch.most_common(): print(f"    {c:03o}  {n:6d}   values: "+' '.join(f'{v:05o}x{k}' for v,k in chv[c].most_common(4)))
chq=collections.Counter()
for w in oq:
    c,v=chdec(w); chq[c]+=qw[w]
print("  channel packets seen ONLY in the quiet flight, by channel:", ' '.join(f'{c:03o}:{n}' for c,n in chq.most_common()))
chb=collections.Counter()
for w in both:
    c,v=chdec(w); chb[c]+=1
print("  channels with packets in BOTH:", ' '.join(f'{c:03o}:{n}' for c,n in chb.most_common()))
