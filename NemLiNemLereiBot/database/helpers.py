from .models import Submission, Article
from sqlalchemy.exc import SQLAlchemyError


def add_submission(Session, **kwargs):
    try:
        Session.add(
            Submission(**kwargs)
        )
        Session.commit()
    except exc.SQLAlchemyError:
        Session.rollback()

def update_submission_status(Session, submission_id, status):
    submission = Session.query(Submission).filter_by(base36_id=submission_id)
    submission.update({'status': status}, synchronize_session='fetch')
    Session.commit()


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
