import argparse

import libvoikko
import pg
import re

import utilities
import sanitation


def voikkoa(topic):
    voikko = libvoikko.Voikko('fi')
    
    words = topic.split()
    for word in words:
        print(voikko.analyze(word))


    print(topic)


def remove_smilies(topic):
    smilies = sanitation.get_smilies()
    for smiley in smilies:
        topic = topic.replace(smiley, ' ')
    return topic


def get_sanitized_topic(config):
    db = pg.DB(dbname=config['db_name'],
                host=config['db_host'],
                port=config['db_port'],
                user=config['db_user'],
                passwd=config['db_password'])

    posts = db.query('SELECT content '
                    'FROM posts '
                    'WHERE topic_id=$1 '
                    'ORDER BY post_number', 2728956).namedresult()

    topic = ' '.join([post.content for post in posts])

    topic = remove_smilies(topic)


    topic = re.sub(r',|!|\?|\.|\)|\(|\^|/|"|:|;|\[|\]|{|}', ' ', topic)

    # Remove multiple whitespaces
    topic = re.sub('\s+', ' ', topic).strip()

    return topic
    # TODO remove punctuation {} etc.


def main():
    parser = argparse.ArgumentParser(
        description='Tool for parsing post data from vauva.fi forum')
    parser.add_argument(
        '-cp', metavar='config_path', type=str,
        help='path to the configuration file of the parser')
    args = parser.parse_args()
    config = utilities.get_configuration(args.cp)

    topic = (get_sanitized_topic(config))
    voikkoa(topic)

if __name__ == '__main__':
    main()
