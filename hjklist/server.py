import bottle
import pymongo
import json
from meta_server import *
from data import *
from utils import *

#-----
# Main views
#-----

def index(**context):
    session = context['session']
    root = nodes.get(user=session.user.id, name='root')
    root['items'] = root.to_
    context['root'] = pymongo_to_json(make_node_rep(root, 2))
    return render('index', **context)

show_login = renderer('login')
def do_login(**context):
    context['submitted']['username'] = username = bottle.request.forms.get('username')
    context['submitted']['password'] = password = bottle.request.forms.get('password')
    if username and password:
        user = users.auth(username, password)
        if user:
            token = generate_token()
            sessions.new(user=user.id, token=token)
            bottle.response.set_cookie("user", user.id, secret=config.secret)
            bottle.response.set_cookie("token", token, secret=config.secret)
            if bottle.request.query.next:
                return bottle.redirect(bottle.request.query.next)
            return bottle.redirect("/")
        else:
            context['errors'].append("Incorrect username or password.")
            return show_login(**context)
    return show_login(**context)

def logout(**context):
    if context['session']:
        session = context['session']
        sessions.remove(user=session.user.id)
        bottle.response.delete_cookie("user", secret=config.secret)
        bottle.response.delete_cookie("token", secret=config.secret)
    return bottle.redirect('/')

show_signup = renderer('signup')
def do_signup(**context):
    session = context['session']
    context['submitted']['username'] = username = bottle.request.forms.get('username') or ''
    context['submitted']['email'] = email = bottle.request.forms.get('email') or ''
    context['submitted']['agree_terms'] = agree_terms = bottle.request.forms.get('agree_terms') or False
    password = bottle.request.forms.get('password')
    if bottle.request.forms:
        if not username: context['errors'].append("Please enter a username.")
        elif users.exists(username=username): context['errors'].append("This username is in use.")
        if not email: context['errors'].append("Please enter an email address.")
        elif users.exists(email=email): context['errors'].append("This email address is in use.")
        if not password: context['errors'].append("Please enter a password.")
        if len(context['errors']) > 1:
            return show_signup(**context)
        # Set up new user
        verification_code = generate_token(20)
        user = users.new(username=username, password=password, email=email, verification=verification_code)
        verification_url = config.base_url + "/verify?user=%s&code=%s" % (username, verification_code)
        send_mail(user.email, 'qrblender@gmail.com', 'Welcome to hjklist!', 
            'Verify your email address by visiting: %s' % verification_url,
            'Verify your email address by visiting: <a href="%s">%s</a>' % (verification_url, verification_url))
        # Set them up a root node
        root = nodes.new(user=session.user.id, name='root')
        welcome = nodes.new(name='Welcome to hjklist!')
        root.to_ = welcome
        context['messages'].append("Thank you for signing up. Please check your email for a verification link.")
        return show_login(**context)
    else:
        return show_signup(**context)

#-----
# Node views
#-----

def show_node(node_id, **context):
    node = nodes.get(_id=node_id)
    node_rep = make_node_rep(node, 2)
    return pymongo_to_json(node_rep)

def new_node(**context):
    new_node = nodes.new(name=bottle.request.json.get('name'))
    from_node = nodes.get(_id=bottle.request.json.get('from_'))
    from_node.to_ = new_node
    return pymongo_to_json(make_node_rep(new_node))

def update_node(node_id, **context):
    node = nodes.get(_id=node_id)
    new_name = bottle.request.json.get('name')
    new_from_ = bottle.request.json.get('from_')
    if new_name:
        node['name'] = new_name
        nodes.update(**node)
    if new_from_:
        edges.remove(to_=node.id)
        from_node = nodes.get(_id=new_from_)
        node.from_ = from_node

def delete_node(node_id, **context):
    node = nodes.get(_id=node_id)
    edges.remove(to_=node.id)
    edges.remove(from_=node.id)
    nodes.remove(**node)

#-----
# Route configuration
#-----

_node_id_ = "<node_id:re:[a-zA-Z0-9]+>"
route_map = {
    '/': [authenticate, index],
    '/signup': show_signup,
    '#/signup': do_signup,
    '/login': show_login,
    '#/login': do_login,
    '/logout': logout,
    '#/new': [authenticate, new_node],
    '/'+_node_id_: [authenticate, show_node],
    '>/'+_node_id_: [authenticate, update_node],
    'X/'+_node_id_: [authenticate, delete_node],
}

# Define routes from the route map
def make_route_callback(callback):
    if type(callback) == list: callback = partial(*callback)
    def wrapper(**context):
        return callback(**get_session(**start_context(**context)))
    return wrapper

for route in route_map.items():
    path, callback = route
    if path.startswith('#'):
        bottle.post(path[1:])(make_route_callback(callback))
    elif path.startswith('X'):
        bottle.delete(path[1:])(make_route_callback(callback))
    elif path.startswith('>'):
        bottle.put(path[1:])(make_route_callback(callback))
    else:
        bottle.get(path)(make_route_callback(callback))

# Static fallback
@bottle.route('/<filepath:path>')
def static_file(filepath):
    return bottle.static_file(filepath, root='.')

# Run the server
bottle.debug(config.debug)
bottle.run(server=config.server, host='0.0.0.0', port=80, reloader=config.debug)

