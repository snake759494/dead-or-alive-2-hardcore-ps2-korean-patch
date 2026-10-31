"""기술명 ↔ 캐릭터 글자표 대응. 글자표 = 0x425000~0x427000 행 포인터 목록(캐릭터 14명)."""
import struct,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import extract
e=extract.e;VA=extract.VA
G0,G1=0x46d3b8,0x46e230
atl=[]  # (list file offset, [row offsets])
i=0x425000
while i<0x427000:
    v=struct.unpack_from('<I',e,i)[0]-VA
    if G0<=v<G1:
        rows=[]
        while True:
            w=struct.unpack_from('<I',e,i)[0]-VA
            if not(G0<=w<G1): break
            rows.append(w);i+=4
        atl.append((i-4*len(rows),rows))
    i+=4
def glyphs(rows):
    s=''
    for r in reversed(rows): s+=extract.dec(r)
    return s
ATL=[glyphs(r) for _,r in atl]
moves=[(o,rf,t) for o,rf,t in extract.out if (0x467460<=o<G0) or o>=0x47f000]
def owner(t):
    return [k for k,g in enumerate(ATL) if all(c in g for c in t if c not in ' ')]
if __name__=='__main__':
    for k,(a,r) in enumerate(atl): print(k,hex(a),len(r),len(ATL[k]),ATL[k])
    import collections;c=collections.Counter()
    for o,rf,t in moves:
        ow=owner(t);c[tuple(ow)]+=1
    for k,v in sorted(c.items(),key=lambda x:-x[1])[:30]: print(k,v)
def assign():
    """포인터 위치 순으로 기술을 훑어 글자표가 연속으로 맞는 구간을 캐릭터로 지정."""
    items=[]
    for o,rf,t in moves:
        for p in rf:
            if 0x421000<=p<0x426100 or 0x441000<=p<0x443000: items.append((p,o,t))
    items.sort()
    res={};cur=None;seg=[]
    segs=[]
    for p,o,t in items:
        ow=set(owner(t))
        if cur is None or not (cur&ow):
            if seg: segs.append((cur,seg))
            cur=ow;seg=[]
        else: cur=cur&ow
        seg.append((p,o,t))
    segs.append((cur,seg))
    return segs
