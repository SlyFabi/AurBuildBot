from dataclasses import dataclass
from datetime import datetime
from dataclasses_jsonschema import JsonSchemaMixin
from typing import List
from pathlib import Path
import json
import os
import shutil

BASE_DIR = str(Path.home()) + '/.local/share/AurBuildBot/'
BASE_BUILD_DIR = BASE_DIR + 'builds/'
LOG_DIR = BASE_DIR + 'logs/'
SERVER_ROOT_DIR = BASE_DIR + 'wwwroot/'
SERVER_PACKAGES_DIR = SERVER_ROOT_DIR + 'packages/'

CONFIG_FILE = BASE_DIR + 'config.cfg'

# Create directories
Path(BASE_DIR).mkdir(parents=True, exist_ok=True)
Path(BASE_BUILD_DIR).mkdir(parents=True, exist_ok=True)
Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
Path(SERVER_ROOT_DIR).mkdir(parents=True, exist_ok=True)

# Cleanup log files
logFiles = [f for f in os.listdir(LOG_DIR) if os.path.isfile(os.path.join(LOG_DIR, f))]
if len(logFiles) > 10:
    print('Cleaning up log files...')
    shutil.rmtree(LOG_DIR)
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)


@dataclass
class Package(JsonSchemaMixin):
    Name: str
    Version: str
    LastBuild: int
    LastBuildDate: str


@dataclass
class Config(JsonSchemaMixin):
    RepositoryName: str
    CheckIntervalM: int
    AdminPassword: str
    Packages: List[Package]


def get():
    if Path(CONFIG_FILE).is_file():
        try:
            with open(CONFIG_FILE, "r") as file:
                data = json.load(file)
                return Config.from_dict(data)
        except Exception:
            print('Could not load config ! Deleting...')
            os.remove(CONFIG_FILE)

    print('No config. Using fallback...')

    packages = []
    config = Config("repo", 60, "admin", packages)

    save(config)
    return config


def save(config):
    with open(CONFIG_FILE, "w") as file:
        file.write(json.dumps(config.to_dict(), indent=4))
