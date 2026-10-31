"""글리프 렌더링: 16px 칸에 4비트(0~15) 계조."""
from PIL import Image,ImageDraw,ImageFont
import os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NANUM=os.path.join(R,'NanumSquareNeo-bRg.ttf')
GAL=os.path.join(R,'fonts','Galmuri11.ttf')
_f={}
def font(path,size):
    k=(path,size)
    if k not in _f: _f[k]=ImageFont.truetype(path,size)
    return _f[k]
def cell(ch,size=16,fs=15,path=NANUM,dy=0,bold=0):
    """size×size 칸 안 가운데 정렬, 값 0~15 리스트(행 우선)."""
    im=Image.new('L',(size*4,size*4),0);d=ImageDraw.Draw(im)
    f=font(path,fs);d.text((size,size),ch,font=f,fill=255,stroke_width=bold,stroke_fill=255)
    bb=im.getbbox()
    out=Image.new('L',(size,size),0)
    if bb:
        g=im.crop(bb);x=(size-g.width)//2
        asc=f.getbbox('가')
        y=size+asc[1]  # 기준선 맞춤
        out.paste(g,(x,bb[1]-size-asc[1]+(size-(asc[3]-asc[1]))//2+dy))
    return [v*15//255 for v in out.getdata()]
