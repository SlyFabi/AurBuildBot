from flask import request, Blueprint, redirect
from pathlib import Path
import shutil

import Globals
from Bot import Config

SettingsController = Blueprint('Settings', __name__, template_folder='templates')

auth = Globals.APP_AUTH


@SettingsController.route('/PostSaveSettings', methods=['POST'])
@auth.login_required
def fnSaveSettings():
    repoName = request.values['repoName']
    checkInterval = request.values['checkInterval']
    if ' ' in repoName:
        raise Exception("Repository Name cannot contain any whitespaces !")
    try:
        checkInterval = int(checkInterval)
    except:
        raise Exception("Check Interval must be a number !")

    config = Config.get()

    # Invalidate packages
    if config.RepositoryName != repoName:
        for pkg in config.Packages:
            pkg.LastBuild = 0

        shutil.rmtree(Config.SERVER_ROOT_DIR)
        Path(Config.SERVER_ROOT_DIR).mkdir(parents=True, exist_ok=True)

    config.RepositoryName = repoName
    config.CheckIntervalM = checkInterval

    Config.save(config)
    Globals.BOT.forceUpdate()

    return redirect('/')
