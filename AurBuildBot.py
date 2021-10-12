from flask import render_template, Markup, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from waitress import serve

import Globals
from Bot import Config

from Controllers.IndexController import IndexController
from Controllers.SettingsController import SettingsController
from Controllers.LogController import LogController

users = {
    "admin": generate_password_hash(Config.get().AdminPassword)
}

app = Globals.APP
auth = Globals.APP_AUTH


def render_base(page):
    return render_template('base.html', content=Markup(page))


@app.errorhandler(Exception)
def handle_exception(e):
    config = Config.get()
    page = render_template('index.html', packages=config.Packages)
    return render_template("base.html", content=Markup(page), exception=e), 500


@app.route('/<path:path>')
def serve_repo_files(path):
    return send_from_directory(Config.SERVER_ROOT_DIR, path)


@app.route('/static/<path:path>')
@auth.login_required
def serve_resources(path):
    return send_from_directory('static/', path)


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@app.route('/')
@auth.login_required
def index():
    config = Config.get()
    return render_base(render_template('index.html', packages=config.Packages))


@app.route('/AddPackage')
@auth.login_required
def addPackage():
    return render_base(render_template('addPackage.html'))


@app.route('/Settings')
@auth.login_required
def settings():
    config = Config.get()
    return render_base(render_template(
        'settings.html', repoName=config.RepositoryName, checkInterval=config.CheckIntervalM))


@app.route('/Logs')
@auth.login_required
def logs():
    return render_base(render_template('logs.html'))


if __name__ == '__main__':
    Globals.BOT.start()

    app.register_blueprint(IndexController)
    app.register_blueprint(SettingsController)
    app.register_blueprint(LogController)
    serve(app, host="0.0.0.0", port=8080)
    # app.run(host="0.0.0.0", port=8080, debug=True)
