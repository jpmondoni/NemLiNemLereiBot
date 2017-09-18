from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base


class Database:
    def __init__(self, driver, username, password, host, port, database):
        self.driver = driver
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.database = database

    def connect(self):
        url = '{driver}://{username}:{password}@{host}:{port}/{database}?charset=utf8'
        engine = create_engine(url.format(**self.__dict__),
                               encoding='utf-8')
        self.engine = engine

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    @property
    def session(self):
        Session = sessionmaker(bind=self.engine)
        return Session()