from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Submission, Article
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging


class Database:
    def __init__(self, driver, username, password, host, port, database):
        self.driver = driver
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.database = database

        self.connect()
        self.create_tables()
        self.make_session()

    def connect(self):
        url = ('{driver}://{username}:{password}@'
               '{host}:{port}/{database}?charset=utf8')
        engine = create_engine(url.format(**self.__dict__),
                               encoding='utf-8')
        self.engine = engine

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def make_session(self):
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def commit(self):
        self.session.commit()

    def add_submission(self, **kwargs):
        try:
            self.session.add(
                Submission(**kwargs)
            )
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()

    def add_article(self, **kwargs):
        try:
            self.session.add(
                Article(**kwargs)
            )
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()

    def get_submissions(self, **kwargs):
        submissions = self.session.query(Submission).filter_by(**kwargs).all()
        return submissions

    def get_article(self, **kwargs):
        article = self.session.query(Article).filter_by(**kwargs).first()
        return article

