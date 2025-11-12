import subprocess
import sys
import os

# ====== 실행 순서 정의 ======
scripts = [
    "중앙일보_NewsScrap.py",
    "조선일보_NewsScrap.py",
    "한겨레_NewsScrap.py"
]

def run_script(script):
    print(f"\n{'='*80}")
    print(f"▶ {script} 실행 시작")
    print(f"{'='*80}\n")
    try:
        subprocess.run([sys.executable, script], check=True)
        print(f"\n✅ {script} 실행 완료!\n")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ {script} 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    for s in scripts:
        if os.path.exists(s):
            run_script(s)
        else:
            print(f"❌ 파일을 찾을 수 없습니다: {s}")
    print("\n🎉 모든 신문사 크롤링이 완료되었습니다!\n")