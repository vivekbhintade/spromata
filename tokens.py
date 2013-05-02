import random, string

token_chars = string.ascii_letters + string.digits
def generate_token(size=10):
    return ''.join(random.choice(token_chars) for x in range(size))

