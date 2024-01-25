FROM ubuntu:22.04

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
        htop \
        vim \
        dnsutils \
        nmap \
        strace \
        iperf3 \
        iperf \
        postgresql \
        git \
        wget \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y locales && \
    rm -rf /var/lib/apt/lists/* && \
    localedef -i cs_CZ -c -f UTF-8 -A /usr/share/locale/locale.alias cs_CZ.UTF-8
ENV LC_ALL cs_CZ.UTF-8
ENV LANG cs_CZ.UTF-8

# Install RabbitMQ
COPY rabbitmq-install.sh /
RUN chmod +x /rabbitmq-install.sh \
    && /rabbitmq-install.sh \
    && rm /rabbitmq-install.sh

RUN groupadd --gid 1000 ${USER} \
    && useradd --uid 1000 --create-home --home-dir ${USER_HOME} -s /bin/bash -g ${USER} ${USER} \
    && usermod -aG sudo ${USER} \
    && chown -R ${USER}:${USER} ${USER_HOME}

RUN echo 'root:a' | chpasswd \
    && echo 'ddiag:a' | chpasswd

ENTRYPOINT ["sleep", "infinity"]
