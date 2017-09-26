from . import Base
from sqlalchemy import (Column, Integer, DateTime, Text,
                        ForeignKey, Float, String)


class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    subtitle = Column(Text(collation='utf8_unicode_ci'))
    summary = Column(Text(collation='utf8_unicode_ci'), nullable=False)
    date_published = Column(DateTime)
    percentage_decrease = Column(Float)
    archiveis_url = Column(String(255))
    submission_id = Column(Integer,
                           ForeignKey("submissions.id"),
                           unique=True, nullable=False)

    mysql_charset = 'utf8'

    def __repr__(self):
        return "<Article(id='%s', subtitle='%s')>" % (self.id,
                                                      self.subtitle)
