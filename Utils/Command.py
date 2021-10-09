import os
import time
import subprocess

from Utils import Logger


class Command:
    def __init__(self, cmd, workingDirectory):
        self.__cmd = cmd
        self.__proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=workingDirectory)

    def poll(self):
        line = self.__proc.stdout.readline()
        lineErr = self.__proc.stderr.readline()
        if not line or not lineErr:
            self.__proc.wait()
            return False

        Logger.getLogger().debug(f'[Cmd {self.__cmd}]: ' + line.rstrip().decode('utf-8'))
        return True

    def getExitCode(self):
        if self.__proc.poll() is None:
            return False

        output = self.__proc.stdout.read()
        outputErr = self.__proc.stderr.read()

        Logger.getLogger().debug(f'[Cmd {self.__cmd}]: ' + output.rstrip().decode('utf-8'))
        Logger.getLogger().debug(f'[Cmd {self.__cmd}]: ' + outputErr.rstrip().decode('utf-8'))
        Logger.getLogger().debug(f'[Cmd {self.__cmd}]: Exit code {self.__proc.returncode}')

        return self.__proc.returncode

    def waitForExit(self):
        while self.poll():
            time.sleep(0.1)
        return self.getExitCode()

    @staticmethod
    def run(cmd, workingDirectory=os.getcwd()):
        command = Command(cmd, workingDirectory)
        return command

    @staticmethod
    def runBash(cmdStr, workingDirectory=os.getcwd()):
        return Command.run(['bash', '-c', cmdStr], workingDirectory=workingDirectory)
