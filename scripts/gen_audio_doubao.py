"""豆包 TTS 批量音频生成 — 遍历数据库场景，生成全部 MP3。
用法：
  python scripts/gen_audio_doubao.py          # 生成全部
  python scripts/gen_audio_doubao.py 1        # 只生成 L1
  python scripts/gen_audio_doubao.py 1 1      # 只生成 L1 S1
  python scripts/gen_audio_doubao.py --check  # 检查缺失文件
"""
import sys
import os
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import init_db, SessionLocal, Scenario
from tts import get_audio

AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "audio")


def gen(line, filename):
    """生成单个 MP3，已存在则跳过"""
    path = os.path.join(AUDIO_DIR, filename)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return "skip"
    text = line.strip()
    if not text:
        return "empty"

    result = get_audio(text)
    if result is None:
        return "fail"
    # get_audio 返回缓存路径，复制到目标文件名
    if result != path:
        import shutil
        shutil.copy2(result, path)
    return "ok"


def process_scenario(s, total, idx):
    """处理单个场景的全部音频"""
    prefix = f"l{s.level}_s{s.order}"
    print(f"\n[{idx}/{total}] L{s.level}-S{s.order} {s.title_cn} ({s.title})")
    stats = {"ok": 0, "skip": 0, "fail": 0, "empty": 0}

    # 1. 完整对话
    dialogue_lines = []
    for d in (s.dialogue_script or []):
        dialogue_lines.append(d.get("text_en", ""))
    dialogue_text = ". ".join(line for line in dialogue_lines if line)
    if dialogue_text:
        r = gen(dialogue_text, f"{prefix}_dialogue.mp3")
        stats[r] = stats.get(r, 0) + 1
        print(f"  dialogue: {r}", end="")

    # 2. 逐句
    for i, d in enumerate(s.dialogue_script or []):
        text = d.get("text_en", "")
        if text:
            r = gen(text, f"{prefix}_sentence_{i+1}.mp3")
            stats[r] = stats.get(r, 0) + 1

    # 3. 语块
    for i, c in enumerate(s.chunks or []):
        text = c.get("chunk", "")
        if text:
            r = gen(text, f"{prefix}_chunk_{i+1}.mp3")
            stats[r] = stats.get(r, 0) + 1

    # 4. 反应题
    for i, q in enumerate(s.reaction_questions or []):
        text = q.get("question", "")
        if text:
            r = gen(text, f"{prefix}_reaction_{i+1}.mp3")
            stats[r] = stats.get(r, 0) + 1

    print(f"  => ok:{stats.get('ok',0)} skip:{stats.get('skip',0)} fail:{stats.get('fail',0)} empty:{stats.get('empty',0)}")
    return stats


def check_missing():
    """检查并报告缺失的音频文件"""
    init_db()
    db = SessionLocal()
    scenarios = db.query(Scenario).order_by(Scenario.level, Scenario.order).all()
    total_missing = 0
    for s in scenarios:
        prefix = f"l{s.level}_s{s.order}"
        expected = []
        # 对话
        if (s.dialogue_script or []):
            expected.append(f"{prefix}_dialogue.mp3")
            for i, d in enumerate(s.dialogue_script or []):
                if d.get("text_en"):
                    expected.append(f"{prefix}_sentence_{i+1}.mp3")
        for i, c in enumerate(s.chunks or []):
            if c.get("chunk"):
                expected.append(f"{prefix}_chunk_{i+1}.mp3")
        for i, q in enumerate(s.reaction_questions or []):
            if q.get("question"):
                expected.append(f"{prefix}_reaction_{i+1}.mp3")

        missing = [f for f in expected if not os.path.exists(os.path.join(AUDIO_DIR, f))]
        if missing:
            total_missing += len(missing)
            print(f"L{s.level}-S{s.order} {s.title_cn}: 缺失 {len(missing)}/{len(expected)} 个")
            for f in missing[:5]:
                print(f"  - {f}")
            if len(missing) > 5:
                print(f"  ... 共 {len(missing)} 个")
    print(f"\n总计缺失: {total_missing} 个音频文件")
    db.close()
    return total_missing


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("level", nargs="?", type=int)
    parser.add_argument("order", nargs="?", type=int)
    parser.add_argument("--check", action="store_true", help="仅检查缺失文件")
    args = parser.parse_args()

    os.makedirs(AUDIO_DIR, exist_ok=True)

    if args.check:
        missing = check_missing()
        sys.exit(1 if missing > 0 else 0)

    init_db()
    db = SessionLocal()
    scenarios = db.query(Scenario).order_by(Scenario.level, Scenario.order).all()

    # 过滤
    if args.level:
        scenarios = [s for s in scenarios if s.level == args.level]
    if args.order:
        scenarios = [s for s in scenarios if s.order == args.order]

    total = len(scenarios)
    print(f"待处理: {total} 个场景")
    print(f"输出目录: {AUDIO_DIR}")
    print()

    agg = {"ok": 0, "skip": 0, "fail": 0, "empty": 0}
    for idx, s in enumerate(scenarios, 1):
        stats = process_scenario(s, total, idx)
        for k in agg:
            agg[k] += stats.get(k, 0)
        # API 限流：每场景间隔 2 秒
        if idx < total:
            time.sleep(2)

    db.close()

    print(f"\n{'='*50}")
    print(f"完成! 成功:{agg['ok']} 跳过:{agg['skip']} 失败:{agg['fail']} 空文本:{agg['empty']}")
    if agg['fail'] > 0:
        print("有失败项，可重新运行此脚本重试（已成功的会自动跳过）")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
