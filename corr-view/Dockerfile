## CoRR View micro-service.
FROM ubuntu:16.04
ENV DEBIAN_FRONTEND noninteractive

## System updates
RUN apt-get -y update
RUN apt-get install -y sudo
RUN apt-get install -y apt-utils
RUN apt-get install bzip2
RUN apt-get install -y curl
RUN apt-get install -y build-essential
RUN apt-get install -y make
RUN apt-get -y update
RUN apt-get install -y ruby-dev
RUN apt-get install -y ruby
RUN apt-get -y update


## Create a user with no sudo password.
RUN useradd -m corradmin
RUN passwd -d corradmin
RUN adduser corradmin sudo
RUN echo 'corradmin ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER corradmin
WORKDIR /home/corradmin

## Setting up the environment.
COPY . /home/corradmin/corr-view
RUN sudo chown corradmin:corradmin /home/corradmin/corr-view -R
RUN sudo gem install jekyll bundler

WORKDIR /home/corradmin/corr-view/frontend

## Configuring the container access.
EXPOSE 5000

## Custom volume
VOLUME /home/corradmin/corr-view/xml/custom.json

## Configuration
VOLUME /home/corradmin/corr-view/js/config.js

## Executing the services.
CMD jekyll serve --host=0.0.0.0 --port=5000 >> /home/corradmin/corrview.log

## Build the image [docker build -t corrview:0.1 .]
## Run the corrview micro-service [docker run -it -v /Users/fyc/config/custom.json:/home/corradmin/corr-view/xml/custom.json -p 5000:5000 --name=corrview corrview:0.1]
