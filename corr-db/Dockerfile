## CoRR Database micro-service.
FROM ubuntu:16.04
ENV DEBIAN_FRONTEND noninteractive

## System updates
RUN apt-get -y update
RUN apt-get install -y sudo
RUN apt-get install -y apt-utils
RUN apt-get install bzip2
RUN apt-get install -y build-essential
RUN apt-get -y update
RUN apt-get install -y git
RUN apt-get install -y wget
RUN apt-get install -y curl
RUN sudo apt-get install -y mongodb

## Create a user with no sudo password.
RUN useradd -m corradmin
RUN passwd -d corradmin
RUN adduser corradmin sudo
RUN echo 'corradmin ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER corradmin
WORKDIR /home/corradmin

## Setting up the environment.
COPY requirements.yaml /home/corradmin/requirements.yaml
COPY . /home/corradmin/corr-db
RUN sudo chown corradmin:corradmin /home/corradmin/corr-db -R
RUN sudo chown corradmin:corradmin /home/corradmin/requirements.yaml
RUN wget https://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh
RUN bash Miniconda-latest-Linux-x86_64.sh -b -p /home/corradmin/anaconda
RUN echo 'export PATH="/home/corradmin/anaconda/bin:$PATH"'>> /home/corradmin/.bashrc
RUN /home/corradmin/anaconda/bin/conda update -y conda
RUN /home/corradmin/anaconda/bin/conda create -y -n corr python=3.7
RUN /home/corradmin/anaconda/bin/conda env update -n corr --file /home/corradmin/requirements.yaml
RUN sudo chown corradmin:corradmin /home/corradmin/corr-db -R
WORKDIR /home/corradmin/corr-db
RUN /home/corradmin/anaconda/envs/corr/bin/python setup.py install

## Configuring the container access.
EXPOSE 27017
EXPOSE 28017
VOLUME /data

## Executing the services.
CMD sudo mongod --httpinterface

## Build the image [docker build -t corrdb:0.1 .]
## Run the corrdb micro-service [docker run -it -v /Users/fyc/data:/data -p 27017:27017 --name=corrdb corrdb:0.1]
