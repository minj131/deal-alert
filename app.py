#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

# 3rd Party Imports
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo, MongoClient
from werkzeug.exceptions import HTTPException, NotFound
import logging
from logging import Formatter, FileHandler
import coloredlogs, colorama
import sass
import os
import sys
import time
import atexit

# Local Imports
from app import functions


#----------------------------------------------------------------------------#
# Logging
#----------------------------------------------------------------------------#

# Create a logger object.
coloredlogs.install(level='DEBUG', fmt='%(asctime)s -- %(message)s')


#----------------------------------------------------------------------------#
# App Config
#----------------------------------------------------------------------------#

app = Flask(__name__, static_url_path='/static', static_folder='static')
sass.compile(dirname=('static/scss', 'static/css'))
app.config.from_object('config')

# # Register MongoDB
# connection = MongoClient(os.environ.get('MONGO_DB_HOST'), os.environ.get('MONGO_DB_PORT'))
# users = connection[os.environ.get('MONGO_DB_USERS')]
# # users.authenticate(os.environ.get('MONGO_DB_USER'), os.environ.get('MONGO_DB_PASS'))
# keywords = connection[os.environ.get('MONGO_DB_KEYWORDS')]
# # keywords.authenticate(os.environ.get('MONGO_DB_USER'), os.environ.get('MONGO_DB_PASS'))

# Set level paths for local imports
sys.path.insert(0, '/app/')

#----------------------------------------------------------------------------#
# Controllers
#----------------------------------------------------------------------------#

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        email = request.form['email']
        keywords = request.form['keywords']
        price = request.form['price']

        missingFields = []
        if not email:
            missingFields.append(email)
        if not keywords:
            missingFields.append(keywords)
        if not isinstance(price, int) or price <= 0:
            missingFields.append(price)
        if len(missingFields) > 0:
            app.register_error_handler(400, handle_bad_request)

        _, err = functions.register_keywords_user(email, keywords, price)
        if not err:
            return redirect(url_for('success', email=email, keywords=keywords, price=price))
        else:
            return redirect(url_for('failure', reason=err))
    return render_template('pages/home.html')


@app.route('/success/email=<string:email>/keywords=<string:keywords>', defaults={'price': None})
@app.route('/success/email=<string:email>/keywords=<string:keywords>/price=<string:price>')
def success(email, keywords, price):
    return render_template('pages/success.html', email=email, keywords=keywords, price=price)


@app.route('/failure/reason=<string:reason>')
def failure(reason):
    # err messages dict
    return render_template('pages/failure.html', reason=reason)


# Error handlers.

@app.errorhandler(500)
def internal_error(error):
    return '500'


@app.errorhandler(404)
def not_found_error(error):
    return '404'

@app.errorhandler(HTTPException)
def handle_bad_request(error):
    return 'bad request!', 400

#----------------------------------------------------------------------------#
# Run
#----------------------------------------------------------------------------#

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# Register background scheduled cronjob
# cronjob = BackgroundScheduler()
# cronjob.add_job(functions.getNewSubmissions, trigger='interval', seconds=10)
# cronjob.add_job(func=functions.getNewSubmissions('buildapcsales'), trigger='interval', seconds=10)
# cronjob.start()

# Register tear down of scheduler on shutdown
# atexit.register(lambda: cronjob.shutdown())

if __name__ == '__main__':
    if os.environ.get('DEBUG_MODE'):
        host = os.environ.get('HOST', '127.0.0.1')
        port = int(os.environ.get('PORT', 8000))
        app.run(host=host, port=port)
    else:
        app.run()