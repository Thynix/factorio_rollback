from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import RadioField
from wtforms.validators import InputRequired
import fcntl
import glob
import os
import time
import subprocess

app = Flask(__name__)
app.config.from_envvar("FACTORIO_ROLLBACK_CONFIG_PATH")


@app.route('/')
def view():
    form = set_field_choices(SaveSelectionForm())
    return render_template("index.html", form=form)


@app.route('/rollback', methods=['POST'])
def rollback():
    saves = list_saves()
    form = set_field_choices(SaveSelectionForm(), saves)
    if not form.validate():
        return str(form.saves.errors)

    saves_by_string = {str(timestamp): filename
                       for timestamp, filename in saves.items()}

    # Ensure no other instances are attempting rollback concurrently.
    with open('rollback.lock', 'w') as lock_file:
        try:
            fcntl.lockf(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            # TODO: How to have pretty error pages?
            return "Another rollback is already running"

        subprocess.check_call(["sudo", "systemctl", "stop", "factorio"])
        try:
            try:
                # Set modification time to current time.
                os.utime(saves_by_string[form.saves.data], None)
            except KeyError:
                return "Requested save no longer exists."
        finally:
            subprocess.check_call(["sudo", "systemctl", "start", "factorio"])

        return "Rollback successful."


class SaveSelectionForm(FlaskForm):
    saves = RadioField(validators=[InputRequired(),])


def set_field_choices(form, saves=None):
    if saves is None:
        saves = list_saves()

    # POSIX timestamp for value; human-readable timestamp label.
    form.saves.choices = [
        (
            str(timestamp),
            time.strftime('%A, %d %B %Y, %I:%M %p %Z', time.localtime(timestamp)),
        ) for timestamp in sorted(saves.keys())
    ]

    return form


def list_saves():
    """
    :return: Autosave filenames keyed by creation time.
    :rtype: dict
    """
    saves = dict()
    for filename in glob.glob("_autosave*.zip"):
        creation_time = os.path.getctime(filename)
        saves[creation_time] = filename

    return saves


@app.before_request
def enter_saves_directory():
    # All operations are performed in this directory.
    os.chdir(app.config["SAVES_DIRECTORY"])

if __name__ == '__main__':
    app.run()
