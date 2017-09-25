#! /usr/bin/env python3
import click
from NemLiNemLereiBot import RedditBot

@click.group()
def cli():
    pass

@cli.command(short_help='Watch for new submissions')
def watch():
    Bot = RedditBot(mode='watch')
    Bot.watch()
@cli.command(short_help='Fetch & summarize articles')
def fetch():
    Bot = RedditBot(mode='fetch')
    Bot.fetch()

@cli.command(short_help='Render template & reply')
def reply():
    Bot = RedditBot(mode='reply')
    Bot.reply()

if __name__ == '__main__':
    cli()
