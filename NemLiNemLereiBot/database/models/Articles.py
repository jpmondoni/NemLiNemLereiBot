from . import Base
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey


class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    subtitle = Column(String(255))
    summary = Column(Text, nullable=False)
    date_published = Column(DateTime)
    archiveis_link = Column(String(255))
    submission_id = Column(Integer, ForeignKey(
        "submissions.id"), unique=True, nullable=False)

    def __repr__(self):
        return "<Article(id='%s', subtitle='%s')>" % (
            self.id, self.subtitle)
