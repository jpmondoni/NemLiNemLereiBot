from .models import Submission, Article


def submission_exists(Session, submission_id):
    query = Session.query(Submission.base36_id).filter_by(
        base36_id=submission_id).one_or_none()
    return query


def add_submission(Session, submission_id, submission_url):
    submission = Submission(base36_id=submission_id, url=submission_url)
    Session.add(submission)
    Session.commit()


def update_submission_status(Session, submission_id, status):
    submission = Session.query(Submission).filter_by(base36_id=submission_id)
    submission.update({'status': status}, synchronize_session='fetch')
    Session.commit()


def get_submissions_by_status(Session, status):
    submissions = Session.query(Submission.id, Submission.base36_id,
                                Submission.url, Submission.status).filter_by(status=status).all()
    return submissions


def article_exists(Session, submission_id):
    query = Session.query(Article).filter_by(
        submission_id=submission_id).one_or_none()
    return query


def add_article(Session, summary, submission_id, archiveis_link, subtitle=None, date_published=None):
    article = Article(subtitle=subtitle, summary=summary, date_published=date_published,
                      archiveis_link=archiveis_link, submission_id=submission_id)
    Session.add(article)
    Session.commit()
