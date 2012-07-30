import xml.dom.minidom

chat_xml = xml.dom.minidom.parse('/Users/sean/b.xml')

def parse_messages(c):
    messages = c.getElementsByTagName('message')
    message_docs = []
    for message in messages:
        message_docs.append({
            'sender': message.getAttribute('sender'),
            'text': strings_in(message),
        })
    return message_docs

def strings_in(n):
    s = ""
    if n.hasChildNodes():
        for c in n.childNodes:
            s += strings_in(c)
    else:
        s += n.nodeValue or ''
    return s
