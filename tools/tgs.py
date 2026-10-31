"""tgs 텍스처 묶음 읽기: 헤더 'tgs\0', +8 항목 수, +0x30 부터 항목(오프셋)…  GIF 블록을 직접 훑어 텍스처/CLUT 추출."""
import struct
from PIL import Image
ISO='../DOA2 - Hardcore (Japan) (En,Ja,Fr,De,Es,It).iso'
ROMB=1575031*2048
CHAR_PACKS=[0x7a5b000,0x7a66000,0x7a73000,0x7a81800,0x7a8a800,0x7a95800,0x7aa0000,0x7aa9800,0x7ab3000,0x7abd800,0x7ac8800,0x7ad7000,0x7ae0800,0x7aeb800]
def blocks(d):
    """GIF 업로드 블록 목록: (데이터 오프셋, dbp, dbw, psm, w, h)"""
    out=[];i=0
    while i+0x80<=len(d):
        lo=struct.unpack_from('<Q',d,i)[0]
        a1=struct.unpack_from('<Q',d,i+0x28)[0]
        if (lo>>60)==1 and (lo&0x7fff)==4 and a1==0x50:
            bb=struct.unpack_from('<Q',d,i+0x20)[0]
            w,h=struct.unpack_from('<II',d,i+0x40)
            n=struct.unpack_from('<Q',d,i+0x70)[0]&0x7fff
            out.append((i+0x80,(bb>>32)&0x3fff,(bb>>48)&0x3f,(bb>>56)&0x3f,w,h,n*16))
            i+=0x80+n*16
        else: i+=16
    return out
def read(off,size):
    f=open(ISO,'rb');f.seek(ROMB+off);return f.read(size)
def img4(d,o,w,h,clut):
    px=[]
    for k in range(w*h//2): b=d[o+k];px+=[clut[b&15],clut[b>>4]]
    im=Image.new('RGBA',(w,h));im.putdata(px);return im
def clut16(d,o): return [tuple(d[o+4*i:o+4*i+3])+(min(255,d[o+4*i+3]*2),) for i in range(16)]
def entries(d):
    """[(entry_off, data_off, psm, w, h)]  항목 = 0x80 헤더(+0x38 BITBLTBUF, +0x50 TRXREG) + 데이터"""
    n=struct.unpack_from('<I',d,8)[0];out=[]
    for k in range(n):
        o=struct.unpack_from('<I',d,0x30+4*k)[0]
        bb=struct.unpack_from('<Q',d,o+0x30)[0];w,h=struct.unpack_from('<II',d,o+0x50)
        out.append((o,o+0x80,(bb>>56)&0x3f,w,h))
    return out
