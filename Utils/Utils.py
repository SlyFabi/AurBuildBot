import subprocess
import os


def tryRemoveFiles(fileList):
    for file in fileList:
        try:
            os.remove(file)
        except OSError:
            pass


def tail(filePath, numLines):
    proc = subprocess.Popen(['tail', '-n', str(numLines), filePath], stdout=subprocess.PIPE)
    lines = proc.stdout.readlines()
    return ''.join(x.decode('utf-8') for x in lines)


def getEnvVars(path):
    with open(path, 'r') as f:
        return dict(tuple(line.replace('\n', '').split('=')) for line
                    in f.readlines() if not line.startswith('#'))
