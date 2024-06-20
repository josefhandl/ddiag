FROM ubuntu:24.04

ENV USER=ubuntu

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
        iproute2 \
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

RUN usermod -aG sudo ubuntu

RUN echo "root:a" | chpasswd \
    && echo "${USER}:a" | chpasswd

# Install Browsh - text-based web browser with JavaScript support
RUN cd /tmp/ \
    && wget https://github.com/browsh-org/browsh/releases/download/v1.8.0/browsh_1.8.0_linux_amd64.deb \
    && apt install ./browsh_1.8.0_linux_amd64.deb \
    && rm ./browsh_1.8.0_linux_amd64.deb

# Install Kubectl
RUN mkdir /opt/bin/ \
    && cd /opt/bin/ \
    && curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && chmod +x kubectl
ENV PATH "/opt/bin/:${PATH}"

# Install Helm
USER root
RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
USER ${USER}
RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
USER root

# Install K9s tool for both users (root, ${USER})
USER root
RUN curl -sS https://webinstall.dev/k9s | bash
USER ${USER}
RUN curl -sS https://webinstall.dev/k9s | bash
USER root

# Install rabbitmqctl
RUN apt update && apt install -y --no-install-recommends \
        rabbitmq-server

# Add simple scripts to test connection and applications
COPY --chown=${USER}:${USER} scripts /opt/scripts
USER ${USER}
WORKDIR /opt/scripts
RUN python3 -m venv venv \
    && /opt/scripts/venv/bin/pip3 install -r /opt/scripts/requirements.txt
# Add cheatsheet
COPY cheatsheet.md /opt/

WORKDIR /opt

ENTRYPOINT ["sleep", "infinity"]
