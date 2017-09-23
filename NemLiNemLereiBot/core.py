import yaml
import time
import logging
from praw import Reddit
from praw.exceptions import APIException
from jinja2 import TemplateError
from .pluginmanager import PluginManager
from .database import Database
from .helpers import render_template
from .summarizer import Summarizer
from .database.helpers import (add_submission, get_submissions,
                               add_article, get_article)


logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")


class RedditBot:

    def __init__(self, mode='watch'):
        logging.info('The Bot is now starting.'.format(mode))
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
        database.connect()
        database.create_tables()
        self._database = database.session
        logging.info('Database is now set up.')

    def _setup_summarizer(self):
        logging.info('Loading summarizer.')
        self._summarizer = Summarizer(**self._config['summarizer']).summarize
        logging.info('Summarizer loaded.')

    def watch_subreddits(self):

        logging.info('Watching for new submissions.')

        # Caso haja mais de um subreddit, junta todos, exemplo:
        # brasil+portugal+BrasildoB, assim o Bot irá buscar
        # por novas submissions de cada um de uma vez só.

        subreddits_list = '+'.join(self._config['bot']['subreddits'])
        subreddits = self._reddit.subreddit(subreddits_list)

        # Looping infinito que assiste cada submission, verifica
        # se a URL da submissão coincide com algum padrão
        # definido por um plugin e armazena no banco de dados.

        for submission in subreddits.stream.submissions():
            logging.info('Found new submission: {}'.format(submission.id))
            if self._plugin_manager.url_matches_plugin(submission.url):
                logging.info('Submission url matches, saving to database: {}'
                             .format(submission.id))
                add_submission(self._database,
                               base36_id=submission.id,
                               url=submission.url)

    def fetch_articles(self):

        # Loopíng infinito com intervalo de 5 segundos, busca por
        # submissões com status 'TO_FETCH', verifica de qual plugin
        # o padrão da URL coincide, invoca o plugin e passa a URL
        # para o método get_article_metadata do plugin, esperando
        # um dicionário contendo os metadados do artigo, invoca
        # o summarizer para resumir o conteúdo extraído pelo plugin,
        # armazena no banco de dados o resultado e atualiza o status
        # para 'TO_REPLY'

        logging.info('Looking for pending articles to fetch data from.')

        while True:
            submissions = get_submissions(self._database,
                                          status='TO_FETCH')
            for submission in submissions:
                # ------

                # Por algum motivo as linhas a seguir não me agradam,
                # mas vou deixar para outro alguém ou eu em outra
                # oportunidade refatorar melhor.
                try:
                    plugin_name = (self._plugin_manager
                                   .url_matches_plugin(self._plugin_manager,
                                                       submission.url))
                    plugin = self._plugin_manager.get_plugin(plugin_name)

                    logging.info('Fetching article for submission '
                                 'base36_id: {} with plugin: {}'
                                 .format(submission.base36_id,
                                         plugin_name))

                    article_metadata = plugin.get_article_metadata(
                        submission.url
                    )

                    article = {'submission_id': submission.id,
                               'subtitle': article_metadata['subtitle'],
                               'date_published': article_metadata['date_published'],
                               'summary': self._summarizer(article_metadata['content'])}

                    logging.info('Saving article metadata to database.')
                    add_article(Session=self._database,
                                **article)
                    submission.status = 'TO_REPLY'
                    self._database.commit()
                except Exception as e:
                    logging.error(e)
                    submission.status = 'FETCH_ERROR'
                    self._database.commit()

                    # ------
            logging.info('No pending articles found, '
                         'waiting 5 seconds before looking up again.')
            self._database.commit()
            time.sleep(5)

    def reply_submissions(self):

        logging.info('Looking for new submissions to reply to.')

        # Busca em loop infinito com intervalo de 5 segundos cada query
        # renderiza com o jinja2 e responde a submission.

        while True:
            submissions = get_submissions(self._database,
                                          status='TO_REPLY')
            for submission in submissions:
                article = get_article(self._database,
                                      submission_id=submission.id)
                try:
                    reply = render_template('summary.md',
                                            article=article)
                    to_reply = self._reddit.submission(id=submission.base36_id)
                    to_reply.reply(reply)
                    submission.status = 'DONE'
                    self._database.commit()
                    logging.info('Replied to submission: {}'
                                 .format(submission.base36_id))
                except (TemplateError, APIException) as e:
                    logging.error('Tried to reply to submission {} but failed!'
                                  .format(submission.base36_id))
                    logging.error(e)
                    submission.status = 'REPLY_ERROR'
                    self._database.commit()
            self._database.flush()
            time.sleep(5)
