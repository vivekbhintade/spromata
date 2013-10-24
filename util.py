import bottle
from collections import defaultdict
import hashlib
from functools import partial
import boto
import boto.ses
import math
import time
import requests
import json
import bson.json_util
import datetime
import string
import random
import urllib2
import urllib
import sys
import os
from spromata.utils.document import *
from spromata.utils.pretty_date import *
from spromata.utils.make_keywords import *

import config
def spromata_root(): return os.path.dirname(__file__)
def spromata_static_path(): return os.path.join(spromata_root(), 'static')

def log(s): sys.stderr.write(str(s).strip() + '\n')

def password_hash(s): return hashlib.sha512(s).hexdigest()

def send_mailgun_mail(to_address, from_address, subject, message_text, message_html=None):
    message_data = {
        'to': to_address,
        'from': from_address,
        'subject': subject,
        'text': message_text,
    }
    if message_html: message_data['html'] = message_html
    print requests.post("https://api.mailgun.net/v2/%s.mailgun.org/messages" % config.mailgun_api_account, auth=('api', config.mailgun_api_key), data=message_data)

if hasattr(config, 'aws_access_key'): ses_conn = boto.ses.SESConnection(config.aws_access_key, config.aws_secret_key)
def send_ses_mail(to_address, from_address, subject, message_text, message_html=None):
    return ses_conn.send_email(from_address, subject, message_text, to_address, html_body=message_html)
def send_ses_raw_mail(to_address, from_address, message_body):
    return ses_conn.send_raw_email(message_body, source=from_address, destinations=[to_address])

send_mail = send_ses_mail

class Context(Document):
    private = ['config']

def start_context():
    context = Context()
    context['messages'] = []
    context['errors'] = []
    context['config'] = config
    context['now'] = datetime.datetime.now(pytz.utc)
    context['timestamp'] = time.mktime(datetime.datetime.now(pytz.utc).timetuple())
    return context

def google_image_search(s):
    response = requests.get(
        'https://ajax.googleapis.com/ajax/services/search/images',
        params={'v': '1.0', 'q': s},
        headers={'Referer': 'http://sprobertson.com/'}
    )
    image_url = random.choice(response.json['responseData']['results'])['url']
    return image_url

# Helper for defining routes from a route map
# The map looks like: {'/': index}
# With optional prefixes #post, >put, and Xdelete
# e.g. {'#/login': do_login}
def make_route_callbacks(b, route_map):
    for route in route_map:
        path, callback = route
        print "PATH: %s" % path
        if path.startswith('#'):
            b.post(path[1:])(callback)
        elif path.startswith('X'):
            b.delete(path[1:])(callback)
        elif path.startswith('>'):
            b.put(path[1:])(callback)
        else:
            b.get(path)(callback)

if hasattr(config, 'aws_access_key'): s3_conn = boto.connect_s3(config.aws_access_key, config.aws_secret_key)
def s3_url(bucket_name, file_name):
    return ('http://%s.s3.amazonaws.com/%s' % (bucket_name, file_name)).lower()
def upload_to_s3(bucket_name, file, filename=None, metadata={}):
    bucket = s3_conn.get_bucket(bucket_name)
    if not filename: filename = file.name.split('/')[-1]
    filename = filename.lower()
    file_key = bucket.new_key(filename);
    #file_encoded = base64.b64encode(file.read())
    #file_key.set_contents_from_string(file_encoded)
    for k, v in metadata.items():
        print 'Setting: %s, %s' % (k, v)
        file_key.set_metadata(k, v)
    file_key.set_contents_from_file(file)
    #file_key.make_public()
    return s3_url(bucket.name, file_key.name)

# Some things just gotta hang out at the bottom

from templating import *

