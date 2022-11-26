from datetime import datetime

from sqlalchemy import Column, String, Integer, BigInteger, Boolean, DateTime

from model import db


class PinMessage(db.Model):
    __tablename__ = 'pin_message'

    id = Column(Integer(), primary_key=True)
    chat_id = Column(BigInteger())
    message_id = Column(BigInteger())

    unpin_date = Column(DateTime())

    created_at = Column(DateTime(), default=datetime.utcnow)
    updated_at = Column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    on_delete = Column(Boolean(), default=False, index=True)
