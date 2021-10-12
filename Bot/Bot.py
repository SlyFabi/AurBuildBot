import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from threading import Thread
from urllib.request import urlopen
from enum import Enum
import requests
import tarfile
import time
import shutil

from Bot import Config
from Utils import Logger
from Utils.Command import Command

AUR_URL = 'https://aur.archlinux.org'
API_URL = AUR_URL + '/rpc.php?type=info&arg=%s'

logger = Logger.getLogger()


class PackageStatus(Enum):
    NOT_BUILT = 0
    BUILDING = 1
    BUILT = 2


@dataclass
class AurPackage:
    Id: int
    Name: str
    Version: str
    LastModified: int
    UrlPath: str

    @staticmethod
    def getPackageByName(name):
        r = requests.get(API_URL % name)
        result = r.json()

        if result["version"] != 1:
            raise Exception("Unsupported AUR Version " + result["version"] + " !")
        if len(result["results"]) == 0 or result["results"]["PackageBase"] != name:
            raise Exception("Package " + name + " not found !")

        pkgJson = result["results"]
        return AurPackage(pkgJson["ID"], pkgJson["Name"], pkgJson["Version"], pkgJson["LastModified"],
                          pkgJson["URLPath"])


class Bot:
    def __init__(self):
        self.__thread = None
        self.__isRunning = False
        self.__forceUpdate = False
        self.__packageStatusDict = {}

    def start(self):
        if self.__thread is not None:
            self.stop()
        self.__isRunning = True
        self.__thread = Thread(target=self.__botThread)
        self.__thread.start()

    def stop(self):
        if self.__thread is None:
            return
        self.__isRunning = False
        self.__thread.join()

    def forceUpdate(self):
        self.__forceUpdate = True

    def getPackageStatus(self, package):
        if package.Name not in self.__packageStatusDict:
            return PackageStatus.NOT_BUILT

        return self.__packageStatusDict[package.Name]

    def __setPackageStatus(self, package, status):
        self.__packageStatusDict[package.Name] = status

    def __botThread(self):
        while self.__isRunning:
            config = Config.get()

            # Update System
            try:
                if not self.__runBotCommand(['sudo', 'pacman', '-Syu', '--noconfirm']):
                    raise Exception("Could not update system !")
            except Exception as e:
                logger.error(e)

            for pkg in config.Packages:
                self.__setPackageStatus(pkg, PackageStatus.NOT_BUILT)

                try:
                    logger.info('Checking package ' + pkg.Name + '...')

                    info = AurPackage.getPackageByName(pkg.Name)
                    if info.LastModified > pkg.LastBuild:
                        self.__setPackageStatus(pkg, PackageStatus.BUILDING)
                        self.__updatePackage(info)

                    self.__setPackageStatus(pkg, PackageStatus.BUILT)
                except Exception as e:
                    logger.error(e)

            logger.info('Done checking packages')

            waitedTime = 0
            while waitedTime < config.CheckIntervalM * 60 and not self.__forceUpdate:
                time.sleep(1.0)
                waitedTime = waitedTime + 1
            self.__forceUpdate = False

    def __updatePackage(self, info):
        logger.info('Updating package ' + info.Name + '...')
        buildPath = Config.BASE_BUILD_DIR + info.Name + '/'

        # Delete old if exists
        if Path(buildPath).is_dir():
            shutil.rmtree(buildPath)

        # Download and extract
        with urlopen(AUR_URL + info.UrlPath) as pkgFile:
            with tarfile.open(mode='r|*', fileobj=pkgFile) as pkgTar:
                pkgTar.extractall(Config.BASE_BUILD_DIR)

        # Build package
        logger.info('Building package ' + info.Name + '...')
        if not self.__runBotCommand(['makepkg', '-s', '--noconfirm'], workingDirectory=buildPath):
            raise Exception("Package " + info.Name + " failed to build !")

        # Deploy package
        config = Config.get()
        pkg = next((x for x in config.Packages if x.Name == info.Name), None)
        if pkg is None:
            raise Exception(f"Failed to deploy package {info.Name}: Deleted while building.")

        logger.info('Deploying package ' + info.Name + '...')
        repoFile = config.RepositoryName + '.db.tar.zst'

        if not self.__runBotCommandBash(f'cp *.pkg.tar.zst {Config.SERVER_ROOT_DIR}', workingDirectory=buildPath):
            raise Exception("Failed to deploy package " + info.Name + " !")

        if not self.__runBotCommandBash(f'repo-add {repoFile} *.pkg.tar.zst', workingDirectory=Config.SERVER_ROOT_DIR):
            raise Exception("Failed to deploy package " + info.Name + " !")

        logger.info(f'Updated package {info.Name} (Version {pkg.Version} -> {info.Version})')

        pkg.LastBuild = info.LastModified
        pkg.LastBuildDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        pkg.Version = info.Version
        Config.save(config)

    def __runBotCommand(self, cmdList, workingDirectory=os.getcwd()):
        cmd = Command.run(cmdList, workingDirectory=workingDirectory)
        while cmd.poll():
            if not self.__isRunning or self.__forceUpdate:
                cmd.kill()
                raise Exception("Aborted command !")
            time.sleep(0.1)

        return cmd.getExitCode() == 0

    def __runBotCommandBash(self, cmdStr, workingDirectory=os.getcwd()):
        cmd = Command.runBash(cmdStr, workingDirectory=workingDirectory)
        while cmd.poll():
            if not self.__isRunning or self.__forceUpdate:
                cmd.kill()
                raise Exception("Aborted command !")
            time.sleep(0.1)

        return cmd.getExitCode() == 0
