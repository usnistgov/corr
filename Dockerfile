## Dockerfile to create devel version of CoRR

FROM ubuntu:16.04
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get -y update
RUN apt-get install -y sudo
RUN apt-get install -y apt-utils
RUN apt-get install bzip2
RUN apt-get install -y build-essential
RUN apt-get install -y ufw

## Create a user with no sudo password.

RUN useradd -m fyc
RUN passwd -d fyc
RUN adduser fyc sudo
RUN echo 'fyc ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER fyc
WORKDIR /home/fyc
COPY . corr/
RUN sudo chown fyc:fyc corr -R

EXPOSE 5000
EXPOSE 5200
EXPOSE 5100

WORKDIR /home/fyc/corr

## Install everything using the Ansible playbook

RUN sudo ./config.bash --tags install --inventory-file builds/hosts.local

CMD sudo ./config.bash --tags serve --inventory-file builds/hosts.local