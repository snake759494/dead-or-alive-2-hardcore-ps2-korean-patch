"""원본 ISO 에서 실행파일 SLPS_250.26 을 tmp/ 로 꺼낸다(extract.py·build.py 가 사용)."""
import os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ISO=os.path.join(R,'DOA2 - Hardcore (Japan) (En,Ja,Fr,De,Es,It).iso')
os.makedirs(os.path.join(R,'tmp'),exist_ok=True)
with open(ISO,'rb') as f: f.seek(1572714*2048); d=f.read(4743236)
open(os.path.join(R,'tmp','SLPS_250.26'),'wb').write(d)
print('tmp/SLPS_250.26',len(d))
