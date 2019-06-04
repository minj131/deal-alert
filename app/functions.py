#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import praw
import os
import logging
import datetime
from flask import Flask
from flask_pymongo import PyMongo, MongoClient
import coloredlogs, logging

# Local Imports
from app import utils

#----------------------------------------------------------------------------#
# App Config
#----------------------------------------------------------------------------#
app = Flask(__name__)
app.config.from_object('config')


reddit = praw.Reddit(client_id=os.environ.get('CLIENT_ID'),
                     client_secret=os.environ.get('CLIENT_SECRET'),
                     redirect_uri=os.environ.get('REDIRECT_URI'),
                     user_agent='testscript by /u/ioeatcode',
                     )

def register_keywords_user(email, keywords, price):
    """Register users then keywords and creates/updates doc

    Keyword arguments:
    email - email for user
    keywords - string of keywords
    price -- (optional) max price can be set to None
    """

    logging.info('[INFO] Registering user email \'{}\' '.format(email))

    # create user doc if doesn't exist
    db = utils.get_db_handle('users')
    doc = db.find_one({ 'email': email })

    # metadata
    keywords_id = keywords.replace(" ", "_")
    date = str(datetime.datetime.now()).split('.')[0]
    num_keywords = 0
    list_keywords = []

    if doc == None:
        doc = db.insert_one({
            'email': email,
            'dateCreated': date,
            'numKeywords': num_keywords,
            'keywords': []
        })
        logging.info('[INFO] Creating new user doc {} with _id: {}'.format(email, doc.inserted_id))
    else:
        num_keywords = doc['numKeywords']
        list_keywords = doc['keywords']
        logging.info('[INFO] Found user doc \'{}\' with {} keywords'.format(email, num_keywords))

    # insert keywords info along in user doc
    max_keywords = 5
    if not utils.check_key_exists(list_keywords, keywords_id):
        if num_keywords < max_keywords:
            update =  utils.update_users_doc(db, email, keywords_id, price, date)
            if update:
                logging.info('[INFO] Successfully created or updated doc for \'{}\''.format(email))
            else:
                logging.info('[INFO] Error creating or updating doc for \'{}\''.format(email))
                return False, 'ERROR_CREATE_DOC'
        else:
            logging.info('[INFO] Unable to create doc for \'{}\''.format(email))
            logging.info('[INFO] Number of keywords exceed maximum of {}'.format(max_keywords))
            return False, 'MAX_KEYWORDS_LIMIT'
    else:
        logging.info('[INFO] Unable to create doc for \'{}\''.format(email))
        logging.info('[INFO] Duplicate key {} for user {}'.format(max_keywords, email))
        return False, 'ERROR_DUPE_KEY'

    logging.info('[INFO] Registering keywords \'{}\' for email \'{}\' with price \'{}\''.format(keywords, email, price))
    
    # create keywords doc if doesn't exist
    db = utils.get_db_handle('keywords')
    doc = db.find_one({ 'keyword': keywords_id })

    # keywords metadata
    date = str(datetime.datetime.now()).split('.')[0]

    if doc == None:
        doc = db.insert_one({ 
                'keyword': keywords_id,
                'subreddit': 'frugalmalefashion',
                'dateCreated': date,
                'users': [] 
                })
        logging.info('[INFO] Creating new keywords doc {} with _id: {}'.format(keywords_id, doc.inserted_id))
    else:
        logging.info('[INFO] Found keywords doc \'{}\''.format(keywords_id))

    # insert user info along in keyword doc
    update = utils.update_keywords_doc(db, keywords_id, email, price, date)
    if update:
        logging.info('[INFO] Successfully created or updated doc for \'{}\''.format(keywords_id))
    else:
        logging.error('[ERROR] Error creating or updating doc for \'{}\''.format(keywords_id))
        return False, 'ERROR_CREATE_DOC'
    
    return True, None

def getNewSubmissions():
    return reddit.subreddit('frugalmalefashion').new(limit=50)

# def searchSubmissions():
