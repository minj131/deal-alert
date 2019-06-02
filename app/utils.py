#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import os
from flask import Flask
from flask_pymongo import PyMongo, MongoClient

#----------------------------------------------------------------------------#
# App Config
#----------------------------------------------------------------------------#
app = Flask(__name__)
app.config.from_object('config')


def get_db_handle(type):
    """Returns db handle of type.

    Keyword arguments:
    type -- 'keywords' or 'users'
    """
    client = MongoClient(os.environ.get('MONGO_DB'))
    if type == 'keywords':
        return client['deal-alert'].keywords
    elif type == 'users':
        return client['deal-alert'].users
    else:
        print('Cannot find db handle with type \'{}\''.format(type))
        raise NameError

def update_keywords_doc(db, id, email, price, date):
    """Updates doc and returns True if successful

    Keyword arguments:
    db -- db handle
    id -- keywords id to use for lookup
    email -- email of user
    price -- (optional) max price can be set to None
    date -- date created
    """
    try:
        db.update_one({'keyword': id}, {
            '$push': {
                'users': {
                    'email': email,
                    'price': price,
                    'notified': False,
                    'dateCreatred': date,
                    'lastTimeNotified': '',
                }
            }
        }, upsert=True)
        return True
    except:
        return False

def update_users_doc(db, id, keywords_id, price, date):
    """Updates doc and returns True if successful

    Keyword arguments:
    db -- db handle
    id -- users id to use for lookup
    keywords -- keywords of user
    price -- (optional) max price can be set to None
    date -- date created
    """
    try:
        db.update_one({'email': id}, {
            '$inc': {
                'numKeywords': 1
            },
            '$push': {
                'keywords': {
                    'keywords_id': keywords_id,
                    'price': price,
                    'notified': False,
                    'dateCreatred': date,
                    'lastTimeNotified': '',
                }
            }
        }, upsert=True)
        return True
    except:
        return False