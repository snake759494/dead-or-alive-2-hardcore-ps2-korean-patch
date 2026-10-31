"""테스트 전용 입력: libpad DMA 영역(0x5C2E40, 이중 버퍼 0x80 간격)의 버튼 바이트를 PINE으로 연속 덮어씀."""
import socket,struct,time,sys
PORT=28241;AREA=(0x5c2e42,)
B=dict(SELECT=0x1,START=0x8,UP=0x10,RIGHT=0x20,DOWN=0x40,LEFT=0x80,L2=0x100,R2=0x200,L1=0x400,R1=0x800,T=0x1000,O=0x2000,X=0x4000,S=0x8000)
def hold(names,ms=60):
    m=0
    for n in names.split('+'): m|=B[n]
    v=(~m)&0xffff; v=((v&0xff)<<0)|((v>>8)<<8)
    s=socket.create_connection(('127.0.0.1',PORT),timeout=10)
    pk=b''.join(struct.pack('<IBIH',11,5,a,v) for a in AREA)
    t=time.time()+ms/1000;n=0
    while time.time()<t:
        s.sendall(pk*8); n+=1
        s.recv(65536)
    s.close(); time.sleep(0.3)
def seq(*ks):
    for k in ks:
        try: time.sleep(float(k))
        except ValueError: hold(k)
if __name__=='__main__': seq(*sys.argv[1:])
