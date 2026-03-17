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

------------------- CURSOR OUTPUT START -------------------

The system is composed of the following elements.

#### VCS

Online version control system. Hosts the repository, manages MRs, and triggers pipelines on push events.

* GitHub - widely adopted, mature CI/CD via Actions, large ecosystem of integrations
* GitLab - built-in CI/CD and MR gating, self-hostable, good fit for single-host setups
* Bitbucket - integrates with Atlassian tooling (Jira, Confluence), common in enterprise environments

#### CI/CD Runner

Executes pipeline stages. Responsible for orchestrating linting, build, deploy, and test stages.

* GitHub Actions - native to GitHub, zero additional infrastructure if GitHub is the VCS
* GitLab CI - native to GitLab, tightly coupled with MR workflows and gating
* Jenkins - VCS-agnostic, highly configurable, self-hostable, large plugin ecosystem

#### Linter

Static analysis tooling invoked in the first pipeline stage. Reports issues back to the MR.

* ruff - very fast Python linter, aims to replace flake8 and isort, actively maintained
* flake8 - lightweight Python linter, mature, wide adoption
* pylint - more thorough Python analysis, catches a wider range of issues at the cost of verbosity

#### Notification Service

Lightweight service exposing a dummy API that accepts structured messages from pipeline stages and forwards them to configured platforms. Initially a stub; actual platform integrations are an action point.

* Custom REST API - simple to implement, full control over message schema and routing
* Targets once implemented: MR comments, Slack, email

#### Build System

Compiles or packages the application into deployable artifacts.

* Docker - containerized builds, reproducible environments, fits the single-host constraint
* Make - simple and widely understood, good for orchestrating multi-step build processes
* setuptools / pip - standard Python packaging, relevant if the application is Python-based

#### Artifact Tracker

Stores build outputs such as container images or packages.

* Docker Registry (self-hosted) - straightforward if using Docker builds, can run on the same host
* GitHub Packages - integrated with GitHub, no extra infrastructure if GitHub is the VCS
* Nexus - supports multiple artifact formats, self-hostable, suitable for heterogeneous setups

#### Log Tracker

Centralized log storage for build and test outputs.

* Pipeline job logs (native) - simplest option, no extra infrastructure, limited search capability
* Loki + Grafana - lightweight log aggregation, self-hostable, good query interface
* ELK stack (Elasticsearch, Logstash, Kibana) - powerful search and visualization, but heavy for a single-host setup

#### Deployment Target

The environment where the application is deployed for testing. Given the single-host constraint, likely containers or lightweight VMs.

* Docker Compose - multi-container orchestration on a single host, simple declarative configuration
* Podman - daemonless container engine, rootless by default, largely Docker-compatible
* LXC/LXD - lightweight system containers, closer to full VMs, stronger isolation

#### Test Runner

Executes the automated test suite against the deployed application and uploads results and logs.

* pytest - Python-native, extensive plugin ecosystem, flexible fixture system
* Robot Framework - keyword-driven, good for acceptance testing, readable by non-developers
* Behave - BDD-style testing for Python, useful when test cases must be readable by non-technical stakeholders

> NOTE: MR state gating (e.g. detecting draft status, checking for open MRs) needs to be clarified once the VCS is selected. Some systems (GitLab, GitHub) have this baked into their pipeline configuration; others may require external logic or webhook handlers.

> NOTE: Readiness verification between deployment and test execution is the responsibility of the installer/deployment process. The installer must explicitly signal a successful deployment before the test stage proceeds. The specific mechanism will depend on the application being deployed.

-------------------- CURSOR OUTPUT END --------------------

##  The application being tested

The application that will be deployed and tested as part of this frameworks development will be a mock twitter clone.

### Capabilities of version v0.1.0

For the first iteration, the application does the following

* Users can view posts without logging-in or while logged-in
* Users **must** log-in to post
* Posts may be up to 256 ASCII characters long
* Posts must contain at least one non-whitespace character
* Duplicate posts by the same user are rejected if submitted within 10 seconds of each other; identical content from different users is always accepted

### Components

TODO AI

------------------- CURSOR OUTPUT START -------------------

#### Frontend

Web-based user interface. Displays posts and provides login and posting functionality.

* Serves a timeline view accessible without authentication
* Provides a login form and post submission form
* Enforces the 256 ASCII character limit client-side as a first line of validation

#### Backend API

Server-side application exposing a REST API consumed by the frontend.

* Handles post retrieval (public, no auth required)
* Handles post creation (authenticated users only)
* Enforces the 256 ASCII character limit server-side as the authoritative validation
* Manages authentication and session state

#### Database

Persistent storage for users and posts.

* Stores user credentials and profile data
* Stores posts with metadata (author, timestamp, content)

#### Authentication

Mechanism for verifying user identity. Could be a separate service or a module within the backend.

* Handles login and session/token issuance
* Guards post-creation endpoints

-------------------- CURSOR OUTPUT END --------------------

### Test suite

TODO AI

------------------- CURSOR OUTPUT START -------------------

#### End-to-end tests

Validate complete user workflows through the full stack.

* View timeline without logging in - confirms posts are visible to unauthenticated users
* View timeline when no posts exist - confirms the system handles an empty state gracefully
* Log in and create a post - confirms the full post-creation flow from login through submission to timeline display
* Create multiple posts in succession - confirms repeated posting works and all posts appear on the timeline
* Attempt to post without logging in - confirms the system rejects unauthenticated post attempts
* Attempt to log in with invalid credentials - confirms the system rejects the attempt and displays an appropriate error
* Attempt to log in with empty credentials - confirms the system rejects blank username/password
* Log out and attempt to post - confirms the system enforces authentication after session ends
* Submit a post exceeding 256 ASCII characters - confirms the system rejects oversized posts
* Submit a post at exactly 256 ASCII characters - confirms the boundary is accepted
* Submit a post at 257 ASCII characters - confirms the first over-limit value is rejected
* Submit an empty post (0 characters) - confirms the system rejects zero-length content
* Submit a post containing only whitespace - confirms the system rejects content with no non-whitespace characters
* Submit a post with special ASCII characters (e.g. control characters, backslashes, quotes) - confirms the system handles them without breaking
* Two different users post identical content - confirms both posts are accepted independently and appear on the timeline
* Same user posts identical content at different times (more than 10 seconds apart) - confirms both posts are accepted
* Same user submits identical content within 10 seconds - confirms the system rejects the second submission as a duplicate
* Rapid duplicate submission of the same post (e.g. double-click) - confirms the system deduplicates within the short timespan window

#### Integration tests

Validate interactions between components.

* Backend API returns posts from the database without authentication
* Backend API returns an appropriate response when no posts exist
* Backend API rejects post creation when no valid session/token is provided
* Backend API accepts post creation with a valid session/token
* Backend API rejects posts exceeding 256 ASCII characters and returns an appropriate error
* Backend API rejects empty or whitespace-only posts
* Backend API accepts identical content from two different authenticated users
* Backend API accepts identical content from the same user when submissions are more than 10 seconds apart
* Backend API rejects identical content from the same user when submissions are within 10 seconds
* Authentication module issues a session/token on valid credentials
* Authentication module rejects invalid credentials
* Authentication module rejects empty credentials
* Expired or invalidated session/token is rejected on post creation

#### Unit tests

Validate individual functions and modules in isolation.

* Post content validation - rejects content over 256 ASCII characters
* Post content validation - rejects content at 257 characters
* Post content validation - accepts content at exactly 256 characters
* Post content validation - rejects empty content
* Post content validation - rejects whitespace-only content
* Post content validation - rejects non-ASCII characters if applicable
* Post content validation - handles special ASCII characters without error
* Duplicate detection - rejects same content from same user within 10 seconds
* Duplicate detection - accepts same content from same user beyond 10 seconds
* Duplicate detection - accepts same content from different users regardless of timing
* Credential validation logic - correct and incorrect inputs
* Credential validation logic - empty inputs

-------------------- CURSOR OUTPUT END --------------------
