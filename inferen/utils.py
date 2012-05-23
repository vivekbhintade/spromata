import requests

def send_mail(to_address, from_address, subject, message_text, message_html):
    print requests.post("https://api.mailgun.net/v2/hjklist.mailgun.org/messages", auth=('api', 'key-8vv5qzxw1hzlnhssb07e-oo35eb8hwe2'), data={
        'to': to_address,
        'from': from_address,
        'subject': subject,
        'text': message_text,
        'html': message_html
    })
