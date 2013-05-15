from spromata.util import *
from spromata.core.auth import *

import cgi
def sanitize(s):
    if isinstance(s, list):
        return map(sanitize, s)
    if isinstance(s, str):
        return cgi.escape(s)
    return s

@bottle.hook('before_request')
def create_context():
    bottle.response.context = add_session(start_context())
@bottle.hook('before_request')
def sanitize_submitted():
    submitted = bottle.MultiDict()
    sanitized_query = dict([(k, sanitize(v)) for k, v in bottle.request.query.dict.items()])
    sanitized_forms = dict([(k, sanitize(v)) for k, v in bottle.request.forms.dict.items()])
    submitted.dict.update(sanitized_query)
    submitted.dict.update(sanitized_forms)
    bottle.response.context['submitted'] = submitted
