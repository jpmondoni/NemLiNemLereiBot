import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--watch', help='Watch subreddits',
                        action='store_true')
    parser.add_argument(
        '--fetch', help='Fetch articles & Summarize', action='store_true')
    parser.add_argument('--reply', help='Reply submissions',
                        action='store_true')

    from NemLiNemLereiBot import RedditBot

    args = parser.parse_args()

    if args.watch:
        RedditBot().watch_subreddits()
    elif args.fetch:
        RedditBot().fetch_articles()
    elif args.reply:
        RedditBot().reply_submissions()


if __name__ == '__main__':
    main()
