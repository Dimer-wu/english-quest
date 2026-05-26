from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session
from models import get_db, User


def get_current_user(request: Request, db: Session = Depends(get_db)):
    """可选的用户认证 — 未登录或会话失效返回 None"""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        return None
    sv = request.session.get("sv", 0)
    if sv != (user.session_version or 0):
        return None
    return user


def require_user(request: Request, db: Session = Depends(get_db)):
    """强制用户认证 — 未登录或会话失效抛出 401"""
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(401, "请先登录")
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(401, "用户不存在")
    # 会话版本校验：其他设备登录后旧会话失效
    sv = request.session.get("sv", 0)
    if sv != (user.session_version or 0):
        raise HTTPException(401, "账号已在其他设备登录，请重新登录")
    return user


def require_admin(request: Request, db: Session = Depends(get_db)):
    """强制管理员认证"""
    user = require_user(request, db)
    if not user.is_admin:
        raise HTTPException(403, "需要管理员权限")
    return user
