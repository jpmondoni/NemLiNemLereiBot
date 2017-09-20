import yaml
import time
import logging
from praw import Reddit
from .pluginmanager import PluginManager
from .database import Database
from .helpers import url_matches_plugin, get_archiveis_url, render_template
from .summarizer import Summarizer
from .database.helpers import submission_exists, add_submission, update_submission_status,\
    get_submissions_by_status, article_exists, add_article


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class RedditBot:
    def __init__(self):
        self.config = self.load_config()

    def load_config(self, config_file='config.yml'):
        with open(config_file, 'r') as file:
            config = yaml.load(file)
        return config

    def setup_plugins(self):
        self.plugin_manager = PluginManager()

    def setup_reddit(self):
        self.reddit = Reddit(**self.config['reddit'])

    def setup_database(self):
        database = Database(**self.config['database'])
        database.connect()
        database.create_tables()
        self.database = database.session

    def setup_summarizer(self):
        self.summarizer = Summarizer(**self.config['summarizer'])

    def watch_subreddits(self):
        self.setup_plugins()
        self.setup_reddit()
        self.setup_database()

        subreddits_list = '+'.join(self.config['bot']['subreddits'])
        subreddits = self.reddit.subreddit(subreddits_list)
        for submission in subreddits.stream.submissions():
            logging.info('Found new submission: {}'.format(submission.id))
            if url_matches_plugin(self.plugin_manager, submission.url)\
               and not submission_exists(self.database, submission.id):
                logging.info('Submission url matches, saving to database: {}'.format(submission.id))
                add_submission(self.database, submission.id, submission.url)

    def fetch_articles(self):
        self.setup_plugins()
        self.setup_database()
        self.setup_summarizer()
        summarize = self.summarizer.summarize

        while True:
            submissions = get_submissions_by_status(self.database, 'TO_FETCH')
            for submission in submissions:
                if not article_exists(self.database, submission.id):
                    plugin_name = url_matches_plugin(self.plugin_manager, submission.url)
                    logging.info('Fetching article: {} | Plugin: {}'.format(submission.url, plugin_name))
                    plugin = self.plugin_manager.get_plugin(plugin_name)
                    article_metadata = plugin.get_article_metadata(
                        submission.url)

                    """A API do archive.is não responde quando feita a partir da Amazon AWS.
                    Eu gostava dessa feature, que pena, comentei para resolver isso depois."""

                    #archiveis_link = get_archiveis_url(submission.url)

                    article = {'submission_id': submission.id,
                               'subtitle': article_metadata['subtitle'],
                               'date_published': article_metadata['date_published'],
                               'summary': summarize(article_metadata['content'])}
                               #'archiveis_link': archiveis_link}

                    add_article(Session=self.database, **article)
                    update_submission_status(
                        self.database, submission.base36_id, 'TO_REPLY')
            self.database.commit()
            time.sleep(5)

    def reply_submissions(self):
        self.setup_reddit()
        reddit = self.reddit
        self.setup_database()

        while True:
            submissions = get_submissions_by_status(self.database, 'TO_REPLY')
            for submission in submissions:
                article = article_exists(self.database, submission.id)
                if article:
                    logging.info('Replying to submission: {}'.format(submission.base36_id))
                    reply = render_template('summary.md', article=article)
                    submission_to_reply = reddit.submission(
                        id=submission.base36_id)
                    submission_to_reply.reply(reply)
                    update_submission_status(
                        self.database, submission.base36_id, 'DONE')
                    time.sleep(2)
            self.database.commit()
            time.sleep(5)
            
