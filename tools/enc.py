"""한글 번역 → 게임 바이트. 한글은 SJIS 한자 코드에 대응, ASCII는 전각으로(제어 토큰 제외)."""
import re
ASCII_FW=True
TOK=re.compile(r'(%s|%d|\$-\d|@-\d|#[A-Z]|\n)')
def fw(c):
    if c==' ': return ' '
    if c=='~': return '～'
    if '!'<=c<='~' and ASCII_FW: return chr(ord(c)+0xfee0)
    return c
def norm(t):
    """제어 토큰은 그대로, 나머지 ASCII는 전각 문자로."""
    t=t.replace(chr(92)+'n',chr(10))
    out=[]
    for i,p in enumerate(TOK.split(t)):
        out.append(p if i%2 else ''.join(fw(c) for c in p))
    return ''.join(out)
def codes():
    """SJIS 한자 영역(0x889F~)의 유효 2바이트 코드 열."""
    for hi in list(range(0x88,0xa0))+list(range(0xe0,0xea)):
        for lo in list(range(0x40,0x7f))+list(range(0x80,0xfd)):
            if hi==0x88 and lo<0x9f: continue
            yield bytes([hi,lo])
def build_map(chars):
    g=codes();return {c:next(g) for c in sorted(chars)}
def encode(t,cmap):
    b=b''
    for i,p in enumerate(TOK.split(norm(t))):
        if i%2: b+=p.encode('ascii');continue
        for c in p:
            b+=cmap[c] if c in cmap else c.encode('cp932')
    return b
