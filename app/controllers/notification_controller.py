from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.config.db import SessionLocal
from app.services.notification_service import list_notifications

router = APIRouter(prefix="/notifications", tags=["notifications"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_notifications(
    db: Session = Depends(get_db),
    email: str = Query(..., description="Correo del usuario")
):
    return list_notifications(db, user_email=email)
