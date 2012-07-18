import config
from util import *

def try_file(name, root):
    filepath = os.path.abspath(os.path.join(root, name.strip('/\\')))
    return os.path.exists(filepath) and os.path.isfile(filepath)

# Static fallback
@bottle.route('/<filename:path>')
def static(filename):
    # Try first with the site-specific files
    root = config.static_path
    if try_file(filename, root):
        return bottle.static_file(filename, root)
    # Try last with the included static files
    root = spromata_static_path()
    if try_file(filename, root):
        return bottle.static_file(filename, root)
    else:
        return bottle.HTTPError(404, "File does not exist.")

