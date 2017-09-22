from . import Base
import datetime
from sqlalchemy import (Column, Integer, String, DateTime)


class Submission(Base):
    __tablename__ = 'submissions'

    id = Column(Integer, primary_key=True)
    base36_id = Column(String(255), unique=True, nullable=False)
    url = Column(String(255), nullable=False)
    status = Column(String(255), default='TO_FETCH')
    added_date = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return "<Submission('%s', '%s', '%s'>" % (self.id,
                                                  self.base36_id,
                                                  self.url)
