# 테스트용: 에뮬 종료 → 빌드 → 결과 ISO 부팅(최소화). work/emu 에 포터블 PCSX2 필요
cd "$(dirname "$0")/.."
taskkill //F //IM pcsx2-qt.exe >/dev/null 2>&1
PYTHONIOENCODING=utf-8 python tools/build.py | tail -1 || exit 1
python tools/emu.py launch "DOA2 - Hardcore (Japan) (Korean).iso" >/dev/null
