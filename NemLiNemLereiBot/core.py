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
        self.mode = mode
        self._setup_logging()

        self._logger.info('The Bot is now starting in {} mode.'
                          .format(mode.upper()))
        self._load_config()

        # Carrega os módulos básicos
        self._setup_database()
        self._setup_plugins()
        # Configura apenas os módulos necessários para cada processo,
        # evitando que o Bot carregue tudo desnecessariamente.
        if mode in ['watch', 'reply']:
            self._setup_reddit()
        elif mode == 'fetch':
            self._setup_summarizer()

    def _setup_logging(self):
        fmt = "%(asctime)s [%(levelname)s] %(message)s"
        logging.basicConfig(level=logging.INFO,
                            format=fmt)
        logger = logging.getLogger('NemLiNemLereiBot')
        logs_folder = self._config['bot']['folders']['logs']
        log_file = logging.FileHandler('{}/{}.log'
                                       .format(logs_folder, self.mode))
        log_file.setFormatter(
            logging.Formatter(fmt)
        )
        logger.addHandler(log_file)
        self._logger = logger

    def _load_config(self):
        try:
            with open('config.yml', 'r') as file:
                self._config = yaml.load(file)
            self._logger.info('Loaded config file.')
        except Exception as e:
            self._logger.critical('Couldn\'t load config file.')
            self._logger.critical(e)
            raise

    def _setup_plugins(self):
        self._logger.info('Loading plugins.')
        self._plugin_manager = PluginManager()

    def _setup_reddit(self):
        try:
            self._reddit = Reddit(**self._config['reddit'])
            username = self._reddit.user.me()
            self._logger.info('Connected to Reddit as: {}.'
                              .format(username))
        except Exception as e:
            self._logger.critical('Couldn\'t connect to Reddit.')
            self._logger.critical(e)
            raise

    def _setup_database(self):
        try:
            database = Database(**self._config['database'])
            self._db = database
            self._logger.info('Connected to database: '
                              '{driver}://{username}@{host}:{port}/{database}'
                              .format_map(self._config['database']))
        except Exception as e:
            self._logger.critical('Couldn\'t connect to database.')
            self._logger.critical(e)
            raise

    def _setup_summarizer(self):
        self._logger.info('Loading summarizer.')
        self._summarize = Summarizer(**self._config['summarizer']).summarize
        self._logger.info('Summarizer loaded.')

    def watch(self):

        self._logger.info('Watching for new submissions.')

        subreddits_list = '+'.join(self._config['bot']['subreddits'])
        subreddits = self._reddit.subreddit(subreddits_list)

        while True:
            try:
                for submission in subreddits.stream.submissions():
                    self._logger.info('Found new submission: {}'
                                      .format(submission.id))
                    if self._plugin_manager.url_matches_plugin(submission.url):
                        self._logger.info('Adding submission: {} '
                                          'to database if not already added.'
                                          .format(submission.id))
                        self._db.add_submission(base36_id=submission.id,
                                                url=submission.url)
            except Exception as e:
                self._logger.error('Tried to read submissions stream'
                                   ' but failed, trying again!')
                self._logger.error(e)
            time.sleep(5)

    def fetch(self):

        self._logger.info('Looking for pending articles to fetch data from.')

        while True:
            submissions = self._db.get_submissions(status='TO_FETCH')
            for submission in submissions:
                try:
                    plugin_name = (self._plugin_manager
                                   .url_matches_plugin(submission.url))
                    plugin = (self._plugin_manager
                              .get_plugin(plugin_name))

                    self._logger.info('Fetching article for submission '
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
                        self._logger.error('Tried to capture the'
                                           ' page but failed!')
                        self._logger.error(e)

                    self._db.add_article(submission_id=submission.id,
                                         **metadata)

                    self._logger.info('Saving article metadata to database.')

                    submission.status = 'TO_REPLY'
                    self._db.session.commit()
                except Exception as e:
                    self._logger.error(e)
                    submission.status = 'FETCH_ERROR'
                    self._db.session.commit()
            self._db.session.commit()
            time.sleep(5)

    def reply(self):

        self._logger.info('Looking for new submissions to reply to.')

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
                    self._db.session.commit()
                    self._logger.info('Replied to submission: {}'
                                      .format(submission.base36_id))
                except Exception as e:
                    self._logger.error('Tried to reply to '
                                       'submission {} but failed!'
                                       .format(submission.base36_id))
                    self._logger.error(e)
                    submission.status = 'REPLY_ERROR'
                    self._db.session.commit()
            self._db.session.commit()
            time.sleep(5)
