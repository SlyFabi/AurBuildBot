# Aur Build Bot #

Aur Build Bot is a simple python flask web application which updates and deploys AUR Packages automatically
into a by the application genererated repository.

The app exposes a simple web interface where packages can be added to the build list.

## Configuration ##

By default, the configuration is located at `~/.local/share/AurBuildBot/config.cfg`.

From there you can specify the repository name (needs to be used in pacman.conf) and the login password.

Default login credentials:

    Username: admin
    Password: admin

## Running manually ##

Note: The user the bot is running with should have sudo rights without asking for a password.

First you need the following dependencies

    pacman -S python python-pip
Then install the python dependencies

    pip install -r requirements.txt
You can run the Server with

    python AurBuildBot.py

## Running through docker ##

Grab the example docker-compose.yml and it's config files from `examples/docker/` and modify it to your liking.

Start the server

    docker-compose up

## Adding your repository to pacman ##

Edit your pacman.conf

    sudo nano /etc/pacman.conf

Append the server at the end of the file

    [RepoName]
    Server = http://address:8080/

If you don´t want to sign the packages created add `RemoteFileSigLevel = Optional` to your pacman.conf
