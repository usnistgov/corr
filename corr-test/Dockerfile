## CoRR Test micro-service.
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

## Create a user with no sudo password.
RUN useradd -m corradmin
RUN passwd -d corradmin
RUN adduser corradmin sudo
RUN echo 'corradmin ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER corradmin
WORKDIR /home/corradmin

## Setting up the environment.
COPY requirements.yaml /home/corradmin/requirements.yaml
COPY . /home/corradmin/corr-test
RUN sudo chown corradmin:corradmin /home/corradmin/corr-test -R
RUN sudo chown corradmin:corradmin /home/corradmin/requirements.yaml
RUN wget https://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh
RUN bash Miniconda-latest-Linux-x86_64.sh -b -p /home/corradmin/anaconda
RUN echo 'export PATH="/home/corradmin/anaconda/bin:$PATH"'>> /home/corradmin/.bashrc
RUN /home/corradmin/anaconda/bin/conda update -y conda
RUN /home/corradmin/anaconda/bin/conda create -y -n corr python=3.7
RUN /home/corradmin/anaconda/bin/conda env update -n corr --file /home/corradmin/requirements.yaml
RUN sudo chown corradmin:corradmin /home/corradmin/corr-test -R
WORKDIR /home/corradmin/corr-test

VOLUME /home/corradmin/test

## Executing the services.
CMD /home/corradmin/anaconda/envs/corr/bin/tavern-ci --stdout test_api.tavern.yaml >> /home/corradmin/test/test_corrapi.txt; /home/corradmin/anaconda/envs/corr/bin/tavern-ci --stdout test_cloud.tavern.yaml >> /home/corradmin/test/test_corrcloud.txt
