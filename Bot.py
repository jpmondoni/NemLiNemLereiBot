#! /usr/bin/env python3
import click
from NemLiNemLereiBot import RedditBot

# O cli demora a responder alguns segundos caso eu importe o RedditBot aqui,
# sei que é uma péssima prática mas não consegui resolver de outra forma e
# acabei importando antes de instanciar o objeto em cada função, considerando
# que apenas uma função será executada por processo, logo o RedditBot só será
# importado uma vez e não deverá haver problemas. Se você conseguir resolver
# de um jeito DRY, só commitar e pull request! :)

@click.group()
def cli():
    pass

@cli.command(short_help='Watch for new submissions')
def watch():
    Bot = RedditBot(mode='watch')
    Bot.watch_subreddits()
@cli.command(short_help='Fetch & summarize articles')
def fetch():
    Bot = RedditBot(mode='fetch')
    Bot.fetch_articles()

@cli.command(short_help='Render template & reply')
def reply():
    Bot = RedditBot(mode='reply')
    Bot.reply_submissions()

if __name__ == '__main__':
    cli()
