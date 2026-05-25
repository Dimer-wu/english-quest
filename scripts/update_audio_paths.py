"""为现有数据库中的场景补充音频文件路径（与 gen_audio.py 命名规则一致）"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import init_db, SessionLocal, Scenario
from sqlalchemy.orm.attributes import flag_modified


def update():
    init_db()
    db = SessionLocal()
    try:
        scenarios = db.query(Scenario).order_by(Scenario.level, Scenario.order).all()
        updated = 0

        for s in scenarios:
            prefix = f"/static/audio/l{s.level}_s{s.order}"
            changed = False

            # 补充 audio_dialogue
            if not s.audio_dialogue:
                s.audio_dialogue = f"{prefix}_dialogue.mp3"
                changed = True

            # 补充 audio_chunks
            chunks = s.chunks or []
            existing_audio = s.audio_chunks or []
            new_audio = []
            for i in range(len(chunks)):
                if i < len(existing_audio) and existing_audio[i]:
                    new_audio.append(existing_audio[i])
                else:
                    new_audio.append(f"{prefix}_chunk_{i+1}.mp3")
            if new_audio != existing_audio:
                s.audio_chunks = new_audio
                flag_modified(s, "audio_chunks")
                changed = True

            # 补充 dialogue_script 各句的 audio_url
            lines = list(s.dialogue_script or [])
            lines_changed = False
            for i, line in enumerate(lines):
                if "audio_url" not in line or not line.get("audio_url"):
                    line["audio_url"] = f"{prefix}_sentence_{i+1}.mp3"
                    lines_changed = True
            if lines_changed:
                s.dialogue_script = lines
                flag_modified(s, "dialogue_script")
                changed = True

            if changed:
                updated += 1
                print(f"  已更新 L{s.level}-S{s.order} {s.title_cn}")
            else:
                print(f"  [跳过] L{s.level}-S{s.order} {s.title_cn}（无需更新）")

        if updated > 0:
            db.commit()
            print(f"\n共更新 {updated} 个场景")
        else:
            print("\n所有场景音频路径已就绪，无需更新")
    finally:
        db.close()


if __name__ == "__main__":
    update()
