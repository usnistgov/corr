<p align="center">
    <img src="https://rawgit.com/usnistgov/corr/master/corr-view/frontend/images/logo.svg"
         height="240"
         alt="CoRR logo"
         class="inline">
</p>

<h1> <p align="center"><sup><strong>
CoRR &ndash; API
</strong></sup></p>
</h1>

## Description

This component of CoRR is a python flask service that is the access point for
software management tools to communicate with the CoRR backend. To be able to
be access the CoRR API a software management tool needs an application key.
The later can only be retrieved from the online creation of an application
instance. When an application token is retrieved it has to be provided within
a config file downloadable from the user profile. This way access to the backend
API provide information about the application in question and the user credentials
used for the requests.
