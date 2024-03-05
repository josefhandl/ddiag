FROM ubuntu:20.04

ENV USER=ddiag
ENV USER_HOME=/home/${USER}

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Prague

RUN apt update && apt install -y --no-install-recommends \
        ca-certificates \
        apt-transport-https \
        locales \
        gnupg \
        sudo \
        python3 \
        python3-pip \
        python3-venv \
        strace \
        openssh-client \
# Basic tools \
        htop \
        vim \
        git \
        wget \
        curl \
# Net info, DNS, performance \
        iputils-ping \
        dnsutils \
        nmap \
        iperf3 \
        iperf \
# Application clients \
        postgresql \
        s3cmd \
        s4cmd \
# Browsh dependency
        firefox \
    && rm -rf /var/lib/apt/lists/*

# Install Browsh - text-based web browser with JavaScript support
RUN cd /tmp/ \
    && wget https://github.com/browsh-org/browsh/releases/download/v1.8.0/browsh_1.8.0_linux_amd64.deb \
    && apt install ./browsh_1.8.0_linux_amd64.deb \
    && rm ./browsh_1.8.0_linux_amd64.deb

RUN groupadd --gid 1000 ${USER} \
    && useradd --uid 1000 --create-home --home-dir ${USER_HOME} -s /bin/bash -g ${USER} ${USER} \
    && usermod -aG sudo ${USER} \
    && chown -R ${USER}:${USER} ${USER_HOME}

RUN echo 'root:a' | chpasswd \
    && echo 'ddiag:a' | chpasswd

# Add simple scripts to test connection and applications
COPY --chown=${USER}:${USER} scripts /opt/scripts
RUN pip3 install -r /opt/scripts/requirements.txt

ENTRYPOINT ["sleep", "infinity"]
