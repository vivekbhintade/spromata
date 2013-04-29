from spromata.util import *
from spromata.core.auth import *

import cgi
def sanitize(s):
    if isinstance(s, str):
        return cgi.escape(s)
    return s

@bottle.hook('before_request')
def create_context(): bottle.response.context = add_session(start_context())
@bottle.hook('before_request')
def sanitize_query(): bottle.response.context.submitted.update(dict([(k, sanitize(v)) for k, v in bottle.request.query.items()]))
@bottle.hook('before_request')
def sanitize_forms(): bottle.response.context.submitted.update(dict([(k, sanitize(v)) for k, v in bottle.request.forms.items()]))

