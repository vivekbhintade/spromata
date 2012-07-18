from spromata.util import *
from spromata.core.data import *
from spromata.core.auth import *

@bottle.get('/admin')
@require_admin
def dashboard():
    all_users = users.fetch()
    bottle.response.context['all_users'] = all_users
    return render('admin/dashboard')

def filter_dict(d, keys):
    return dict([ (k,v) for k,v in d.items() if k in keys ])

@bottle.put('/admin/users/:user_id')
@require_admin
def update_user(user_id):
    user = users.get(_id=user_id)
    new_user_raw = bottle.request.json
    new_user = filter_dict(new_user_raw, ['name', 'email', 'type', 'verified'])
    new_user['verified'] = True if new_user['verified']==True else False
    if user and new_user:
        user.update(new_user)
        users.update(**user)
    return json.dumps(user.to_json())

