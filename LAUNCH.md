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

# Launching an instance

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

The CoRR instance requires a location to store its [setup folder](corr-setup). The content of
this folder does not have to remain in the same folder. Rather this is done for convenience. The
instance administrator (admin) may decide to reloaded the data/db folder which is needed by the mongodb
micro-service. However doing so required a extra step in the adjustment of the docker-compose
recipe. Once the admin determines a location, copy the [setup folder](corr-setup) folder over to
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
