from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from .Submissions import Submission
from .Articles import Article