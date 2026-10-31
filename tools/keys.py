"""PCSX2 창에 키 메시지를 보내 패드 입력(포커스 불필요). PCSX2.ini [Pad1] 키보드 매핑 사용."""
import ctypes,time,sys,os
u=ctypes.windll.user32
VK=dict(UP=0x26,RIGHT=0x27,DOWN=0x28,LEFT=0x25,T=ord('I'),O=ord('L'),X=ord('K'),S=ord('J'),SELECT=0x08,START=0x0D,L1=ord('Q'),R1=ord('E'),L2=ord('1'),R2=ord('3'))
PIDF=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'emu','emu.pid')
def wins():
    pid=int(open(PIDF).read());hs=[]
    @ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.c_void_p,ctypes.c_void_p)
    def cb(h,l):
        pp=ctypes.c_ulong();u.GetWindowThreadProcessId(ctypes.c_void_p(h),ctypes.byref(pp))
        if pp.value==pid: hs.append(h)
        return True
    u.EnumWindows(cb,0)
    out=list(hs)
    for h in hs:
        @ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.c_void_p,ctypes.c_void_p)
        def cc(c,l): out.append(c);return True
        u.EnumChildWindows(ctypes.c_void_p(h),cc,0)
    return out
def press(name,ms=120):
    vk=VK[name];sc=u.MapVirtualKeyW(vk,0)
    ext=1<<24 if vk in (0x25,0x26,0x27,0x28) else 0
    for h in wins(): u.PostMessageW(ctypes.c_void_p(h),0x100,vk,1|(sc<<16)|ext)
    time.sleep(ms/1000)
    for h in wins(): u.PostMessageW(ctypes.c_void_p(h),0x101,vk,1|(sc<<16)|ext|(3<<30))
    time.sleep(0.25)
if __name__=='__main__':
    for k in sys.argv[1:]:
        try: time.sleep(float(k))
        except ValueError: press(k)
