import argparse

import libvoikko
import utilities
import pg

# voikko = libvoikko.Voikko('fi')

def get_sanitized_topic(config):
    db = pg.DB(dbname=config['db_name'],
                host=config['db_host'],
                port=config['db_port'],
                user=config['db_user'],
                passwd=config['db_password'])

    posts = db.query('SELECT content '
                    'FROM posts '
                    'WHERE topic_id=$1 '
                    'ORDER BY post_number', 2722541).namedresult()

    topic = ' '.join([post.content for post in posts])
    return topic
    # TODO remove smilies, punctuation .,;()[]{}!? etc.


def main():
    parser = argparse.ArgumentParser(
        description='Tool for parsing post data from vauva.fi forum')
    parser.add_argument(
        '-cp', metavar='config_path', type=str,
        help='path to the configuration file of the parser')
    args = parser.parse_args()
    config = utilities.get_configuration(args.cp)

    print(get_sanitized_topic(config))


if __name__ == '__main__':
    main()