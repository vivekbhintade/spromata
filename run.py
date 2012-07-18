from server import *
bottle.debug=config.debug
bottle.run(host=config.server_host, port=config.server_port, server=config.server_type, reloader=config.reloader)
