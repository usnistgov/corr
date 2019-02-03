<p align="center">
    <img src="https://rawgit.com/usnistgov/corr/master/corr-view/frontend/images/logo.svg"
         height="240"
         alt="CoRR logo"
         class="inline"/>
</p>

<p align="center"><sup><strong>
<a href="https://github.com/usnistgov/corr-sumatra">Sumatra</a>
<a href="https://github.com/usnistgov/corr-reprozip">Reprozip</a>
<a href="https://github.com/usnistgov/corr-cde">CDE</a>
<a href="https://github.com/usnistgov/pfhub">PFHub</a>
<a href="https://github.com/usnistgov/corr-noworkflow">NoWorkflow</a>
<a href="https://github.com/usnistgov/corr-maestrowf">MaestroWf</a>
<a href="https://github.com/usnistgov/corr-aiida">Aiida</a>
<a href="https://github.com/usnistgov/corr-pandaa">Panda</a>

</strong></sup></p>

<p align="center">
<a href="https://corr.nist.gov" target="_blank">
<img src="https://img.shields.io/badge/corr-nist-cyan.svg"
alt="CoRR NIST Public Instance">
</a>
<a href="https://corrworkspace.slack.com" target="_blank">
<img src="https://img.shields.io/badge/corr-slack-purple.svg"
alt="Slack">
</a>
<a href="http://corr.readthedocs.io/en/v0.2" target="_blank">
<img src="https://readthedocs.org/projects/corr/badge/?version=v0.2" alt="Reathedocs">
</a>
<a href="https://www.youtube.com/playlist?list=PLiWY1GXAXKFk4aSwI9CfyAoDwR6bjD8zV">
<img src="https://img.shields.io/badge/corr-youtube-red.svg" alt="Youtube Playlist" height="18">
</a>
<a href="https://github.com/usnistgov/corr/blob/master/LICENSE">
<img src="https://img.shields.io/badge/license-mit-blue.svg" alt="License" height="18">
</a>
</p>

# Overview

<p align="justify">
The Cloud of Reproducible Records (CoRR) is a web platform for storing and
viewing metadata and data associated with simulation records for reproducibility and beyond.
It is designed as a gateway for execution management tools that aim in capturing software
executions. The need of those records for recalls, reproducibility, education, provenance
and posterity is so critical now more than ever.
</p>
<p align="justify">
The platform is composed of five components. A database component which stores the meta-data about
the diverse entities in relationship within the platform. An api component which identifies and allow
software management tools to interact with the platform. A cloud component dedicated for the frontend
component access to the meta-data and records. A storage component that handles non meta-data
files management.
</p>
<p align="justify">
The CoRR platform is programming language agnostic, recording style and process independent. Instead
of focusing in these specifics, the platform comes at a higher level by providing a unified gateway for
execution management tools. They are the ones who handle these specifics. The platform focuses on networking
records and scientists. Thus, making the long term survival of research reproducibility its core goal.
</p>
<p align="justify">
A CoRR instance is composed of five micro-services. The database micro-service which is a mongodb database
combined with a python shared library corrdb for distributed entities models to the other micro-services. The
api micro-service (corrapi) which is a restfull service that is the interface dedicated to execution management
tools. The cloud micro-service which is a second restfull service (corrcloud) dedicated to the view
micro-service (corrview) which is the frontend exposed to web users. Finally a nginx service takes care of
unifying the access to the corrcloud, corrapi and corrview. Information on how to launch a CoRR instance is
provided in <a href="./LAUNCH.md">How to use</a> and also in videos (click on the corr youtube badge above.).
</p>

## Citation

* [Congo, F.Y.P., Wheeler, D., Hill, D.R.C. 2015. Building a Cloud Service for Reproducible Simulation Management. SciPy proceedings. 2015.](http://conference.scipy.org/proceedings/scipy2015/pdfs/yannick_congo.pdf)
* [Congo, F. Y. P. 2015. CoRR - Materials Genome Initiation (MGI) at NIST.](https://mgi.nist.gov/cloud-reproducible-records)
