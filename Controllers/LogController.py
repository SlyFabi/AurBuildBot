from flask import request, Blueprint

import Globals
from Utils import Logger, Utils

LogController = Blueprint('Log', __name__, template_folder='templates')

auth = Globals.APP_AUTH


@LogController.route('/GetLog', methods=['GET'])
@auth.login_required
def fnGetLog():
    numLinesStr = request.values['numLines']
    try:
        numLines = int(numLinesStr)
    except Exception:
        raise Exception("Number of lines must be a number !")

    return Utils.tail(Logger.LOG_PATH, numLines)
