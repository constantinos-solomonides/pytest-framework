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

-------------------------- CURSOR CONCATENATION START --------------------------

The system is composed of the following elements, designed for modular
deployment on a single host.

#### 1. Version Control System (VCS)

Online version control system. Hosts the repository, manages MRs, and
triggers pipelines on push events.

* GitHub - widely adopted, mature CI/CD via Actions, large ecosystem
* GitLab (Self-hosted) - built-in CI/CD and MR gating, full data control,
  integrated container registry
* Bitbucket - integrates with Atlassian tooling (Jira, Confluence), common
  in enterprise environments

#### 2. CI/CD Runner

Executes pipeline stages. Responsible for orchestrating linting, build,
deploy, and test stages.

* GitHub Actions - native to GitHub, zero additional infrastructure if GitHub
  is the VCS; requires a local runner for on-premises deployment
* GitLab CI - native to GitLab, tightly coupled with MR workflows; native
  Docker-in-Docker support; simple runner registration
* Jenkins - VCS-agnostic, highly configurable, self-hostable, large plugin
  ecosystem; higher maintenance overhead

#### 3. Linter

Static analysis tooling invoked in the first pipeline stage. Reports issues
back to the MR.

* ruff - very fast Python linter, combines rules from multiple tools (flake8,
  isort), actively maintained
* flake8 - lightweight, mature, wide adoption
* pylint - deeper analysis, catches a wider range of issues at the cost of
  verbosity and speed

#### 4. Notification Service

Lightweight service exposing a dummy API that accepts structured messages from
pipeline stages and forwards them to configured platforms. Initially a stub;
actual platform integrations are an action point.

* Custom REST API - simple to implement, full control over message schema and
  routing
* Targets once implemented: MR comments, Slack, email

#### 5. Build System

Compiles or packages the application into deployable artifacts.

* Docker - containerized builds, reproducible environments, fits the
  single-host constraint
* Make - simple and widely understood, good for orchestrating multi-step build
  processes
* setuptools / pip - standard Python packaging, relevant if the application is
  Python-based

#### 6. Artifact Tracker

Stores build outputs such as container images or packages.

* Local Docker Registry - low overhead, fast image pulls on the same host; no
  GUI, requires manual cleanup
* GitHub/GitLab Packages - integrated with the VCS, no extra infrastructure;
  consumes storage quotas
* Nexus - supports multiple artifact formats, self-hostable, suitable for
  heterogeneous setups
* Harbor - enterprise-grade image scanning and UI; likely too heavy for the
  toy setup

#### 7. Log Tracker

Centralized log storage for build and test outputs.

* Native pipeline logs - simplest option, no extra infrastructure, limited
  search capability
* Loki + Grafana - lightweight log aggregation, self-hostable, powerful query
  language (LogQL)
* ELK stack - powerful search and visualization, but heavy for a single-host
  setup

#### 8. Deployment Target

The environment where the application is deployed for testing. Given the
single-host constraint, likely containers or lightweight VMs.

* Docker Compose - multi-container orchestration on a single host, simple
  declarative YAML configuration
* Podman (with Podman Compose) - daemonless, rootless by default, largely
  Docker-compatible; occasional edge-case differences
* LXC/LXD - lightweight system containers, closer to full VMs, stronger
  isolation

#### 9. Test Runner

Executes the automated test suite against the deployed application and
uploads results and logs.

* pytest - Python-native, extensive plugin ecosystem, flexible fixture system
* Robot Framework - keyword-driven, good for acceptance testing, readable by
  non-developers
* Behave - BDD-style testing for Python, useful when test cases must be
  readable by non-technical stakeholders

#### Notes

* MR state gating (e.g. detecting draft status, checking for open MRs)
  needs to be clarified once the VCS is selected. Some systems (GitLab,
  GitHub) have this baked into their pipeline configuration; others may
  require external logic or webhook handlers.
* Readiness verification between deployment and test execution is the
  responsibility of the installer/deployment process. The installer must
  explicitly signal a successful deployment before the test stage proceeds.
  The specific mechanism will depend on the application being deployed.

--------------------------- CURSOR CONCATENATION STOP --------------------------


------------------------------ GEMINI OUTPUT START -----------------------------

The infrastructure is designed to be modular and executable on a single host.

#### 1. Version Control System (VCS)
Acts as the source of truth and the primary trigger for the automation pipeline.
*   **GitHub**
    *   **Pros**: Industry standard, seamless GitHub Actions integration, extensive documentation.
    *   **Cons**: Some advanced features are paywalled; relies on external cloud availability.
*   **GitLab (Self-hosted)**
    *   **Pros**: Complete control over data; integrated CI/CD and Container Registry; ideal for single-host setups.
    *   **Cons**: Resource-intensive to run alongside the application on home-grade hardware.

#### 2. CI/CD Orchestrator
The engine that interprets the pipeline definition and manages the lifecycle of each stage.
*   **GitHub Actions**
    *   **Pros**: No infrastructure to maintain; massive marketplace of pre-built actions.
    *   **Cons**: Requires a local runner for "on-premises" deployment to the host.
*   **GitLab CI**
    *   **Pros**: Tightly coupled with the VCS; simple runner registration; native support for Docker-in-Docker.
    *   **Cons**: Configuration can become complex for multi-project pipelines.

#### 3. Container Engine & Orchestration
Provides the environment for both the application under test and the transient testing tools.
*   **Docker Compose**
    *   **Pros**: Simple, YAML-based configuration; perfect for orchestrating a few service containers on one host.
    *   **Cons**: Lacks advanced features like auto-healing or secret management found in Kubernetes.
*   **Podman Compose**
    *   **Pros**: Daemonless and rootless by default, offering better security.
    *   **Cons**: Occasional compatibility edge cases with standard Docker Compose files.

#### 4. Artifact & Log Management
Centralized storage for build outputs and execution traces.
*   **Local Registry + Filesystem Mounts**
    *   **Pros**: Minimal resource footprint; extremely fast local transfers.
    *   **Cons**: Lacks a GUI for browsing artifacts; requires custom scripts for log rotation.
*   **Harbor (Self-hosted)**
    *   **Pros**: Enterprise-grade security and image scanning; excellent UI.
    *   **Cons**: Likely too heavy for the "toy setup" constraints.

#### 5. Test Execution Environment
A dedicated containerized environment where the test suite is executed.
*   **Pytest in Docker**
    *   **Pros**: Highly extensible via plugins; uses the same language as the backend (Python).
    *   **Cons**: Requires careful management of container networks to reach the application.
*   **Robot Framework**
    *   **Pros**: High-level, keyword-driven syntax; generates excellent built-in reports.
    *   **Cons**: More verbose than pure Python for complex data manipulation.

------------------------------ GEMINI OUTPUT STOP ------------------------------


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

-------------------------- GEMINI CONCATENATION START --------------------------

The infrastructure is designed as a modular, containerized ecosystem optimized for 
execution on a single host.

#### 1. Version Control System (VCS)
Hosts the repository and manages Merge Requests (MRs).
*   **GitHub**
    *   **Pros**: Industry standard, seamless Actions integration.
    *   **Cons**: Cloud-dependent; some advanced features are paid.
*   **GitLab (Self-hosted)**
    *   **Pros**: Full data control; integrated container registry and CI.
    *   **Cons**: Resource-intensive to host on a single machine.
*   **Bitbucket**
    *   **Pros**: Strong integration with Atlassian tools like Jira.
    *   **Cons**: Smaller action/plugin ecosystem compared to GitHub/GitLab.

#### 2. CI/CD Orchestrator
Orchestrates the lifecycle of build, deploy, and test stages.
*   **GitHub Actions**
    *   **Pros**: Zero infrastructure maintenance; vast marketplace of actions.
    *   **Cons**: Requires a local runner for deployments to the host.
*   **GitLab CI**
    *   **Pros**: Native MR gating; simple runner registration.
    *   **Cons**: Complex to manage for very large, multi-repo setups.
*   **Jenkins**
    *   **Pros**: VCS-agnostic; highly extensible with thousands of plugins.
    *   **Cons**: High maintenance overhead; requires significant configuration.

#### 3. Linter (Static Analysis)
Invoked early in the pipeline to catch syntax and style issues.
*   **ruff**
    *   **Pros**: Extremely fast; combines rules from multiple tools.
    *   **Cons**: Newer than established tools; might lack niche plugins.
*   **flake8 / pylint**
    *   **Pros**: Mature; deep analysis of Python code quality.
    *   **Cons**: Significantly slower execution than ruff.

#### 4. Artifact & Build Management
Stores container images and deployment packages.
*   **Local Docker Registry**
    *   **Pros**: Low overhead; fast image pulls on the same host.
    *   **Cons**: No graphical interface; manual cleanup scripts required.
*   **GitHub/GitLab Packages**
    *   **Pros**: Integrated into the VCS; no extra infrastructure.
    *   **Cons**: Consumes storage/bandwidth quotas; requires internet.

#### 5. Log Tracker
Centralized storage for build and test outputs.
*   **Native Pipeline Logs**
    *   **Pros**: No setup required; directly linked to build jobs.
    *   **Cons**: Limited searchability; logs are lost if jobs are deleted.
*   **Loki + Grafana**
    *   **Pros**: Lightweight; powerful query language (LogQL); self-hostable.
    *   **Cons**: Adds complexity to the single-host infrastructure.

#### 6. Deployment Target
The environment where the application is deployed for testing.
*   **Docker Compose**
    *   **Pros**: Simple YAML configuration; native to the Docker ecosystem.
    *   **Cons**: Lacks advanced features like auto-healing or secret management.
*   **Podman**
    *   **Pros**: Daemonless and rootless; enhanced security profile.
    *   **Cons**: Subtle differences in CLI flags compared to Docker.

#### 7. Test Runner
Executes the automated test suite and generates reports.
*   **pytest**
    *   **Pros**: Python-native; massive plugin ecosystem; simple syntax.
    *   **Cons**: Requires Python knowledge to maintain complex test logic.
*   **Robot Framework**
    *   **Pros**: Keyword-driven; readable by non-developers; great reporting.
    *   **Cons**: Can be restrictive for highly custom low-level testing.

--------------------------- GEMINI CONCATENATION STOP --------------------------


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

-------------------------- CURSOR CONCATENATION START --------------------------

The mock twitter clone is composed of the following components.

#### 1. Frontend

Web-based user interface. Displays posts and provides login and posting
functionality.

* Serves a timeline view accessible without authentication
* Provides a login form and post submission form
* Enforces the 256 ASCII character limit client-side as a first line of
  validation
* Candidate stack: React/TypeScript (component-based, rich testing
  ecosystem, type safety)

#### 2. Backend API

Server-side application exposing a REST API consumed by the frontend.

* Handles post retrieval (public, no auth required)
* Handles post creation (authenticated users only)
* Enforces the 256 ASCII character limit server-side as the authoritative
  validation
* Enforces the 10-second duplicate rejection rule per user
* Manages authentication and session state
* Candidate stack: FastAPI/Python (async support, automatic OpenAPI docs)

#### 3. Database

Persistent storage for users and posts.

* Stores user credentials and profile data
* Stores posts with metadata (author, timestamp, content)
* Candidate: SQLite (zero-config, file-based, fits single-host constraint)

#### 4. Authentication

Mechanism for verifying user identity. Could be a separate service or a
module within the backend.

* Handles login and session/token issuance
* Guards post-creation endpoints
* Candidate: JWT (stateless, simplifies testing of protected endpoints)

#### 5. Service Orchestration

Manages the lifecycle of all application containers as a single deployable
unit.

* Launches frontend, backend, and database together
* Provides a consistent target for automated tests
* Candidate: Docker Compose (simple YAML config, single-command startup)

--------------------------- CURSOR CONCATENATION STOP --------------------------


------------------------------ GEMINI OUTPUT START -----------------------------

The mock application is built using a lightweight, modern stack designed for rapid deployment and testing:

*   **Frontend (React / TypeScript)**
    *   **Reason**: Provides a robust ecosystem for component testing and E2E automation; allows for immediate user feedback on post-length and character constraints.
*   **Backend API (FastAPI / Python)**
    *   **Reason**: Extremely fast to develop and performant; handles the 10-second duplicate check logic efficiently with asynchronous tasks; automatically generates interactive API documentation.
*   **Database (SQLite)**
    *   **Reason**: A zero-config, file-based database that fits perfectly within a single-host environment, avoiding the resource overhead of a dedicated database server.
*   **Authentication (JWT - JSON Web Tokens)**
    *   **Reason**: Enables stateless communication between the frontend and backend, simplifying the testing of protected endpoints without managing server-side session state.
*   **Service Orchestration (Docker Compose)**
    *   **Reason**: Ensures the entire application stack (frontend, backend, and database) can be launched reliably with a single command, providing a consistent target for automated tests.

------------------------------ GEMINI OUTPUT STOP ------------------------------


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

-------------------------- GEMINI CONCATENATION START --------------------------

The mock application is designed as a multi-tier web application optimized for 
containerized testing.

#### 1. Frontend (Web UI)
Displays posts and provides login and posting functionality.
*   **React / TypeScript (SPA)**
    *   **Pros**: Component-based; rich testing ecosystem; static type safety.
    *   **Cons**: Requires a build step; can have large bundle sizes.
    *   **Role**: Enforces the 256 ASCII character limit client-side; serves the 
        timeline view and login forms.

#### 2. Backend API
Exposes a REST API consumed by the frontend.
*   **FastAPI / Python**
    *   **Pros**: High performance; automatic OpenAPI docs; asynchronous support.
    *   **Cons**: Python's GIL can be a bottleneck for CPU-bound tasks.
    *   **Role**: Authoritative business logic; manages authentication state; 
        enforces the 10-second duplicate rejection rule per user.

#### 3. Database
Persistent storage for users and posts.
*   **SQLite**
    *   **Pros**: Zero-config; portable; minimal resource footprint.
    *   **Cons**: Limited concurrency for write-heavy production workloads.
*   **PostgreSQL (Alternative)**
    *   **Pros**: Robust; supports complex queries and high concurrency.
    *   **Cons**: Requires more setup and resources than SQLite.
    *   **Role**: Stores credentials, profiles, and posts with author/timestamp 
        metadata.

#### 4. Authentication
Mechanism for verifying user identity.
*   **JWT (JSON Web Tokens)**
    *   **Pros**: Stateless; easily distributed; standard-based.
    *   **Cons**: Revocation is difficult; payload is visible if not encrypted.
*   **Session-based (Alternative)**
    *   **Pros**: Easy revocation; simpler for small apps.
    *   **Cons**: Requires server-side state; harder to scale horizontally.
    *   **Role**: Handles login and token issuance; guards post-creation 
        endpoints.

#### 5. Service Orchestration
Manages the lifecycle of the application containers.
*   **Docker Compose**
    *   **Pros**: Simple multi-service management; consistent environments.
    *   **Cons**: Not suitable for large-scale production clustering.
    *   **Role**: Ensures Frontend, API, and DB are launched as a single 
        reliable unit for testing.

--------------------------- GEMINI CONCATENATION STOP --------------------------


### Test suite

TODO AI

-------------------------- CURSOR CONCATENATION START --------------------------

The test suite validates the application across three levels: end-to-end
user workflows, component integration, and isolated unit logic.

#### Suggested tooling

Frameworks and libraries for executing tests at each level.

* E2E: Playwright - real browser automation, multi-browser support,
  auto-waiting reduces flakiness; Selenium as a fallback with broader
  legacy support
* Integration: pytest with HTTPX - async-capable HTTP client, direct API
  contract testing without browser overhead
* Unit: pytest - fast execution, granular failure reports, extensive plugin
  ecosystem, flexible fixture system

#### End-to-end tests

Validate complete user workflows through the full stack.

* View timeline without logging in - confirms posts are visible to
  unauthenticated users
* View timeline when no posts exist - confirms the system handles an empty
  state gracefully
* Log in and create a post - confirms the full post-creation flow from
  login through submission to timeline display
* Create multiple posts in succession - confirms repeated posting works and
  all posts appear on the timeline
* Attempt to post without logging in - confirms the system rejects
  unauthenticated post attempts
* Attempt to log in with invalid credentials - confirms the system rejects
  the attempt and displays an appropriate error
* Attempt to log in with empty credentials - confirms the system rejects
  blank username/password
* Log out and attempt to post - confirms the system enforces authentication
  after session ends
* Submit a post exceeding 256 ASCII characters - confirms the system
  rejects oversized posts
* Submit a post at exactly 256 ASCII characters - confirms the boundary is
  accepted
* Submit a post at 257 ASCII characters - confirms the first over-limit
  value is rejected
* Submit an empty post (0 characters) - confirms the system rejects
  zero-length content
* Submit a post containing only whitespace - confirms the system rejects
  content with no non-whitespace characters
* Submit a post with special ASCII characters (e.g. control characters,
  backslashes, quotes) - confirms the system handles them without breaking
* Two different users post identical content - confirms both posts are
  accepted independently and appear on the timeline
* Same user posts identical content more than 10 seconds apart - confirms
  both posts are accepted
* Same user submits identical content within 10 seconds - confirms the
  system rejects the second submission as a duplicate
* Rapid duplicate submission of the same post (e.g. double-click) -
  confirms the system deduplicates within the short timespan window

#### Integration tests

Validate interactions between components at the API and service boundary.

* Backend API returns posts from the database without authentication
* Backend API returns an appropriate response when no posts exist
* Backend API rejects post creation when no valid session/token is provided
  (expects 401)
* Backend API accepts post creation with a valid session/token
* Backend API rejects posts exceeding 256 ASCII characters and returns an
  appropriate error
* Backend API rejects empty or whitespace-only posts
* Backend API accepts identical content from two different authenticated
  users
* Backend API accepts identical content from the same user when submissions
  are more than 10 seconds apart
* Backend API rejects identical content from the same user when submissions
  are within 10 seconds
* Backend API rejects duplicate submissions at exactly 10 seconds and
  accepts at 11 seconds (boundary precision)
* Backend API rejects a malformed or tampered-with authentication token
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
* Duplicate detection - rejects same content from same user within 10
  seconds
* Duplicate detection - accepts same content from same user beyond 10
  seconds
* Duplicate detection - accepts same content from different users
  regardless of timing
* Timestamp comparator - verifies the 10-second window calculation in
  isolation
* Credential validation logic - correct and incorrect inputs
* Credential validation logic - empty inputs

--------------------------- CURSOR CONCATENATION STOP --------------------------


------------------------------ GEMINI OUTPUT START -----------------------------

The test suite is structured to provide high confidence through multiple layers of verification:

#### End-to-End (E2E) Tests
*Focus: User-centric workflows using the full stack via Playwright or Selenium.*
*   **Public Access**: Verify that unauthenticated users can view the global timeline.
    *   **Reason**: Confirms the app is accessible and the basic read-flow is functional.
*   **Authenticated Posting**: Verify a user can log in, create a valid post, and see it appear on the timeline.
    *   **Reason**: Validates the core value-proposition and the integration of Auth, API, and Database.
*   **Negative: Unauthorized Posting**: Attempt to submit a post after a session has expired or after logging out.
    *   **Reason**: Ensures that security boundaries are enforced at the UI layer and that the user is redirected or prompted.
*   **Corner: Boundary Content**: Submit a post that is exactly 256 characters long and another that contains exactly one non-whitespace character.
    *   **Reason**: Confirms that the system correctly handles the limits of the defined business rules.
*   **Corner: Concurrency/Deduplication**: Rapidly click the "Post" button multiple times (double-click) to trigger simultaneous requests.
    *   **Reason**: Tests the robustness of the frontend and backend against race conditions or accidental double-submissions.

#### Integration Tests
*Focus: API contracts and component interactions.*
*   **API Security**: Ensure the /post endpoint returns a 401 Unauthorized without a valid JWT.
    *   **Reason**: Directly tests the Auth Provider's protection of the Backend API.
*   **Negative: Oversized Payload**: Send a 257+ character post directly to the API, bypassing frontend validation.
    *   **Reason**: Validates that the backend acts as the authoritative source of truth for business rules.
*   **Negative: Invalid Auth Token**: Submit a post with a malformed or tampered-with JWT.
    *   **Reason**: Verifies the integrity of the token validation logic in the Auth module.
*   **Corner: Precise Duplicate Window**: Submit identical posts exactly 10 seconds apart and 11 seconds apart.
    *   **Reason**: Verifies the exactness of the duplicate detection window implementation.

#### Unit Tests
*Focus: Isolated business logic and utility functions.*
*   **Content Validator**: Test the 256-character boundary and ASCII-only constraints in isolation.
    *   **Reason**: Fast, low-overhead verification of the core data-integrity rules.
*   **Negative: Empty/Whitespace Input**: Pass null, empty strings, and strings with only tabs or newlines to the validator.
    *   **Reason**: Ensures the "minimum content" rule is robust against diverse whitespace characters and edge inputs.
*   **Corner: Special ASCII Characters**: Test strings containing control characters, backslashes, and quotes.
    *   **Reason**: Confirms that the sanitization and storage logic handles valid but potentially problematic ASCII symbols safely.
*   **Timestamp Comparator**: Verify the logic that calculates the 10-second window for duplicate detection.
    *   **Reason**: Isolates the time-calculation logic from the API/Database layers.

------------------------------ GEMINI OUTPUT STOP ------------------------------


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

-------------------------- GEMINI CONCATENATION START --------------------------

The test suite is structured to provide exhaustive verification across all 
architectural layers, from individual logic units to full user workflows.

#### I. Testing Tools
The following frameworks are used to execute the test suite at different levels 
of isolation.

*   **E2E Framework: Playwright / Selenium**
    *   **Pros**: Real browser testing; captures UI/UX regressions; multi-browser 
        support.
    *   **Cons**: Slower execution; prone to flakiness if not properly isolated.
    *   **Reason**: Ensures the full system (Frontend, API, DB) works together 
        from the user's perspective.
*   **Integration Framework: Pytest with Requests/HTTPX**
    *   **Pros**: Fast execution; isolates backend logic from UI flakiness; 
        easy API contract testing.
    *   **Cons**: Does not catch frontend-only rendering or state issues.
    *   **Reason**: Validates API security and database persistence without the 
        overhead of a browser.
*   **Unit Framework: Pytest**
    *   **Pros**: Extremely fast; provides granular failure reports; simple 
        syntax.
    *   **Cons**: Limited scope; does not verify connectivity between services.
    *   **Reason**: Allows for rapid iteration on core business rules and 
        validation logic.

#### II. Test Cases
Each level of testing addresses specific functional and security requirements.

**End-to-End (E2E) Tests**
*   Verify that unauthenticated users can view the global timeline.
*   Verify that the system handles an empty timeline state gracefully.
*   Verify a user can log in and successfully create a post.
*   Verify that multiple posts created in succession all appear on the timeline.
*   Verify that the system rejects post attempts without logging in.
*   Verify rejection of login attempts with invalid credentials.
*   Verify rejection of login attempts with empty credentials.
*   Verify that logging out prevents further posting and clears the session.
*   Verify UI rejection and error messaging for posts exceeding 256 characters.
*   Verify that a post at exactly 256 characters is accepted.
*   Verify that a post at 257 characters is rejected at the UI layer.
*   Verify rejection of empty posts (0 characters) in the UI.
*   Verify rejection of posts containing only whitespace in the UI.
*   Verify that the UI correctly handles special ASCII characters (backslashes, 
    quotes).
*   Verify that two different users can post identical content.
*   Verify that the same user can post identical content more than 10 seconds 
    apart.
*   Verify rejection of identical content from the same user within 10 seconds.
*   Verify system behavior during rapid duplicate submissions (double-click).

**Integration Tests**
*   Verify the Backend API returns posts without authentication.
*   Verify the Backend API returns appropriate responses for empty states.
*   Verify the Backend API returns 401 Unauthorized for missing session tokens.
*   Verify the Backend API accepts post creation with a valid session token.
*   Verify the Backend API rejects posts exceeding 256 characters (Negative).
*   Verify the Backend API rejects empty or whitespace-only posts (Negative).
*   Verify the Backend API accepts identical content from different users.
*   Verify the Backend API accepts identical content from the same user 
    beyond 10s.
*   Verify the Backend API rejects identical content from the same user 
    within 10s.
*   Verify the Auth module issues a valid session token on correct credentials.
*   Verify the Auth module rejects invalid credentials.
*   Verify the Auth module rejects empty credentials.
*   Verify rejection of expired or invalidated session tokens (Security).
*   Verify the Backend API rejects malformed or tampered-with JWT tokens.
*   Verify database persistence for successful API calls.
*   Verify precise duplicate detection at exactly 10s and 11s boundaries.

**Unit Tests**
*   Verify content validator rejects content over 256 ASCII characters.
*   Verify content validator rejects content at 257 characters.
*   Verify content validator accepts content at exactly 256 characters.
*   Verify content validator rejects empty content.
*   Verify content validator rejects whitespace-only content.
*   Verify content validator rejects non-ASCII characters.
*   Verify content validator handles special ASCII characters safely.
*   Verify duplicate detection logic rejects same user/content within 10s.
*   Verify duplicate detection logic accepts same user/content beyond 10s.
*   Verify duplicate detection logic accepts same content from different users.
*   Verify credential validation logic handles correct and incorrect inputs.
*   Verify credential validation logic handles empty inputs.
*   Verify timestamp comparison logic for the 10-second window in isolation.
*   Verify sanitization logic against diverse whitespace (tabs, newlines).

--------------------------- GEMINI CONCATENATION STOP --------------------------

