import struct,sys,os
from PIL import Image
def clut(r,h,n):
    p,g,tbw,wl,hl,psm=struct.unpack_from('<IHHBBB',r,0x4a9220+16*h)[:6]
    d=r[p+0x80:p+0x80+4*n]
    c=[tuple(d[4*i:4*i+3])+(min(255,d[4*i+3]*2),) for i in range(n)]
    if n==256:
        c2=list(c)
        for i in range(256):
            j=(i&0xe7)|((i&8)<<1)|((i&16)>>1); c2[i]=c[j]
        c=c2
    return c
def tex(r,h,ch):
    p,g,tbw,wl,hl,psm=struct.unpack_from('<IHHBBB',r,0x4a9220+16*h)[:6]
    W,H=struct.unpack_from('<II',r,p+0x40);d=r[p+0x80:]
    if psm==0x14:
        pal=clut(r,ch,16);px=[]
        for i in range(W*H//2): b=d[i];px+= [pal[b&15],pal[b>>4]]
    elif psm==0x13:
        pal=clut(r,ch,256);px=[pal[b] for b in d[:W*H]]
    elif psm==0:
        px=[tuple(d[4*i:4*i+3])+(min(255,d[4*i+3]*2),) for i in range(W*H)]
    else: return None
    im=Image.new('RGBA',(W,H));im.putdata(px);return im
if __name__=='__main__':
    r=open(sys.argv[1],'rb').read();out=sys.argv[2];os.makedirs(out,exist_ok=True)
    E=[struct.unpack_from('<IHHBBB',r,0x4a9220+16*h)[:6] for h in range(4000)]
    for h,(p,g,tbw,wl,hl,psm) in enumerate(E):
        if not(0x100000<p<0x2000000) or wl>10 or hl>10 or psm not in (0x14,0x13,0): continue
        if psm==0 and wl<=4: continue
        c=h+1
        while c<h+4 and not(E[c][5]==0 and E[c][3]<=4): c+=1
        try:
            im=tex(r,h,c)
            if im and im.width*im.height>=1024: im.save(os.path.join(out,'%04d_%x_%dx%d.png'%(h,p,im.width,im.height)))
        except Exception as ex: print(h,ex)
