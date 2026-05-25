from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session
from models import get_db, User


def get_current_user(request: Request, db: Session = Depends(get_db)):
    """可选的用户认证 — 未登录返回 None"""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter_by(id=user_id).first()


def require_user(request: Request, db: Session = Depends(get_db)):
    """强制用户认证 — 未登录抛出 401"""
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(401, "请先登录")
    return db.query(User).filter_by(id=user_id).first()


def require_admin(request: Request, db: Session = Depends(get_db)):
    """强制管理员认证"""
    user = require_user(request, db)
    if not user.is_admin:
        raise HTTPException(403, "需要管理员权限")
    return user
