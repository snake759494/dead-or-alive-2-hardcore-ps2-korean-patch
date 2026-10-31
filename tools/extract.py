"""ELF 일본어 문자열 추출(포인터 기준). translation/ja.tsv: addr  refs  text"""
import re,struct,sys,os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
e=open(os.path.join(R,'tmp','SLPS_250.26'),'rb').read()
VA=0x1ff000; LO,HI=0x42c000,0x480000
LEAD=set(range(0x81,0xa0))|set(range(0xe0,0xf0))
def dec(o):
    i=o;out=[]
    while e[i]:
        b=e[i]
        if b in LEAD:
            try: out.append(e[i:i+2].decode('cp932'))
            except: return None
            i+=2
        elif 0x20<=b<0x7f or b==10: out.append(chr(b));i+=1
        else: return None
    return ''.join(out)
def isja(t): return bool(t) and len(re.findall('[ぁ-ヶ一-龠ー々]',t))>=1 and not re.search('[a-z]{2}',t)  and not re.search('[ｦ-ﾟ]',t)
refs={}
for i in range(0x1000,len(e)-3,4):
    v=struct.unpack_from('<I',e,i)[0]-VA
    if LO<=v<HI: refs.setdefault(v,[]).append(i)
out=[]
for t0 in sorted(refs):
    t=dec(t0)
    if isja(t) and not 0x45be00<=t0<0x45c100 and not re.fullmatch(r'.[A-Za-z]',t): out.append((t0,refs[t0],t))
# 포인터 없는 고정 슬롯
for o in [o for o in range(0x42c800,0x42d500) if e[o-1]==0 and e[o]]+[0x475aa8,0x475ac0,0x475ae0,0x475af8]:
    t=dec(o)
    if isja(t) and o not in refs: out.append((o,[],t))
out.sort()
if __name__=='__main__':
    with open(os.path.join(R,'translation','ja.tsv'),'w',encoding='utf-8',newline='\n') as f:
        for o,rf,t in out: f.write('%06x\t%d\t%s\n'%(o,len(rf),t.replace(chr(10),chr(92)+'n')))
    print(len(out))
