# Cloud of Reproducible Records Database

CoRR is a Plateform designed to store records from SMT initially.
It allows scientists to automatically push their record in the cloud
and be able to display and manipulate them later. Also CoRR is a 
collaboration platform where the interaction between scientists lead to:
- Discussion about records
- Rationels inclusion
- Reproducible tags between each couple of records as: repeated, replicated,
reproduced, non-repeated, non-replicated, non-reproduced.
To run this, you have to run the database first:

    $ sudo mongod --rest

and then:

    $ python run.py

By default it will run on 0.0.0.0 on port 5100. You may
change those by using --host and --port.

To test the api:
    $ nosetests -w absolute_path_to/corr-api/test/ --with-doctest -v

## [Sumatra]()

Sumatra is a command line tool that captures a lot of meta-data
pertaining to a Python execution. Sumatra is primarily aimed at
scientists using Python to run simulations, but the ideas could extend
to many other uses. The captured meta-data is not scientific specific,
but scientist often run the same script multiple times with only
slight modifications to parameter values. Version control alone is not
good at capturing this aspect of the scientific process.

## More reasons for CoRR

CoRR has a web front end and an API that can be scripted and 
used in many simulation management tools (Sumatra), Benchmarking tools,
Evaluation tools, Statistical tools or any other computation regarding
a set of records. CoRR Cloud Plateform is divided into four entities: A
cloud and api backend, a database backend and a frontend view. It can 
be deployed on web hosting services like AWS, Google Apps or Heroku.

## License

[The MIT license.][LICENSE]

## Prerequisites and Installation

See the [installation guide](INSTALLATION.md).