from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
)
from app import db

class Payment(db.Model):
    id = Column(Integer, primary_key=True)
    payment_id = Column(String(32), unique=True)
    months = Column(Integer)
    user_id = Column(Integer)
    paid = Column(Boolean, default=False)
