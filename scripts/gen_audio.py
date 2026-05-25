"""使用 Edge TTS 批量生成场景音频 MP3 文件。

用法：
  python scripts/gen_audio.py          # 生成全部场景
  python scripts/gen_audio.py 1        # 只生成 L1
  python scripts/gen_audio.py 1 1      # 只生成 L1 S1
"""
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import init_db, SessionLocal, Scenario
import edge_tts

AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "audio")
VOICE = "en-US-JennyNeural"  # 美式女声，自然清晰


async def generate(text, filename):
    """生成单个 MP3 文件"""
    path = os.path.join(AUDIO_DIR, filename)
    if os.path.exists(path):
        print(f"  [跳过] {filename}（已存在）")
        return
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(path)
    print(f"  [生成] {filename}")


async def generate_scenario(scenario, level_filter=None, order_filter=None):
    """为一个场景生成全部音频"""
    if level_filter and scenario.level != level_filter:
        return
    if order_filter and scenario.order != order_filter:
        return

    prefix = f"l{scenario.level}_s{scenario.order}"
    print(f"\n── L{scenario.level}-S{scenario.order} {scenario.title_cn} ──")

    # 1. 完整对话音频
    dialogue_text = " ".join(
        d.get("text_en", "") for d in (scenario.dialogue_script or [])
    )
    if dialogue_text:
        await generate(dialogue_text, f"{prefix}_dialogue.mp3")

    # 2. 逐句音频
    for i, d in enumerate(scenario.dialogue_script or []):
        text = d.get("text_en", "")
        if text:
            await generate(text, f"{prefix}_sentence_{i+1}.mp3")

    # 3. 语块音频
    for i, c in enumerate(scenario.chunks or []):
        text = c.get("chunk", "")
        if text:
            await generate(text, f"{prefix}_chunk_{i+1}.mp3")

    # 4. 反应题音频
    for i, q in enumerate(scenario.reaction_questions or []):
        text = q.get("question", "")
        if text:
            await generate(text, f"{prefix}_reaction_{i+1}.mp3")


async def main():
    os.makedirs(AUDIO_DIR, exist_ok=True)
    init_db()
    db = SessionLocal()

    level_filter = int(sys.argv[1]) if len(sys.argv) > 1 else None
    order_filter = int(sys.argv[2]) if len(sys.argv) > 2 else None

    scenarios = db.query(Scenario).order_by(Scenario.level, Scenario.order).all()
    for s in scenarios:
        await generate_scenario(s, level_filter, order_filter)

    db.close()
    print("\n音频生成完成")


if __name__ == "__main__":
    asyncio.run(main())
