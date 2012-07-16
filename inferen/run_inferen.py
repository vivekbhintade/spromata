from server import *
# Run the server
bottle.debug(config.debug)
bottle.run(server=config.server, host=config.host, port=config.port, reloader=config.debug)

