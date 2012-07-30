import imaplib
import pickle
import email
from collections import defaultdict
import re

emails = defaultdict(list)

print "Connecting to GMail"
gm = imaplib.IMAP4_SSL('imap.gmail.com')
gm.login('sprobertson', 'mock36geo')
gm.select('PKS')

print "Selecting messages"
r, its = gm.search(None, 'ALL')
itis = its[0].split()
n = 0

class BadSign(Exception): pass
bad_signs = [
    lambda l: not l,
    lambda l: l.startswith('>'),
    lambda l: re.match("^.*On.*(\n)?wrote:$", l),
    lambda l: re.match("-+Original Message", l),
    lambda l: re.match("^From:", l),
    lambda l: re.match("^Date:", l),
    lambda l: re.match("^Sent from", l),
]

def extract_email(en):
    g = re.match(".*<(.*)>", en)
    if g: en = g.group(1)
    return en.lower().strip()

print "Parsing..."
for iti in reversed(itis):
    it = gm.fetch(iti, '(RFC822)')
    m = email.message_from_string(it[1][0][1])
    # loop through message data to get text
    m_text = ""
    for p in m.walk():
        if p.get_content_type()=='text/plain':
            m_text += p.get_payload()
    # clear up message text (mostly get rid of \r)
    m_text = m_text.replace('\r','').replace('\n\n','\n')
    m_lines = []
    # loop through message lines to get rid of replies
    for l in m_text.split('\n'):
        l = l.strip()
        try:
            for bad_sign in bad_signs:
                if bad_sign(l):
                    raise BadSign
        except BadSign: break
        # Passed those checks? Great.
        m_lines.append(l)
    # Rejoin and rejoice
    m_text = '\n'.join(m_lines)
    # Identify sender
    m_from = extract_email(m['From'])
    emails[m_from].append(m_text)
    n += 1
    print n
    if n > 9000: break

print "Dumping extracted content..."
pickle.dump(emails, open('emails.p', 'wb'))
