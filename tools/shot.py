import sys,emu
from PIL import Image
imgs=[]
import pad,time
for i,k in enumerate(sys.argv[1:]):
    if k=='snap':
        p=emu.snap('q%d'%i); imgs.append(Image.open(p).convert('RGB').resize((320,240)))
    elif k.startswith('load'): emu.load(int(k[4:]))
    else: pad.seq(k)
W=min(len(imgs),4)
c=Image.new('RGB',(320*W,240*((len(imgs)+W-1)//W)))
for i,im in enumerate(imgs): c.paste(im,(320*(i%W),240*(i//W)))
c.save(emu.os.path.join(emu.R,'tmp','s.png'))
