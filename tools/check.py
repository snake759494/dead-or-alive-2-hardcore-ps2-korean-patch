"""번역 검사: 누락, 기술표 글자표 예산(원래 행 수×16)."""
import sys,os,glob,re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import extract,moves
R=extract.R
SKIP={0x457e65,0x467661,0x46d021,0x47c6c0,0x47c7a8,0x47d068}
def load():
    ko={}
    for f in sorted(glob.glob(os.path.join(R,'translation','ko_*.tsv'))):
        for l in open(f,encoding='utf-8'):
            l=l.rstrip('\n')
            if not l: continue
            a,t=l.split('\t',1);ko[int(a,16)]=t.replace('\n','\n')
    return ko
def targets():
    return [(o,rf,t) for o,rf,t in extract.out if not(moves.G0<=o<moves.G1) and o not in SKIP]
if __name__=='__main__':
    ko=load();tg=targets()
    miss=[(o,t) for o,rf,t in tg if o not in ko];print('targets',len(tg),'missing',len(miss))
    for o,t in miss: print(' %06x %s'%(o,t))
    extra=set(ko)-set(o for o,_,_ in tg);print('extra',[hex(x) for x in extra])
    # 기술표 예산
    segs=moves.assign();per={}
    for cur,seg in segs:
        if len(cur)!=1: continue
        k=list(cur)[0]
        for p,o,t in seg: per.setdefault(k,set()).add(o)
    rows=[len(r) for _,r in moves.atl]
    for k in range(14):
        cs=set()
        for o in per.get(k,()): cs|=set(ko.get(o,''))
        cs-={' '}
        print('atlas',k,'rows',rows[k],'budget',rows[k]*16,'need',len(cs))
    allh=set(c for t in ko.values() for c in t if '가'<=c<='힣');print('hangul total',len(allh))
    sysh=set(c for o,t in ko.items() if not(0x467460<=o<moves.G0 or o>=0x47f000) for c in t if '가'<=c<='힣');print('system hangul',len(sysh))
