#! /usr/bin/env python3
import click
from NemLiNemLereiBot import RedditBot

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
