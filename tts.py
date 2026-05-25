"""豆包 TTS 语音合成模块 — 调用火山引擎 API，自动缓存到磁盘"""
import hashlib
import os
import base64
import logging
import httpx
from config import VOLC_APP_ID, VOLC_ACCESS_TOKEN

logger = logging.getLogger("tts")
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "audio", "tts_cache")
VOICE_EN = "BV002_streaming"  # 美式英语女声（流式合成，速度快）

os.makedirs(CACHE_DIR, exist_ok=True)


def _cache_key(text, voice):
    return hashlib.md5(f"{text}|{voice}".encode()).hexdigest() + ".mp3"


def get_audio(text, voice=VOICE_EN):
    """获取文本的语音 MP3。优先读缓存，缓存未命中则调 API 生成。"""
    key = _cache_key(text, voice)
    path = os.path.join(CACHE_DIR, key)

    if os.path.exists(path):
        return path

    try:
        import requests

        resp = requests.post(
            "https://openspeech.bytedance.com/api/v1/tts",
            headers={
                "Authorization": f"Bearer;{VOLC_ACCESS_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "app": {
                    "appid": VOLC_APP_ID,
                    "token": VOLC_ACCESS_TOKEN,
                    "cluster": "volcano_tts",
                },
                "user": {"uid": "english-quest"},
                "audio": {
                    "voice_type": voice,
                    "encoding": "mp3",
                    "speed_ratio": 1.0,
                },
                "request": {
                    "reqid": key[:36],
                    "text": text,
                    "text_type": "plain",
                    "operation": "query",
                },
            },
            timeout=15,
        )
        data = resp.json()
        if data.get("code") == 3000:
            audio_bytes = base64.b64decode(data["data"])
            with open(path, "wb") as f:
                f.write(audio_bytes)
            logger.info("TTS cached: %s (%d bytes)", key[:16], len(audio_bytes))
            return path
        else:
            logger.error("TTS API error: %s", data.get("message", "unknown"))
            return None
    except Exception as e:
        logger.error("TTS failed: %s", e)
        return None
