import yaml
import time
import logging
from praw import Reddit
from .pluginmanager import PluginManager
from .database import Database
from .helpers import render_template, percentage_decrease, archive_page
from .summarizer import Summarizer


class RedditBot:

    def __init__(self, mode='watch'):

        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s [%(levelname)s] %(message)s")

        logging.info('The Bot is now starting in {} mode.'.format(mode))
        self._config = self._load_config()

        # Carrega os módulos básicos
        self._setup_database()
        self._setup_plugins()
        # Configura apenas os módulos necessários para cada processo,
        # evitando que o Bot carregue tudo desnecessariamente.
        if mode in ['watch', 'reply']:
            self._setup_reddit()
        elif mode == 'fetch':
            self._setup_summarizer()

    def _load_config(self, config_file='config.yml'):
        logging.info('Loading config file.')
        with open(config_file, 'r') as file:
            config = yaml.load(file)
        return config

    def _setup_plugins(self):
        logging.info('Loading plugins.')
        self._plugin_manager = PluginManager()

    def _setup_reddit(self):
        logging.info('Connecting to Reddit.')
        self._reddit = Reddit(**self._config['reddit'])
        logging.info('Connected to Reddit!')

    def _setup_database(self):
        logging.info('Setting up database.')
        database = Database(**self._config['database'])
        self._db = database
        logging.info('Database is now set up.')

    def _setup_summarizer(self):
        logging.info('Loading summarizer.')
        self._summarize = Summarizer(**self._config['summarizer']).summarize
        logging.info('Summarizer loaded.')

    def watch_subreddits(self):

        logging.info('Watching for new submissions.')

        subreddits_list = '+'.join(self._config['bot']['subreddits'])
        subreddits = self._reddit.subreddit(subreddits_list)

        while True:
            try:
                for submission in subreddits.stream.submissions():
                    logging.info('Found new submission: {}'
                                 .format(submission.id))
                    if self._plugin_manager.url_matches_plugin(submission.url):
                        logging.info('Adding submission: {} '
                                     'to database if not already added.'
                                     .format(submission.id))
                        self._db.add_submission(base36_id=submission.id,
                                                url=submission.url)
            except Exception as e:
                logging.error('Tried to read submissions stream but failed,'
                              ' trying again!')
                logging.error(e)
            time.sleep(5)

    def fetch_articles(self):

        logging.info('Looking for pending articles to fetch data from.')

        while True:
            submissions = self._db.get_submissions(status='TO_FETCH')
            for submission in submissions:
                try:
                    plugin_name = (self._plugin_manager
                                   .url_matches_plugin(submission.url))
                    plugin = (self._plugin_manager
                              .get_plugin(plugin_name))

                    logging.info('Fetching article for submission '
                                 'base36_id: {} with plugin: {}.'
                                 .format(submission.base36_id,
                                         plugin_name))
                    metadata = plugin.extract_metadata(submission.url)
                    content = metadata['content']
                    summary = self._summarize(content)
                    decrease = percentage_decrease(content, summary)
                    metadata['summary'] = summary
                    metadata['percentage_decrease'] = decrease
                    metadata.pop('content')

                    try:
                        archiveis_url = archive_page(submission.url)
                        metadata['archiveis_url'] = archiveis_url
                    except Exception as e:
                        logging.error('Tried to capture the page but failed!')
                        logging.error(e)

                    self._db.add_article(submission_id=submission.id,
                                         **metadata)

                    logging.info('Saving article metadata to database.')

                    submission.status = 'TO_REPLY'
                    self._db.commit()
                except Exception as e:
                    logging.error(e)
                    submission.status = 'FETCH_ERROR'
                    self._db.commit()
            self._db.commit()
            time.sleep(5)

    def reply_submissions(self):

        logging.info('Looking for new submissions to reply to.')

        while True:
            submissions = self._db.get_submissions(status='TO_REPLY')
            for submission in submissions:
                article = self._db.get_article(submission_id=submission.id)
                try:
                    reply = render_template('summary.md',
                                            article=article)
                    to_reply = self._reddit.submission(id=submission.base36_id)
                    to_reply.reply(reply)
                    submission.status = 'DONE'
                    self._db.commit()
                    logging.info('Replied to submission: {}'
                                 .format(submission.base36_id))
                except Exception as e:
                    logging.error('Tried to reply to submission {} but failed!'
                                  .format(submission.base36_id))
                    logging.error(e)
                    submission.status = 'REPLY_ERROR'
                    self._db.commit()
            self._db.commit()
            time.sleep(5)
