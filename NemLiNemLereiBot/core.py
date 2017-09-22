import yaml
import time
import logging
from praw import Reddit
from .pluginmanager import PluginManager
from .database import Database
from .helpers import url_matches_plugin, render_template
from .summarizer import Summarizer
from .database.helpers import add_submission, update_submission_status,\
    get_submissions_by_status, add_article


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

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

        # Caso haja mais um subreddit, junta todos exemplo:
        # brasil+portugal+BrasildoB, assim o Bot irá buscar
        # por novas submissões de cada um.

        logging.info('Watching for new submissions.')

        subreddits_list = '+'.join(self._config['bot']['subreddits'])
        subreddits = self._reddit.subreddit(subreddits_list)

        # Looping infinito que assiste cada submissão, verifica
        # se a URL da submissão coincide com algum padrão 
        # definido por um plugin e armazena no banco de dados
        # com o status 'TO_FETCH' para ser processado pelo fetch_articles.

        for submission in subreddits.stream.submissions():
            logging.info('Found new submission: {}'.format(submission.id))
            if url_matches_plugin(self._plugin_manager, submission.url):
                logging.info('Submission url matches, saving to database: {}'.format(submission.id))
                add_submission(self._database, submission.id, submission.url)

    def fetch_articles(self):

        # Loopíng infinito com intervalo de 5 segundos, busca por
        # submissões com status 'TO_FETCH', verifica de qual plugin
        # o padrão da URL coincide, invoca o plugin e passa a URL
        # para o método get_article_metadata do plugin, esperando
        # um dicionário contendo os metadados do artigo, invoca 
        # o summarizer para resumir o conteúdo extraído pelo plugin,
        # armazena no banco de dados o resultado e atualiza o status
        # para 'TO_REPLY'

        logging.info('Looking up for pending articles.')

        while True:
            submissions = get_submissions_by_status(self._database, 'TO_FETCH')
            for submission in submissions:
                # ------

                # Por algum motivo as linhas a seguir não me agradam, mas vou deixar
                # para outro alguém ou eu em outra oportunidade refatorar melhor.
                try:
                    plugin_name = url_matches_plugin(self._plugin_manager, submission.url)
                    plugin = self._plugin_manager.get_plugin(plugin_name)

                    logging.info('Fetching article for submission base36_id: {} with plugin: {}'.format(submission.base36_id, plugin_name))

                    article_metadata = plugin.get_article_metadata(submission.url)

                    article = {'submission_id': submission.id,
                            'subtitle': article_metadata['subtitle'],
                            'date_published': article_metadata['date_published'],
                            'summary': self._summarizer(article_metadata['content'])}

                    logging.info('Saving article metadata to database.')
                    add_article(Session=self._database, **article)
                    update_submission_status(self._database, submission.base36_id, 'TO_REPLY')
                except Exception as e:
                    logging.error(e)
                    update_submission_status(self._database, submission.base36_id, 'ERROR')

                    # ------
            logging.info('No pending articles found, waiting 5 seconds before looking up again.')
            self._database.commit()
            time.sleep(5)

    def reply_submissions(self):

        # Busca por submissões com o status 'TO_REPLY', puxa os metadados do
        # artigo amazenados do banco de dados, renderiza o template da resposta
        # com o Jinja2, responde a publicação pelo id único em base36 gerado
        # pelo Reddit e atualiza o status para 'DONE'. A preferência pelo Jinja2
        # deve-se ao fato de ser uma solução já muito bem desenvolvida para 
        # renderização de templates, muito mais simples e fácil de usar que
        # reinventar a roda.
        # O tempo de 2 segundos após a resposta é o limite imposto pela API do Reddit.

        logging.info('Looking up for submissions to reply')

        while True:
            submissions = get_submissions_by_status(self._database, 'TO_REPLY')
            for submission in submissions:
                article = article_exists(self._database, submission.id)
                if article:
                    logging.info('Replying to submission: {}'.format(submission.base36_id))
                    reply = render_template('summary.md', article=article)
                    submission_to_reply = self._reddit.submission(id=submission.base36_id)
                    submission_to_reply.reply(reply)
                    update_submission_status(self._database, submission.base36_id, 'DONE')
                    time.sleep(2)

            logging.info('No pending submissions found, waiting 5 seconds before looking up again.')
            self._database.commit()
            time.sleep(5)
            
