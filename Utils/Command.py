import os
import time
from threading import Thread
import asyncio

from Utils import Logger


class Command:
    class SubprocessProtocol(asyncio.SubprocessProtocol):
        def __init__(self, command):
            self.__command = command
            self.__transport = None

        def connection_made(self, transport):
            self.__transport = transport

        def pipe_data_received(self, fd, data):
            Logger.getLogger().debug(f'[Cmd {self.__command.cmd}]: ' + data.rstrip().decode('utf-8'))

        def process_exited(self):
            self.__command.exitCode = self.__transport.get_returncode()
            Logger.getLogger().debug(f'[Cmd {self.__command.cmd}]: Exit ' + str(self.__command.exitCode))

        def connection_lost(self, exc):
            self.__command.loop.stop()

    def __init__(self, cmd, workingDirectory):
        self.cmd = cmd
        self.workingDirectory = workingDirectory
        self.isRunning = True
        self.exitCode = 0

        self.__thread = Thread(target=self.__runLoop)
        self.__thread.daemon = True
        self.__thread.start()

    def __runLoop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        try:
            self.loop.run_until_complete(self.loop.subprocess_exec(lambda: Command.SubprocessProtocol(command=self),
                                                                   *self.cmd, cwd=self.workingDirectory))
            self.loop.run_forever()
        finally:
            self.loop.close()
            self.isRunning = False

    def poll(self):
        if not self.isRunning:
            return False

        return True

    def getExitCode(self):
        if self.isRunning:
            return False

        return self.exitCode

    def waitForExit(self):
        while self.poll():
            time.sleep(0.1)
        return self.getExitCode()

    def kill(self):
        self.loop.stop()

    @staticmethod
    def run(cmd, workingDirectory=os.getcwd()):
        command = Command(cmd, workingDirectory)
        return command

    @staticmethod
    def runBash(cmdStr, workingDirectory=os.getcwd()):
        return Command.run(['bash', '-c', cmdStr], workingDirectory=workingDirectory)
