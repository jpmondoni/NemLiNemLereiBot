from .models import Submission, Article


def add_submission(Session, **kwargs):
    try:
        Session.add(
            Submission(**kwargs)
        )
        Session.commit()
    except Exception:
        pass

def update_submission_status(Session, submission_id, status):
    submission = Session.query(Submission).filter_by(base36_id=submission_id)
    submission.update({'status': status}, synchronize_session='fetch')
    Session.commit()


def get_submissions_by_status(Session, status):
    submissions = Session.query(Submission.id, Submission.base36_id,
                                Submission.url, Submission.status).filter_by(status=status).all()
    return submissions


def add_article(Session, **kwargs):
    try:
        Session.add(
            Article(**kwargs)
        )
        Session.commit()
    except Exception:
        pass
