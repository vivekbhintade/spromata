debug = True

site_name = 'spromata_app'
site_title = "My Spromata App"

mongo_host = 'localhost'
mongo_port = None
mongo_db = site_name

server_host = '0.0.0.0'
server_port = 8888
server_type = 'gevent'

static_path = 'static'
base_url = 'http://localhost:%s' % server_port

from spromata.tokens import generate_token
session_secret = '.'.join([site_name, generate_token(16)])
