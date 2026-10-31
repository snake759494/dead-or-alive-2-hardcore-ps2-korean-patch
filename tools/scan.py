import re,struct,collections,sys
e=open('tmp/SLPS_250.26','rb').read()
def va(o): return o+0x1ff000
LEAD=set(range(0x81,0xa0))|set(range(0xe0,0xf0))
def dec(s):
    i=0;out=[]
    while i<len(s):
        b=s[i]
        if b in LEAD:
            if i+1>=len(s):return None
            try: out.append(s[i:i+2].decode('cp932'))
            except: return None
            i+=2
        elif 0x20<=b<0x7f or b==10: out.append(chr(b));i+=1
        else: return None
    return ''.join(out)
res=[]
for m in re.finditer(rb'[^\x00]+\x00',e[0x228000:0x480000]):
    o=m.start()+0x228000;s=m.group()[:-1]
    if o<0x42c000: continue
    t=dec(s)
    if not t or not re.search('[ぁ-ヶ一-龠]',t): continue
    if len(re.findall('[ぁ-ヶ一-龠ー]',t))<2: continue
    j=m.end()+0x228000
    while j<len(e) and e[j]==0: j+=1
    res.append((o,len(s),j-o,t))
ptr=collections.Counter()
pv=set(va(r[0]) for r in res)
for i in range(0,len(e)-3,4):
    v=struct.unpack_from('<I',e,i)[0]
    if v in pv: ptr[v]+=1
with open('tmp/strings.tsv','w',encoding='utf-8') as f:
    for o,l,cap,t in res: f.write('%06x\t%d\t%d\t%d\t%s\n'%(o,l,cap,ptr[va(o)],t.replace('\n','\n')))
print(len(res),sum(1 for r in res if ptr[va(r[0])]))
