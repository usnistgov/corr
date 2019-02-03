## CoRR API micro-service.
FROM palingwende/corrdb:0.2

## User and update.
USER corradmin
RUN sudo apt-get -y update
WORKDIR /home/corradmin

## Setting up the environment.
RUN mkdir /home/corradmin/.config
COPY corrapi_config /home/corradmin/.config
COPY . /home/corradmin/corr-api
RUN sudo chown corradmin:corradmin /home/corradmin/corr-api -R
RUN sudo apt-get install -y clamav-daemon
RUN sudo apt-get install -y clamav-freshclam
RUN sudo apt-get install -y clamav-unofficial-sigs
RUN sudo chown -R clamav:clamav /var/lib/clamav
RUN sudo chown -R clamav:clamav /var/log/clamav
RUN sudo chown corradmin:corradmin /home/corradmin/corr-api -R
WORKDIR /home/corradmin/corr-api

## Update clamav
RUN sudo freshclam

## Configuring the access.
EXPOSE 5100

## CoRR micro-service logs.
VOLUME /home/corradmin/log

## CoRR storage volume.
VOLUME /home/corradmin/corr-storage

## CoRR s3 config and credentials volume.
VOLUME /home/corradmin/s3

## Configuration
#VOLUME /home/corradmin/corr-api/config.py

## Executing the services.
## For production, make sure you know what you are doing here.
## For high performance, we have identified that CoRR is mostly I/O bound as in most cases it is about uploading and downloading content.
## Thus, since in our development computer we have 8 cores, we have done --worker-class=gevent --workers 2*cpus+1 = 17 and --worker-connections=1000
## In case you are not sure or you do not agree with us or think it is CPU bound just compute the number of workers and only leave --workers={{2*cpus+1}}. Remove "--worker-class=gevent --worker-connections=1000"
CMD sudo freshclam; sudo service clamav-daemon start; sudo /home/corradmin/anaconda/envs/corr/bin/gunicorn -c /home/corradmin/.config/corrapi_config --worker-class=gevent --worker-connections=1000 --workers=3 --bind 0.0.0.0:5100 run:app
#; sleep 60
#; multitail /home/corradmin/log/corrapi-access.log /home/corradmin/log/corrapi-error.log

## Build the image [docker build -t corrapi:0.1 .]
## Run the corrapi micro-service [docker run -it -v /Users/fyc/log:/home/corradmin/log -v /Users/fyc/corr-storage:/home/corradmin/corr-storage -p 5100:5100 corrapi:0.1]
## If you have selected AWS S3 as your storage option for this micro-service, please provide a s3 folder volume that will provide
## the config and the credentials as directed in the repository with config-s3 and credentials-s3.

## Test on a browser at: http://0.0.0.0:5100/corr/api/v0.1/public/users
