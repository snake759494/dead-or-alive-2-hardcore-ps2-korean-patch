# 재빌드

## 준비물

- 원본 ISO `DOA2 - Hardcore (Japan) (En,Ja,Fr,De,Es,It).iso` (README의 해시와 일치해야 함)를 저장소 루트에 둡니다.
- Python 3.13, `Pillow`
- 글꼴(`docs/FONT_CREDITS.md`):
  - 저장소 루트: `NanumSquareNeo-bRg.ttf`, `NanumSquareNeo-cBd.ttf`, `NanumSquareNeo-eHv.ttf`
  - `fonts/Galmuri11.ttf`, `fonts/Galmuri11-Condensed.ttf`
- xdelta3 (배포 파일을 만들 때만)

## 빌드

```powershell
python tools/unpack_elf.py   # 원본 ISO 의 실행파일 → tmp/SLPS_250.26
python tools/build.py        # → DOA2 - Hardcore (Japan) (Korean).iso
```

결과 ISO가 없으면 원본을 복사한 뒤, 바꾸는 영역(실행파일, 시스템 글꼴, 커맨드 리스트 아틀라스, 분류 제목, 프로필)을 매번 원본 바이트에서 다시 만들어 덮어씁니다. 결과 ISO의 SHA-256이 `release_manifest.json`의 `output_iso_sha256`과 같아야 합니다.

## 배포 파일

```powershell
xdelta3 -e -0 -S none -A -s "DOA2 - Hardcore (Japan) (En,Ja,Fr,De,Es,It).iso" "DOA2 - Hardcore (Japan) (Korean).iso" DOA2_Hardcore_PS2_KO_v1.0.xdelta
```

실행파일이 바뀌면 게임 CRC(실행파일을 4바이트 단위로 XOR한 값, `tools/emu.py`의 `elf_crc`)를 다시 계산해 `patches/SLPS-25026_<CRC>.pnach`의 이름을 맞추고, 와이드 패치 주소(`0x4588D0`, `0x459140`, `0x4599B0`, `0x45A220`, `0x3A5D2C`)의 원래 값이 그대로인지 확인합니다.

## 번역 수정

- `translation/ko_*.tsv`: `실행파일 주소(16진) <탭> 번역`. `\n` = 줄바꿈, `%s`·`%d`·`$-n`·`@-n`·`#X`는 제어 코드라 그대로 둡니다.
- `translation/notes.txt`: 커맨드 리스트 조건 설명(`번호 <탭> 문구`).
- `translation/profiles.txt`: 프로필(`이름|국적|유파|나이|키|체중|생일 혈액형|직업`, `=`는 원본 숫자 유지).
- 원문 대조표가 필요하면 `python tools/extract.py`로 `translation/ja.tsv`를 만듭니다(배포하지 않음).
