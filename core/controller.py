from spromata.util import *
from spromata.core.data import *
from spromata.core.auth import *

import cgi
def sanitize(s):
    if isinstance(s, str):
        return cgi.escape(s)
    return s

@bottle.hook('before_request')
def create_context(): bottle.response.context = add_session(start_context())
#@bottle.hook('before_request')
def sanitize_forms(): bottle.request.forms = dict([(k, sanitize(v)) for k, v in bottle.request.forms.items()])
#@bottle.hook('before_request')
def sanitize_query(): bottle.request.query = dict([(k, sanitize(v)) for k, v in bottle.request.query.items()])

@bottle.get('/')
def index():
    return render('landing')

@bottle.get('/signup')
def show_signup(): return render('core/signup')

@bottle.get('/login')
def show_login(): return render('core/login')

@bottle.post('/signup')
def signup():
    context = bottle.response.context
    context['submitted']['name'] = name = bottle.request.forms.get('name')
    context['submitted']['email'] = email = bottle.request.forms.get('email')
    context['submitted']['password'] = password = bottle.request.forms.get('password')
    if not name: context['errors'].append("Please enter your name.")
    if not email: context['errors'].append("Please enter your email address.")
    elif users.exists(email=email): context['errors'].append("This email address is already in use!")
    if not password: context['errors'].append("Please enter a password.")
    if len(context['errors']) > 0:
        return render('core/signup')
    user = users.new(
        name = name,
        password = password_hash(password),
        email = email,
        verified = False,
        timestamp = bottle.response.context.timestamp
    )
    context['messages'].append("Thank you for signing up. When your account is verified you can log in here.")
    return render('core/login')

@bottle.post('/login')
def login():
    bottle.response.context['submitted']['email'] = email = bottle.request.forms.get('email')
    bottle.response.context['submitted']['password'] = password = bottle.request.forms.get('password')
    if email and password:
        user = users.auth(email, password_hash(password))
        if user:
            if not user.verified:
                bottle.response.context['errors'].append("Your account has not yet been verified.")
                return render('core/login')
            token = generate_token()
            sessions.new(user=user.id, token=token)
            bottle.response.set_cookie("user", user.id, secret=config.session_secret)
            bottle.response.set_cookie("token", token, secret=config.session_secret)
            if bottle.request.query.next:
                return bottle.redirect(bottle.request.query.next)
            return bottle.redirect("/")
        else:
            bottle.response.context['errors'].append("Incorrect email or password.")
            return render('core/login')
    else:
        bottle.response.context['errors'].append("Please fill in all required fields.")
        return render('core/login')
    return render('core/login')

@bottle.get('/logout')
def logout():
    context = bottle.response.context
    if context['session']:
        session = context['session']
        sessions.remove(user=session.user.id)
        bottle.response.delete_cookie("user", secret=config.session_secret)
        bottle.response.delete_cookie("token", secret=config.session_secret)
    return bottle.redirect('/')

@bottle.get('/forgot')
def show_forgot():
    return render('core/forgot')

@bottle.post('/forgot')
def setup_forgot():
    bottle.response.context['submitted']['username'] = username = bottle.request.forms.get('username')
    bottle.response.context['submitted']['email'] = email = bottle.request.forms.get('email')
    if username and email:
        user = users.get(username=username, email=email)
        if user:
            token = generate_token(10)
            user['reset_token'] = password_hash(token)
            reset_link = "%s/forgot/%s" % (config.base_url, token)
            users.update(**user)
            bottle.response.context['reset_link'] = reset_link
            bottle.response.context['forgotten_user'] = user
            email_text = render("emails/forgot.txt")
            email_html = render("emails/forgot.html")
            send_mail(user.email, config.from_email, "Reset your %s password" % config.site_title, email_text, email_html)
            bottle.response.context['messages'].append("An email with instructions to reset your password has been sent to <strong>%s</strong>." % user.email)
            return render("core/login")
    bottle.response.context['errors'].append("Invalid username or email.")
    return render('core/forgot')

@bottle.get('/forgot/<reset_token:re:[a-zA-Z0-9]+>')
def show_reset(reset_token):
    return render('core/reset')

@bottle.post('/forgot/<reset_token:re:[a-zA-Z0-9]+>')
def do_reset(reset_token):
    bottle.response.context['submitted']['username'] = username = bottle.request.forms.get('username')
    bottle.response.context['submitted']['email'] = email = bottle.request.forms.get('email')
    bottle.response.context['submitted']['password'] = password = bottle.request.forms.get('password')
    if username and email and password:
        user = users.get(username=username, email=email)
        if user:
            if user.reset_token == password_hash(reset_token):
                user['password'] = password_hash(password)
                del user['reset_token']
                users.update(**user)
                bottle.response.context['messages'].append("Successfully changed your password.")
                return render('core/login')
    bottle.response.context['errors'].append("Unable to verify account.")
    return render('core/reset')

