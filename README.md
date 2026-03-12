# pytest-framework-example

This project concerns building an end-to-end testing framework using AI assistance. The end result will be equivalent to
a "toy setup" that can be deployed and individually expanded until it fits production needs.

## Motivation

The system being designed here is meant to serve the following purposes:

* A front-end sample-of-work
* An actual, extensible framework for use where needed
* Practice and familiarization with various AI models and best practices

## System design

**NOTE**: The design is subject to change, because it must be made to run on a single, home-grade host using docker
containers or reasonably-sized VMs.

### Assumptions

* There is some way for a pipeline to be launched after a push:
    * Either the online VCS has the ability to launch a CI/CD pipeline
    * There is an external system polling the VCS that runs pipelines upon commit (not ideal)
* The VCS has the concept of MRs
* The MRs for the VCs can be set in draft mode

### Sequence of events - Flow of control

The system works in the following way:

* User makes commit and pushes to the online VCS (e.g. GitHub, Gitlab, Bitbucket etc.)
* The CI/CD runs linting for the code
* Communicate any issues found
* The commit system checks if there's an open MR for the commit
* If the MR is in draft mode stop
* If the MR is open, the following steps take place (possible second pipeline):
    * Build
    * Upload artifacts to artifact tracker and logs to log tracker
    * Deploy automatically
    * Run automated tests against system
    * Upload logs to log tracker

### Components

TODO AI

##  The application being tested

The application that will be deployed and tested as part of this frameworks development will be a mock twitter clone.

### Capabilities of version v0.1.0

For the first iteration, the application does the following

* Users can view posts without logging-in or while logged-in
* Users **must** log-in to post
* Posts may be up to 256 ASCII characters long

### Components

TODO AI

### Test suite

TODO AI
