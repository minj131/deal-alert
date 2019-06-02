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
    numKeywords = 0

    if doc == None:
        doc = db.insert_one({
            'email': email,
            'dateCreated': date,
            'numKeywords': numKeywords,
            'keywords': []
        })
        logging.info('[INFO] Creating new user doc {} with _id: {}'.format(email, doc.inserted_id))
    else:
        numKeywords = doc['numKeywords']
        logging.info('[INFO] Found user doc \'{}\' with {} keywords'.format(email, numKeywords))

    # insert keywords info along in user doc
    maxKeywords = 5
    if numKeywords < maxKeywords:
        update =  utils.update_users_doc(db, email, keywords_id, price, date)
        if update:
            logging.info('[INFO] Successfully created or updated doc for \'{}\''.format(email))
        else:
            logging.info('[INFO] Error creating or updating doc for \'{}\''.format(email))
            return False, 'ERROR_CREATE_DOC'
    else:
        logging.info('[INFO] Unable to create doc for \'{}\''.format(email))
        logging.info('[INFO] Number of keywords exceed maximum of {}'.format(maxKeywords))
        return False, 'MAX_KEYWORDS_LIMIT'

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
