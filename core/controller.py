from spromata.util import *
from spromata.core.data import *
from spromata.core.auth import *

@bottle.hook('before_request')
def create_context(): bottle.response.context = add_session(start_context())

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

def logout(**context):
    if context['session']:
        session = context['session']
        sessions.remove(user=session.user.id)
        bottle.response.delete_cookie("user", secret=config.session_secret)
        bottle.response.delete_cookie("token", secret=config.session_secret)
    return bottle.redirect('/')

def send_email(email_attrs):
    posted = requests.post(("https://api.mailgun.net/v2/sasaafrica.mailgun.org/messages"),
        auth=("api", "key-1h3jll-ukzzvret0rpn9tt6ruapva386"),
        data=email_attrs)

