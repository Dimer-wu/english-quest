import logging
from datetime import date, datetime, timezone, timedelta
from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
import httpx

from config import (
    SECRET_KEY, APP_NAME, LOG_LEVEL,
    ADMIN_USERNAME, ADMIN_PASSWORD,
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL,
    SECURE_COOKIES, SESSION_MAX_AGE,
    SRS_INTERVALS,
)
from models import init_db, SessionLocal, get_db, User, Scenario, UserProgress, UserChunk, ChatLog
from deps import get_current_user, require_user, require_admin
from tts import get_audio

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("english-quest")

app = FastAPI(title=APP_NAME)
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=SESSION_MAX_AGE,
    https_only=SECURE_COOKIES,
    same_site="lax",
    session_cookie="eq_session",
)
app.mount("/static", StaticFiles(directory="static"), name="static")


# ── 启动 ──────────────────────────────────────────────

@app.on_event("startup")
def startup():
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY 环境变量未设置，请在 .env 中配置")
    init_db()
    db = SessionLocal()
    try:
        if ADMIN_PASSWORD and not db.query(User).filter_by(username=ADMIN_USERNAME).first():
            db.add(User(
                username=ADMIN_USERNAME,
                password_hash=generate_password_hash(ADMIN_PASSWORD),
                status="active",
                is_admin=1,
            ))
            db.commit()
            logger.info("已创建管理员: %s", ADMIN_USERNAME)
    finally:
        db.close()
    logger.info("%s 启动完成", APP_NAME)


# ── 页面入口 ──────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def index():
    with open("templates/index.html", encoding="utf-8") as f:
        return f.read()


@app.get("/manifest.json")
def manifest():
    return FileResponse("static/manifest.json", media_type="application/manifest+json")


@app.get("/sw.js")
def service_worker():
    return FileResponse("static/sw.js", media_type="application/javascript")


# ── 认证 API ──────────────────────────────────────────

@app.post("/api/login")
def api_login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        raise HTTPException(401, "用户名或密码错误")
    if user.status == "pending":
        raise HTTPException(403, "账号等待管理员审核中，请稍后再试")
    if user.status == "disabled":
        raise HTTPException(403, "账号已被禁用，请联系管理员")
    # 踢掉旧会话：递增版本号，旧会话下次请求时校验失败
    user.session_version = (user.session_version or 0) + 1
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    request.session["user_id"] = user.id
    request.session["sv"] = user.session_version
    return {"ok": True, "user": {"id": user.id, "username": user.username, "level": user.level}}


@app.post("/api/register")
def api_register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if db.query(User).filter_by(username=username).first():
        raise HTTPException(400, "用户名已存在")
    user_count = db.query(User).count()
    if user_count >= 10:
        raise HTTPException(403, "注册名额已满（上限 10 人），请联系管理员")
    user = User(
        username=username,
        password_hash=generate_password_hash(password),
        status="pending",
    )
    db.add(user)
    db.commit()
    return {"ok": True, "pending": True, "message": "注册成功！请等待管理员审核后即可登录使用。"}


@app.get("/api/me")
def api_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return {"user": None}
    total_scenarios = db.query(Scenario).count()
    completed = db.query(UserProgress).filter_by(user_id=user.id).filter(UserProgress.completed_at.isnot(None)).count()
    total_chunks = db.query(UserChunk).filter_by(user_id=user.id).count()
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "level": user.level,
            "streak_days": user.streak_days,
            "is_admin": bool(user.is_admin),
        },
        "stats": {
            "completed_scenarios": completed,
            "total_scenarios": total_scenarios,
            "total_chunks": total_chunks,
        },
    }


@app.post("/api/logout")
def api_logout(request: Request):
    request.session.clear()
    return {"ok": True}


# ── 场景 API ──────────────────────────────────────────

@app.get("/api/scenarios")
def api_scenarios(db: Session = Depends(get_db)):
    scenarios = db.query(Scenario).order_by(Scenario.level, Scenario.order).all()
    return {
        "scenarios": [
            {
                "id": s.id,
                "level": s.level,
                "order": s.order,
                "title": s.title,
                "title_cn": s.title_cn,
                "category": s.category,
                "can_do": s.can_do,
            }
            for s in scenarios
        ]
    }


@app.get("/api/scenarios/{scenario_id}")
def api_scenario_detail(request: Request, scenario_id: int, db: Session = Depends(get_db)):
    s = db.query(Scenario).filter_by(id=scenario_id).first()
    if not s:
        raise HTTPException(404, "场景不存在")
    user_id = request.session.get("user_id")
    progress = None
    if user_id:
        progress = db.query(UserProgress).filter_by(user_id=user_id, scenario_id=scenario_id).first()
    return {
        "scenario": {
            "id": s.id,
            "level": s.level,
            "order": s.order,
            "title": s.title,
            "title_cn": s.title_cn,
            "dialogue_script": s.dialogue_script,
            "chunks": s.chunks,
            "pattern_focus": s.pattern_focus,
            "reaction_questions": s.reaction_questions,
            "can_do": s.can_do,
            "audio_dialogue": s.audio_dialogue,
            "audio_chunks": s.audio_chunks,
        },
        "progress": {
            "step1_done": progress.step1_done if progress else 0,
            "step2_done": progress.step2_done if progress else 0,
            "step3_done": progress.step3_done if progress else 0,
            "step4_done": progress.step4_done if progress else 0,
            "step5_done": progress.step5_done if progress else 0,
            "step6_done": progress.step6_done if progress else 0,
            "completed": bool(progress.completed_at) if progress else False,
            "can_do_self_eval": progress.can_do_self_eval if progress else 0,
        } if progress else None,
    }


# ── 进度 API ──────────────────────────────────────────

@app.post("/api/progress/{scenario_id}")
def api_update_progress(
    scenario_id: int,
    step: int = Form(...),
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    if step < 1 or step > 6:
        raise HTTPException(400, f"步骤编号无效: {step}，有效范围 1-6")
    progress = db.query(UserProgress).filter_by(user_id=user.id, scenario_id=scenario_id).first()
    if not progress:
        progress = UserProgress(user_id=user.id, scenario_id=scenario_id)
        db.add(progress)

    step_field = f"step{step}_done"
    if hasattr(progress, step_field):
        setattr(progress, step_field, 1)

    # 全部完成时记录
    steps = [progress.step1_done, progress.step2_done, progress.step3_done,
             progress.step4_done, progress.step5_done, progress.step6_done]
    if all(steps):
        progress.completed_at = datetime.now(timezone.utc)
        # 更新连续学习天数
        today = date.today()
        if user.last_study_date != today:
            yesterday = today - timedelta(days=1)
            if user.last_study_date == yesterday:
                user.streak_days += 1
            else:
                user.streak_days = 1
            user.last_study_date = today

    db.commit()
    return {"ok": True}


# ── 语块本 API ────────────────────────────────────────

@app.get("/api/chunks")
def api_chunks(user: User = Depends(require_user), db: Session = Depends(get_db)):
    chunks = db.query(UserChunk).filter_by(user_id=user.id).order_by(UserChunk.collected_at.desc()).all()
    return {
        "chunks": [
            {
                "id": c.id,
                "chunk_text": c.chunk_text,
                "translation": c.translation,
                "scene_sentence": c.scene_sentence,
                "scenario_id": c.scenario_id,
                "mastery": c.mastery,
            }
            for c in chunks
        ]
    }


@app.post("/api/chunks")
def api_add_chunk(
    chunk_text: str = Form(...),
    translation: str = Form(...),
    scene_sentence: str = Form(""),
    scenario_id: int = Form(...),
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    chunk = UserChunk(
        user_id=user.id,
        scenario_id=scenario_id,
        chunk_text=chunk_text,
        translation=translation,
        scene_sentence=scene_sentence,
        next_review_at=datetime.now(timezone.utc) + timedelta(seconds=SRS_INTERVALS[0]),
    )
    db.add(chunk)
    db.commit()
    return {"ok": True, "id": chunk.id}


@app.post("/api/chunks/{chunk_id}/mastery")
def api_update_mastery(
    chunk_id: int,
    mastery: int = Form(...),
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    chunk = db.query(UserChunk).filter_by(id=chunk_id, user_id=user.id).first()
    if not chunk:
        raise HTTPException(404, "语块不存在")
    chunk.mastery = mastery
    chunk.last_reviewed_at = datetime.now(timezone.utc)
    if mastery == 2:
        chunk.next_review_at = datetime.now(timezone.utc) + timedelta(seconds=SRS_INTERVALS[1])
    elif mastery == 3:
        chunk.next_review_at = datetime.now(timezone.utc) + timedelta(seconds=SRS_INTERVALS[2])
    else:
        chunk.next_review_at = datetime.now(timezone.utc) + timedelta(seconds=SRS_INTERVALS[0])
    db.commit()
    return {"ok": True}


@app.get("/api/chunks/due")
def api_due_chunks(user: User = Depends(require_user), db: Session = Depends(get_db)):
    """获取到期需要复习的语块"""
    now = datetime.now(timezone.utc)
    chunks = db.query(UserChunk).filter(
        UserChunk.user_id == user.id,
        UserChunk.next_review_at <= now,
    ).order_by(UserChunk.next_review_at).all()
    return {
        "chunks": [
            {
                "id": c.id,
                "chunk_text": c.chunk_text,
                "translation": c.translation,
                "mastery": c.mastery,
            }
            for c in chunks
        ]
    }


# ── AI 对话 API ───────────────────────────────────────

@app.post("/api/chat")
async def api_chat(
    message: str = Form(...),
    scenario_id: int = Form(...),
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    # 获取场景信息和对话历史
    scenario = db.query(Scenario).filter_by(id=scenario_id).first()
    if not scenario:
        raise HTTPException(404, "场景不存在")
    history = db.query(ChatLog).filter_by(user_id=user.id, scenario_id=scenario_id) \
        .order_by(ChatLog.created_at).limit(20).all()

    # 构建系统提示词
    scenario_title = scenario.title_cn or scenario.title
    dialogue_context = ""
    if scenario.dialogue_script:
        sample_lines = []
        for d in scenario.dialogue_script[:8]:
            sample_lines.append(f"{d.get('speaker', '')}: {d.get('text_en', '')}")
        dialogue_context = "\n".join(sample_lines)

    system_prompt = (
        f"你是 English Quest 口语练习助手。当前场景：{scenario_title}。\n\n"
        f"规则：\n"
        f"1. 像真人一样用自然口语对话，不是教科书英语\n"
        f"2. 用适当的停顿词（well, um, you know）、缩读（gonna, wanna, kinda）\n"
        f"3. 对话保持在场景情境中\n"
        f"4. 不要直接指出用户语法错误，用自然的正确表达回应\n"
        f"5. 每轮回复结束后，用「💡 地道小贴士：xxx」给一句口语技巧\n"
        f"6. 用户水平为零基础成人，用简单词汇，但语气要自然\n\n"
        f"参考对话：\n{dialogue_context}"
    )

    messages = [{"role": "system", "content": system_prompt}]
    for h in history:
        messages.append({"role": h.role, "content": h.content})
    messages.append({"role": "user", "content": message})

    # 保存用户消息
    db.add(ChatLog(user_id=user.id, scenario_id=scenario_id, role="user", content=message))
    db.commit()

    # 调用 DeepSeek API
    ai_reply = ""
    tip = ""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{DEEPSEEK_BASE_URL}/v1/chat/completions",
                headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
                json={"model": DEEPSEEK_MODEL, "messages": messages, "temperature": 0.8},
            )
            data = resp.json()
            ai_reply = data["choices"][0]["message"]["content"]

        # 提取小贴士
        if "💡" in ai_reply:
            parts = ai_reply.split("💡", 1)
            if len(parts) == 2:
                ai_reply = parts[0].strip()
                tip_marker = "地道小贴士：" if "地道小贴士：" in parts[1] else ""
                tip = parts[1].replace("地道小贴士：", "").strip()
    except Exception as e:
        logger.error("AI 对话失败: %s", e)
        ai_reply = "Sorry, I got a bit distracted. Could you say that again?"

    # 保存 AI 回复
    db.add(ChatLog(user_id=user.id, scenario_id=scenario_id, role="assistant", content=ai_reply, tip=tip))
    db.commit()

    return {"reply": ai_reply, "tip": tip}


# ── TTS 语音合成 API ──────────────────────────────────

@app.get("/api/tts")
def api_tts(text: str, voice: str = "en_female_dacey_uranus_bigtts"):
    """文本转语音，返回 MP3 文件。自动缓存，后续请求直接命中磁盘。"""
    path = get_audio(text, voice)
    if path is None:
        raise HTTPException(500, "TTS synthesis failed")
    return FileResponse(path, media_type="audio/mpeg")


# ── 管理员 API ────────────────────────────────────────

@app.get("/api/admin/users")
def api_admin_users(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return {
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "status": u.status,
                "is_admin": bool(u.is_admin),
                "level": u.level,
                "streak_days": u.streak_days,
                "created_at": u.created_at.strftime("%Y-%m-%d %H:%M") if u.created_at else "",
                "last_login_at": u.last_login_at.strftime("%Y-%m-%d %H:%M") if u.last_login_at else "从未登录",
            }
            for u in users
        ]
    }


@app.post("/api/admin/users/{user_id}/approve")
def api_admin_approve(user_id: int, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    target = db.query(User).filter_by(id=user_id).first()
    if not target:
        raise HTTPException(404, "用户不存在")
    if target.is_admin:
        raise HTTPException(400, "不能操作管理员账号")
    target.status = "active"
    db.commit()
    return {"ok": True}


@app.post("/api/admin/users/{user_id}/disable")
def api_admin_disable(user_id: int, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    target = db.query(User).filter_by(id=user_id).first()
    if not target:
        raise HTTPException(404, "用户不存在")
    if target.is_admin:
        raise HTTPException(400, "不能操作管理员账号")
    target.status = "disabled"
    db.commit()
    return {"ok": True}


@app.post("/api/admin/users/{user_id}/delete")
def api_admin_delete(user_id: int, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    target = db.query(User).filter_by(id=user_id).first()
    if not target:
        raise HTTPException(404, "用户不存在")
    if target.is_admin:
        raise HTTPException(400, "不能删除管理员账号")
    # 清理关联数据
    db.query(UserProgress).filter_by(user_id=user_id).delete()
    db.query(UserChunk).filter_by(user_id=user_id).delete()
    db.query(ChatLog).filter_by(user_id=user_id).delete()
    db.delete(target)
    db.commit()
    return {"ok": True}


# ── 启动入口 ──────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    print(f"[启动] {APP_NAME}")
    print("       打开浏览器访问 http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)
