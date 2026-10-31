"""한글패치 빌드: ELF 텍스트·시스템 폰트·기술표 아틀라스를 패치 ISO에 기록.
패치 ISO가 없으면 원본을 복사한 뒤, 매번 원본 바이트로 다시 만든 영역을 통째로 덮어쓴다."""
import os,sys,struct,shutil
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import extract,check,moves,enc,glyph
from tgs import CHAR_PACKS,read,entries
from PIL import Image,ImageDraw,ImageFont
R=extract.R
ISO=os.path.join(R,'DOA2 - Hardcore (Japan) (En,Ja,Fr,De,Es,It).iso')
OUT=os.path.join(R,'DOA2 - Hardcore (Japan) (Korean).iso')
ELF_LBA,ELF_SIZE=1572714,4743236
ROMB=1575031*2048
VA=0x1ff000
SYSFONT=0x7767A80              # ROM_00 안 핸들 18 헤더 위치(RAM 0x948280)
SYS_RAM=0x948280               # 시스템 폰트 픽셀은 각 헤더 +0x70부터(GIF IMAGE 태그 뒤)
SYS_PAGES=[(0x9503c0-0x9503c0+0x948280,256,256),(0x9503c0,256,256)]+[(a,64,64) for a in (0x958500,0x958e40,0x959780,0x95a0c0)]
SYS_CODES=[(0x4c1658,256),(0x4c1860,256),(0x4c1a68,16),(0x4c1a90,16),(0x4c1ab8,16),(0x4c1ae0,16)]
NOTE_TABS=[0x426378,0x426418,0x4264e0,0x426590,0x426628,0x4266f0,0x4267b0,0x426870,0x426920,0x426a00,0x426ae0,0x426ba8,0x426c68,0x426cf8]
PACK_OF=[13,12,7,3,5,8,4,6,10,1,9,0,11,2]   # 캐릭터 목록 순서 → CHAR_PACKS 순서
LIST_TAB=0x426310                            # 캐릭터 ID별 행 목록 포인터(26개)
ROW0,ROW1=0x46d3b8,0x46e230                  # 행 문자열 영역
LST0,LST1=0x426128,0x426310                  # 행 포인터 목록 영역

def iso_read(off,n):
    with open(ISO,'rb') as f: f.seek(off);return f.read(n)

# ---------------- 텍스트 ----------------
def cap_of(e,o):
    L=e.index(b'\0',o)-o;z=o+L
    while z<len(e) and e[z]==0: z+=1
    lim=0x40 if 0x42c800<=o<0x42d500 else (o+L+1+7)//8*8-o
    return min(z-o,lim)

def place_text(e,ko,cm):
    """고정 슬롯은 제자리, 포인터 문자열은 원래 슬롯들을 이어 붙인 공간에 차례로 다시 채운다."""
    tg=[x for x in check.targets() if eval(os.environ.get('TFILT','True'),{'o':x[0]})];iv=[];items=[]
    for o,rf,t in tg:
        b=enc.encode(ko[o],cm)+b'\0';c=cap_of(e,o)
        e[o:o+c]=bytes(c)
        if not rf:
            if len(b)>c: raise SystemExit('고정 슬롯 초과 %06x %s'%(o,ko[o]))
            e[o:o+len(b)]=b
        else: iv.append([o,o+c]);items.append((o,rf,b))
    iv.sort();free=[]
    for a,b_ in iv:
        if free and free[-1][1]>=a: free[-1][1]=max(free[-1][1],b_)
        else: free.append([a,b_])
    for o,rf,b in items:
        for fr in free:
            a=(fr[0]+3)&~3
            if fr[1]-a>=len(b):
                e[a:a+len(b)]=b;fr[0]=a+len(b)
                for p in rf: struct.pack_into('<I',e,p,a+VA)
                break
        else: raise SystemExit('공간 부족 %06x'%o)
    print('텍스트 %d개, 구간 %d개, 남은 공간 %d'%(len(tg),len(free),sum(max(0,b-a) for a,b in free)))

# ---------------- 글리프 원본 ----------------
def orig_atlas_cells():
    """원본 아틀라스들의 글자→16×16 계조(0~15, 흰 글자=15)."""
    cells={}
    for k,(a,rows) in enumerate(moves.atl):
        d=read(CHAR_PACKS[PACK_OF[k]],0x10000);en=entries(d);do=en[2][1]
        for r,ro in enumerate(rows):
            for c,ch in enumerate(extract.dec(ro)):
                if ch in cells: continue
                px=[]
                for y in range(16):
                    for x in range(16):
                        X,Y=c*16+x,r*16+y;b=d[do+(Y*256+X)//2]
                        px.append(15-((b>>(4*(X&1)))&15))
                cells[ch]=px
    return cells

def orig_sys_cells(rom_sys):
    cells={}
    e0=bytes(iso_read(ELF_LBA*2048,ELF_SIZE))
    for (ca,n),(pa,w,h) in zip(SYS_CODES,SYS_PAGES):
        cols=w//16;base=pa-SYS_RAM+0x70
        for i,code in enumerate(struct.unpack_from('>%dH'%n,e0,ca-VA)):
            if not code: continue
            try: ch=bytes([code>>8,code&255]).decode('cp932')
            except: continue
            px=[]
            for y in range(16):
                for x in range(16):
                    X,Y=(i%cols)*16+x,(i//cols)*16+y;b=rom_sys[base+(Y*w+X)//2]
                    px.append((b>>(4*(X&1)))&15)
            cells.setdefault(ch,px)
    return cells

def put4(buf,w,X,Y,v):
    i=(Y*w+X)//2
    buf[i]=(buf[i]&0xf0)|v if X&1==0 else (buf[i]&0x0f)|(v<<4)

# ---------------- 시스템 폰트 ----------------
def build_sysfont(e,ko,cm,rom_sys):
    chars=set()
    for o,rf,t in check.targets():
        if moves.G0<=o<moves.G1 or 0x467460<=o<moves.G0 or o>=0x47f000: continue
        chars|=set(enc.TOK.sub('',enc.norm(ko[o])))
    chars-={chr(10),' '}
    sysc=orig_sys_cells(rom_sys)
    chars={c for c in chars if ord(c)>0x7f}|set('０１２３４５６７８９')   # 실행 중 끼워 넣는 숫자용
    code=lambda ch:struct.unpack('>H',cm[ch] if ch in cm else ch.encode('cp932'))[0]
    order=sorted(chars,key=code)   # 조회는 선형 탐색이라 순서 무관, 보기 좋게 코드순
    total=sum(n for _,n in SYS_CODES)
    if len(order)>total: raise SystemExit('시스템 폰트 초과 %d'%len(order))
    rom=bytearray(rom_sys);k=0
    for (ca,n),(pa,w,h) in zip(SYS_CODES,SYS_PAGES):
        cols=w//16;base=pa-SYS_RAM+0x70
        pg=bytearray(w*h//2)
        codes=[]
        for i in range(n):
            if k<len(order):
                ch=order[k];k+=1
                px=sysc[ch] if ch in sysc else glyph.cell(ch)
                code=cm[ch] if ch in cm else ch.encode('cp932')
                codes.append(struct.unpack('>H',code)[0])
                for j,v in enumerate(px): put4(pg,w,(i%cols)*16+j%16,(i//cols)*16+j//16,v)
            else: codes.append(0xffff)
        struct.pack_into('>%dH'%n,e,ca-VA,*codes)
        rom[base:base+len(pg)]=pg
    print('시스템 폰트 글자',len(order),'/',total)
    return bytes(rom)

# ---------------- 기술표 아틀라스 ----------------
NOTES=dict(l.rstrip('\n').split('\t') for l in open(os.path.join(R,'translation','notes.txt'),encoding='utf-8') if l.strip())
def note_img(txt,cond=False):
    f=ImageFont.truetype(glyph.GAL.replace('11.ttf','11-Condensed.ttf') if cond else glyph.GAL,12)
    w=int(f.getlength(txt))+2
    im=Image.new('L',(w,12),0);ImageDraw.Draw(im).text((1,0),txt,font=f,fill=255)
    return im

def char_moves(ko):
    starts=sorted((min(p for p,o,t in seg),list(cur)[0]) for cur,seg in moves.assign() if len(cur)==1)
    st={}
    for k in set(k for _,k in starts): st[k]=min(p for p,kk in starts if kk==k)
    order=sorted((p,k) for k,p in st.items())
    per={k:set() for k in range(14)}
    for o,rf,t in check.targets():
        if not(0x467460<=o<moves.G0 or o>=0x47f000): continue
        for p in rf:
            if 0x421000<=p<0x426100:
                own=[k for s,k in order if s<=p]
                if own: per[own[-1]].add(o)
    return per

def build_atlases(e,ko,cm,packs):
    acell=orig_atlas_cells();per=char_moves(ko)
    # 행 문자열/목록 영역 초기화
    e[ROW0:ROW1]=bytes(ROW1-ROW0);e[LST0:LST1]=bytes(LST1-LST0)
    rp=ROW0;lp=LST0;tabs=struct.unpack_from('<26I',e,LIST_TAB)
    for t in range(14):
        chars=set()
        for o in per[t]: chars|=set(enc.TOK.sub('',enc.norm(ko[o])))
        chars-={chr(0x3000),' '}
        order=sorted(c for c in chars if not '가'<=c<='힣')+sorted(c for c in chars if '가'<=c<='힣')
        nrows=(len(order)+15)//16
        img=bytearray([0xff]*0x8000)
        rows=[]
        for r in range(nrows):
            seg=order[r*16:r*16+16];b=b''
            for c,ch in enumerate(seg):
                b+=cm[ch] if ch in cm else ch.encode('cp932')
                px=acell[ch] if ch in acell else glyph.cell(ch)
                for j,v in enumerate(px): put4(img,256,c*16+j%16,r*16+j//16,15-v)
            if rp+len(b)+1>ROW1: raise SystemExit('행 문자열 공간 부족')
            e[rp:rp+len(b)]=b;rows.append(rp);rp+=len(b)+1
            rp+=rp&1
        # 설명 이미지: 넓은 것부터 빈 줄에 채움(first-fit decreasing)
        y0=nrows*16;j=NOTE_TABS[t];ids=[]
        while struct.unpack_from('<5H',e,j)[2]==24: ids.append((j,struct.unpack_from('<H',e,j)[0]));j+=10
        for cond in (False,True):
            recs=[(j,nid,note_img(NOTES[str(nid)],cond)) for j,nid in ids]
            shelves=[];pos={}
            for j,nid,im in sorted(recs,key=lambda r:-r[2].width):
                for sh in shelves:
                    if sh[1]+im.width<=256: break
                else:
                    sh=[y0+12*len(shelves),0];shelves.append(sh)
                pos[j]=(sh[1],sh[0]);sh[1]+=im.width
            if y0+12*len(shelves)<=256: break
        else: raise SystemExit('설명 공간 부족 %d'%t)
        for j,nid,im in recs:
            x,yy0=pos[j]
            for yy in range(12):
                for xx in range(im.width): put4(img,256,x+xx,yy0+yy,15-im.getpixel((xx,yy))*15//255)
            struct.pack_into('<5H',e,j,nid,im.width*2,24,x*2,yy0*2)
        y=y0+12*len(shelves)-12
        if cond: print('  (좁은 글꼴)')
        # 행 포인터 목록(행 0부터, NUL 종료)
        lst=lp
        for a in rows: struct.pack_into('<I',e,lp,a+VA);lp+=4
        lp+=4
        if lp>LST1: raise SystemExit('목록 공간 부족')
        ci=tabs.index(moves.atl[t][0]+VA)
        struct.pack_into('<I',e,LIST_TAB+4*ci,lst+VA)
        packs[PACK_OF[t]]=bytes(img)
        print('아틀라스 %2d: 글자 %3d, 행 %d, 설명 끝 y=%d'%(t,len(order),nrows,y+12))

# ---------------- 기술표 분류 제목(공용 팩 핸들 1877) ----------------
COMMON=0x7a46000
TITLES=['고유 타격기','잡기','홀드기','다운 공격기','특수 행동기','태그 협력기','배후 타격기','부보 타격기']
def build_titles():
    d=read(COMMON,0x20000);do=entries(d)[14][1]
    px=lambda x,y:(d[do+(y*256+x)//2]>>(4*(x&1)))&15
    img=bytearray([0xff]*0x8000)
    f=ImageFont.truetype(glyph.NANUM.replace('bRg','cBd'),24)
    for k,t in enumerate(TITLES):
        y0=28*k
        xs=[x for x in range(256) if any(px(x,y)!=15 for y in range(y0,y0+28))]
        cx=(xs[0]+xs[-1])//2;room=xs[-1]-xs[0]+1
        im=Image.new('L',(256,28),0);ImageDraw.Draw(im).text((0,0),t,font=f,fill=255)
        bb=im.getbbox();g=im.crop(bb)
        if g.width>room: g=g.resize((room,g.height),Image.LANCZOS)
        x0=cx-g.width//2;yy=y0+(28-g.height)//2
        for y in range(g.height):
            lv=1+(y*11)//max(1,g.height-1)          # 위 밝게 → 아래 어둡게(원본과 같은 계조)
            for x in range(g.width):
                a=g.getpixel((x,y))/255
                if a: put4(img,256,x0+x,yy+y,round(15-a*(15-lv)))
    return do,bytes(img)

# ---------------- 캐릭터 선택 프로필(256×256 PSMT4 ×14, 연속 배치) ----------------
PROF0,PROF_STRIDE=0x71C8B70,0x8140     # 헤더 위치, 픽셀은 +0x70
def build_profiles():
    rows=[l.rstrip(chr(10)).split('|') for l in open(os.path.join(R,'translation','profiles.txt'),encoding='utf-8') if l.strip() and not l.startswith('#')]
    f=ImageFont.truetype(glyph.NANUM.replace('bRg','eHv'),21)
    out=[]
    for k,lines in enumerate(rows):
        H=PROF0+k*PROF_STRIDE;img=bytearray(iso_read(ROMB+H+0x70,0x8000))
        for n,t in enumerate(lines):
            if t=='=': continue
            y0=25*n
            for y in range(y0,y0+25):
                for x in range(256): put4(img,256,x,y,15)
            if not t: continue
            im=Image.new('L',(256,25),0);ImageDraw.Draw(im).text((1,1),t,font=f,fill=255)
            for y in range(25):
                for x in range(256):
                    v=im.getpixel((x,y))
                    if v: put4(img,256,x,y0+y,15-v*15//255)
        out.append((H+0x70,bytes(img)))
    return out

def main():
    if not os.path.exists(OUT):
        print('ISO 복사…');shutil.copyfile(ISO,OUT)
    ko=check.load()
    cm=enc.build_map(set(c for t in ko.values() for c in t if '가'<=c<='힣'))
    e=bytearray(iso_read(ELF_LBA*2048,ELF_SIZE))
    place_text(e,ko,cm)
    # PCSX2 GameDB가 원본 CRC에만 거는 부팅 멈춤 수정(CRC가 바뀌므로 ELF에 직접 적용)
    struct.pack_into('<I',e,0x2b666c-0x200000+0x1000,0x24060000)
    rom_sys=iso_read(ROMB+SYSFONT,0x95b300-SYS_RAM)
    new_sys=build_sysfont(e,ko,cm,rom_sys)
    packs={}
    build_atlases(e,ko,cm,packs)
    tdo,timg=build_titles();profs=build_profiles()
    with open(OUT,'r+b') as f:
        f.seek(ROMB+COMMON+tdo);f.write(timg)
        for o,img in profs: f.seek(ROMB+o);f.write(img)
        f.seek(ELF_LBA*2048);f.write(e)
        f.seek(ROMB+SYSFONT);f.write(new_sys)
        for k,img in packs.items():
            d=read(CHAR_PACKS[k],0x10000);do=entries(d)[2][1]
            f.seek(ROMB+CHAR_PACKS[k]+do);f.write(img)
    print('완료',OUT)
if __name__=='__main__': main()
