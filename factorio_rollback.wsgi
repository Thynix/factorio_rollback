# TODO: Why doesn't python-home on WSGIDaemonProcess or WSGIPythonHome work?
activate_this = '/home/factorio/.virtualenvs/rollback/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# TODO: Why doesn't Apache's SetEnv work to set this?
import os
os.environ["FACTORIO_ROLLBACK_CONFIG_PATH"] = "/home/factorio/factorio_rollback/config.py"

from factorio_rollback import app as application
