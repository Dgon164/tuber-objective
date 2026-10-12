"""
flips.py -- one row per 100 ms on the shared clock: the vehicle's 13 fields and the last value seen on each of the
channels the computer used (in the order they first appeared in the quiet flight, then any new ones) -- then the
row_by_row step: which fields changed from the row before.  Each flip-row is one word; Discovery reads the
sequence of flip-rows.  Nothing says which field is a jet or a rate; that is the lens afterwards."""
import struct, collections, sys
# python flips.py RUNS_DIR HELD_RUN QUIET_RUN   -> held-flips.bin, quiet-flips.bin, fields.txt in the current folder
A=sys.argv[1].rstrip('/')+'/'
runs={'held':sys.argv[2],'quiet':sys.argv[3]}
VEH=['ax','ay','az','wx','wy','wz','alt','vx','vz','thrust','jets5','jets6','cdu_sent','pipa_sent']
# channel order: fixed list of every channel seen in either flight, sorted, so columns line up
chans=set()
for r in runs.values():
    d=open(A+r+'/channels.bin','rb').read()
    for i in range(0,len(d),8):
        b=d[i+4:i+8]; chans.add((b[0]<<3)|((b[1]>>3)&7))
chans=sorted(chans)
FIELDS=VEH+[f'ch{c:03o}' for c in chans]
print('fields',len(FIELDS),FIELDS)
# vehicle time -> cycle: both clocks start at 0; the kick is at vehicle t=340.0 s and the first CDU pulse is at
# cycle 31956856, so cycles per vehicle second = 31956856/340
CPV=31956856/340.0
for name,r in runs.items():
    d=open(A+r+'/channels.bin','rb').read()
    pk=[]
    for i in range(0,len(d),8):
        cyc=struct.unpack('>I',d[i:i+4])[0]; b=d[i+4:i+8]
        pk.append((cyc,(b[0]<<3)|((b[1]>>3)&7),((b[1]&7)<<12)|((b[2]&0x3f)<<6)|(b[3]&0x3f)))
    pk.sort()
    v=open(A+r+'/vehicle.bin','rb').read()
    rows=[]; last={c:0 for c in chans}; j=0
    for i in range(0,len(v),28):
        f=struct.unpack('>HhhhhhhHhhHBBHH',v[i:i+28]); t10=f[0]
        if not (3300<=t10<4300): continue
        cyc_end=(t10+1)/10.0*CPV
        while j<len(pk) and pk[j][0]<cyc_end:
            last[pk[j][1]]=pk[j][2]; j+=1
        rows.append(list(f[1:])+[last[c] for c in chans])
    # flips: field changed from the row before -> one bit per field, packed big-endian into 5 bytes (40 bits)
    out=bytearray(); nbits=len(FIELDS)
    for a,b in zip(rows,rows[1:]):
        bits=0
        for k in range(nbits):
            if a[k]!=b[k]: bits|=1<<(nbits-1-k)
        out+=bits.to_bytes(5,'big') if nbits<=40 else bits.to_bytes((nbits+7)//8,'big')
    open(f'{name}-flips.bin','wb').write(out); print(name,'flip rows',len(rows)-1,'bytes per row',len(out)//(len(rows)-1))
open('fields.txt','w').write('\n'.join(FIELDS))
