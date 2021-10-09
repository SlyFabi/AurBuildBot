FROM archlinux
EXPOSE 8080

# Enable multilib
RUN echo "[multilib]" >> /etc/pacman.conf && \
    echo "Include = /etc/pacman.d/mirrorlist" >> /etc/pacman.conf

# Install packages
RUN pacman-key --init && \
    pacman-key --populate archlinux && \
    pacman -Sy base-devel git python python-pip --noconfirm

# Create user
RUN useradd --shell=/bin/bash buildbot && \
    usermod -L buildbot && \
    echo "buildbot ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
    echo "root ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Setup home
WORKDIR /home/buildbot
RUN chown -R buildbot /home/buildbot

# Install bot
COPY . /aurbuildbot
WORKDIR /aurbuildbot
RUN pip install -r requirements.txt

ENTRYPOINT [ "sudo", "-u", "buildbot", "python", "AurBuildBot.py" ]
