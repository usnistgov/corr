<p align="center">
    <img src="https://rawgit.com/usnistgov/corr/master/corr-view/frontend/images/logo.svg"
         height="240"
         alt="CoRR logo"
         class="inline"/>
</p>

<p align="center">
<a href="https://corr.nist.gov" target="_blank">
<img src="https://img.shields.io/badge/corr-nist-cyan.svg"
alt="CoRR NIST Public Instance">
</a>
<a href="https://corrworkspace.slack.com" target="_blank">
<img src="https://img.shields.io/badge/corr-slack-purple.svg"
alt="Slack">
</a>
<a href="http://corr.readthedocs.io/en/latest/?badge=latest" target="_blank">
<img src="https://readthedocs.org/projects/corr/badge/?version=0.2" alt="Reathedocs">
</a>
<a href="https://www.youtube.com/playlist?list=PLiWY1GXAXKFk4aSwI9CfyAoDwR6bjD8zV">
<img src="https://img.shields.io/badge/corr-youtube-red.svg" alt="Youtube Playlist" height="18">
</a>
<a href="https://github.com/usnistgov/corr/blob/master/LICENSE">
<img src="https://img.shields.io/badge/license-mit-blue.svg" alt="License" height="18">
</a>
</p>

# Introduction

CoRR is designed as a web platform. CoRR is not a tool for a single user perspective
but rather a community oriented portal. The present document explains how to configure
and launch a CoRR instance. For more help, please refer to the slack workspace provided in badge
above. Also, video tutorials are provided which demonstrate what is explained here.

# Requirements

CoRR micro-services are [Docker](https://www.docker.com) containers. Thus, to launch the platform
[docker](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/install/)
commands must be present on the system. The present version has been tested on the following versions:

    $ Docker version 1.13.0, build 49bf474
    $ docker-compose version 1.23.2, build 1110ad0

The CoRR instance requires a location to store its [setup folder](./corr-setup). The content of
this folder does not have to remain in the same folder. Rather this is done for convenience. The
instance administrator (admin) may decide to reloaded the data/db folder which is needed by the mongodb
micro-service. However doing so required a extra step in the adjustment of the docker-compose
recipe. Once the admin determines a location, copy the [setup folder](./corr-setup) folder over to
that location and copy the path to this folder (your_setup_path). We will use it in the next section.

# Dockercompose recipe

Open the [docker-compose recipe](docker-compose.yaml) in a text editor and replace all occurrences of
/Users/fyc/CoRR-Final-2018/corr with your_setup_path. Then if you need specific files or folders in
your corr-setup folder relocated, do so but provide their paths in the appropriate volumes line. For
example if we wanted to relocate the corr-storage folder (holds the actual files in complement to the
metadata stored in mongodb) to a different disk that has more space such as /more-space. We will have to
change the lines: your_setup_path/corr-setup/corr-storage:/home/corradmin/corr-storage in corrapi and corrview
services definitions to /more-space/corr-setup/corr-storage:/home/corradmin/corr-storage .

# Instance setup

Before going further, we must make sure that your_setup_path is accessible by docker. If not, the instance will
be in lockdown mode and all docker containers will be marked unhealthy. The instance will be unstable and probably
fail to respond properly. Moreover, if you relocate content present in corr-setup, make sure they are in locations
accessible by docker. Once this is being taken care of, we can now setup the instance to be launched.

## Instance configuration

The CoRR instance frontend has a title shown on the top left corner in the banner. This can be adapted to your needs.
In your_setup_path/corr-setup/config, edit custom.json. Change the content of the key `name` to what you want displayed.
The NIST instance is configured to `NIST Demo Instance`. In the CoRR instance footer, a warning content is provided for
customization. The current default states that the platform leverages cookies to function. We strongly recommend that the
admin change this to be adequate to its institutions rules and regulations. This can be done in the same custom.json
file in the value of the key `warning`. The terms of service of a CoRR instance is also customizable in the value of the
key `terms`. Again we also strongly recommend changing this before any public access is provided. The other files in
your_setup_path/corr-setup/config are to be left as is. Editing them belongs to advanced configuration which is not need here.

## Adminstrator credentials

Before launching the instance, we extremely recommend addressing this. your_setup_path/corr-setup/credentials contains
tmp_admin.json which allow the admin to provide an email address, a password, a first name and last name. We recommend
changing at least the email as it WILL CANNOT BE EDITED LATER. Furthermore, we recommend changing every else in the file. The
password must be at least 12 characters and must contains Upper characters, numbers and special characters. A failure to comply
with this rule will result in the failure to create the admin account. Thus, the launched instance will have to be
terminated, the password fixed and then relaunched to create the admin account.

## HTTPS configuration

In the your_setup_path/corr-setup/nginx folder there are three files that must be replaced by the appropriate ones from an
authorized certificate authority. Before buying a certificate to test the instance in a verified https fashion we suggest
using services such as [Let's Encrypt](https://letsencrypt.org/) which provide a free short term alternative. The files to
be replaced are `corr.cer`, `corr.crt`, `corr.key`. When replacing them keep the naming convention as the nginx micro-service
will be looking for these exactly.

# Instance deployment

## Monitoring an instance

To monitor your CoRR instance, there are three folder to look into in your your_setup_path/corr-setup.
Right after your first launch we recommend looking into the `test` folder. What you are looking for is the passed keyword.
We are working on more adequate testing. So bare with us while we work on this. Then, the admin should refer to the `log` folder
regularly. It contains the `access` and `error` of the corrapi, corrcloud, corrview and nginx micro-services logs. A word of warning
here is that `corrapi-error` and `corrcloud-error` are not only showing `errors` but also log the services workers executions. We
apologize for the confusion that this must create. Finally, the corr-storage folder contains the data stored in CoRR in complement to
the metadata present in the mongodb database.

## Security and scale

With regard to the system on which the CoRR instance is launched, CoRR components are launched in an isolated fashion.
The access to the instance containers is restricted to a docker-compose created network. Containers address each other by service name
as specified in the docker-compose recipe. Regarding scale, when he two flask-based restful services corrapi and corrcloud are launched,
3 workers accepting 1000 concurrent connections are executed for each of those services in their respective containers.
The number of worker was calculated from the simple formula 2*{number_of_cpus}+1. We assume a minimal number of cpu here to 1. On a computer with greater capacity and to accomodate for response time in case of high volume we recommend changing this in the corr-api and
corr-cloud respective Dockerfiles on the CMD line in the gunicorn call. The parameter --workers can then be adjusted to the result of the
formula on your system as needed. In such a scaling situation you will have to rebuild the docker containers to reflect on this change.

## Managing the instance

To build new images from the source with docker-compose after following the previous steps run:

    $ docker-compose build --force-rm

This command will build four images palingwende/(corrdb:0.2, corrapi:0.2, corrcloud:0.2, corrview:0.2)
and pull the nginx image. It will remove intermediate images to avoid stacking in memory.
If you do not need to build new containers, run the following:

    $ docker-compose pull

This command will pull the five images palingwende/(corrdb:0.2, corrapi:0.2, corrcloud:0.2, corrview:0.2)
and nginx from [dockerhub](https://hub.docker.com). These are our latest default builds.
To finally run your instance of CoRR, run:

    $ docker-compose up -d

While this is processing we recommend looking into the micro-services logs and running docker to track
deployment process:

    $ docker ps

The previous command will list the instance micro-services execution status and health. Please look for health
to determine that the container passed our health check. You must aim for an `healthy` value here. If it shows
`unhealthy` instead it means something has gone wrong and we can't reach the service status check url.
The CoRR instance micro-services are launched in a specific fashion as following:

    $ corrdb --> corrapi --> corrcloud --> corrview --> nginx --> corrtest

The health status of a container depends on the health state of its predecessors. corrapi and corrcloud critically
depends on corrdb to run. Thus, if the corrdb container fails to stay running, the corrapi and corrcloud will also
fail to run. Moreover, if any of these two cannot access corrdb they will crash. corrview, nginx and corrtest on the
other end have loose dependencies. Despite the fact that their health is regulated by the precedence they will not
fail to run if one of their dependencies fail.
To shutdown a CoRR instance run:

    $ corr-compose down

To build, launch or shutdown a specific micro-service, provide its name at the end of the previous docker-compose
commands. The service names are: corrdb, corrapi, corrcloud, corrapi, corrview, nginx, corrtest. However, since
the network is not specific in static in the docker-compose recipe, restarting a specific container might isolate
it to another network and thus block traffic to the others. Thus, proceed with care in this. We recommend stopping
the whole instance and restarting it.

## Access the instance

Open a browser and go to [CoRR Local](https://0.0.0.0). If you haven't provided verified SSL/TLS certificates and keys,
a security alert will be brought up by the browser. You must add the exception before proceeding. Issues have been reported
on Safari while none were for other browsers. We recommend trying on other browsers if you are not able to accept the
exception in a specific one. Please refer to [How to use](USE.md) to understand how to use CoRR as an admin or a user.


# Advanced configuration

By default a CoRR instance uses local filesystem for data storage, does user moderation (no automatic login after registration.  
users must be approved by the admin) and communication to the instance is not scanned. The can be changed but will require
rebuilding the containers.

## Storage options

To change the storage option, the administrator will have to edit the config-(api, cloud) files in your_setup_path/corr-setup/config.
The section FILE_STORAGE is a dictionary that can be changed. The present version of CoRR v0.2 also support s3 storage. To switch to s3,
change the values of the keys `type`, `location`, `name`, `id`, `key` to `s3`, `aws_region_name`, `s3_bucket_name`,
`aws_access_key_id` and `aws_secret_access_key`. Moreover, we recommend providing this content to your `s3` folder files. For more
information refer to the [AWS Boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html).
Beware that this must be done for both corrapi and corrcloud simultaniously as they must both store data at the same location. Not doing
so will cause stability issue.

## User moderation options

To require account verification before the first login, after registration, the admin must go to the users page and approve them.
This is the default behavior of the CoRR instance. To allow automatic login on registration and turn down requirement for admin
initial acceptance, refer to your your_setup_path/corr-setup/config/config/config-(cloud, api).py SECURITY_MANAGEMENT section. Turn the
`account` key value to false to turn off on registration moderation and true to require it before login.

## Platform communication scanning

The corrapi and corrcloud are designed to work with [ClamAV antivirus](http://www.clamav.net). Thus, security checks on all content
sent to these services can be enforced. By default in the current instance this is not enabled as it stalls the instance much. However,
activating it provide a greater security regarding what is received from users, tools and what is effectively stored on the system.
To turn this feature on, go to your_setup_path/corr-setup/config/config/config-(cloud, api).py under the same SECURITY_MANAGEMENT as
before and change `content` key value to true.
