from flask import request, Blueprint, redirect
from pathlib import Path
from Bot.Bot import AurPackage, PackageStatus
import shutil

import Globals
from Bot import Config

IndexController = Blueprint('Index', __name__, template_folder='templates')

auth = Globals.APP_AUTH


@IndexController.route('/GetPackageStatus', methods=['GET'])
@auth.login_required
def fnGetPackageStatus():
    pkgName = request.values['name']

    config = Config.get()
    pkg = next((x for x in config.Packages if x.Name == pkgName), None)
    if pkg is None:
        return ""

    status = Globals.BOT.getPackageStatus(pkg)
    if status == PackageStatus.NOT_BUILT:
        return "Not built"
    elif status == PackageStatus.BUILDING:
        return "Building"
    elif status == PackageStatus.BUILT:
        return "Built"

    return "Error"


@IndexController.route('/PostAddPackage', methods=['POST'])
@auth.login_required
def fnAddPackage():
    pkgName = request.values['name']
    aurPkg = AurPackage.getPackageByName(pkgName)

    config = Config.get()
    for pkg in config.Packages:
        if pkg.Name == aurPkg.Name:
            raise Exception(f"Package {aurPkg.Name} is already on the list !")

    pkg = Config.Package(aurPkg.Name, '0.0.0', 0, 'Never')
    config.Packages.append(pkg)

    Config.save(config)
    Globals.BOT.forceUpdate()

    return redirect('/')


@IndexController.route('/PostRebuildPackage', methods=['POST'])
@auth.login_required
def fnRebuildPackage():
    pkgName = request.values['name']
    buildPath = Config.BASE_BUILD_DIR + pkgName + '/'
    if Path(buildPath).is_dir():
        shutil.rmtree(buildPath)

    config = Config.get()
    pkg = next((x for x in config.Packages if x.Name == pkgName), None)
    if pkg is None:
        raise Exception(f"Could not rebuild package {pkgName} !")

    pkg.LastBuild = 0
    Config.save(config)
    Globals.BOT.forceUpdate()

    return redirect('/')


@IndexController.route('/PostRemovePackage', methods=['POST'])
@auth.login_required
def fnRemovePackage():
    pkgName = request.values['name']
    config = Config.get()

    config.Packages = [pkg for pkg in config.Packages if pkg.Name != pkgName]
    Config.save(config)
    Globals.BOT.forceUpdate()

    return redirect('/')


@IndexController.route('/PostRebuildAll', methods=['POST'])
@auth.login_required
def fnRebuildAll():
    if Path(Config.BASE_BUILD_DIR).is_dir():
        shutil.rmtree(Config.BASE_BUILD_DIR)
        Path(Config.BASE_BUILD_DIR).mkdir(parents=True, exist_ok=True)

    config = Config.get()
    for pkg in config.Packages:
        pkg.LastBuild = 0

    Config.save(config)
    Globals.BOT.forceUpdate()

    return redirect('/')
