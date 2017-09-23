from .models import Submission, Article
from sqlalchemy.exc import SQLAlchemyError


def add_submission(Session, **kwargs):
    try:
        Session.add(
            Submission(**kwargs)
        )
        Session.commit()
    except SQLAlchemyError:
        Session.rollback()


def get_submissions(Session, **kwargs):
    submissions = Session.query(Submission).filter_by(**kwargs).all()
    return submissions


def get_article(Session, **kwargs):
    article = Session.query(Article).filter_by(**kwargs).first()
    return article


def add_article(Session, **kwargs):
    try:
        Session.add(
            Article(**kwargs)
        )
        Session.commit()
    except SQLAlchemyError:
        Session.rollback()
