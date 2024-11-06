# :whale: Docker: best practices for application development 

[![CI](https://github.com/moonraker595/dockerBestPractices/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/moonraker595/dockerBestPractices/actions/workflows/main.yml)

This document provides best practices for developing applications targeted for deployment in a Kubernetes (K8s) environment.

Kubernetes introduces specific requirements and considerations for application architecture, particularly in containerisation, configuration management, logging, monitoring, and security. These guidelines aim to streamline the development process, improve scalability, and reduce deployment issues.

> **Note:** These are recommendations, not requirements. Not all applications require this set-up, but if the application is to be deployed in a K8s environment then building these recommendations into the application will help streamline deployment later on.

## End goal

As a developer, the end goal is to have an application which is tested in the CI, in a container and then pushed to [our Harbor repository](https://harbor.stfc.ac.uk/). This means that the image will be:

- Tested from inside a container, like it is going to be ran
- Be available in Harbor for deployment into the K8s cluster
- Be available  in Harbor for other apps to use as a dependency

## Example FastAPI Project

The code snippets in this document are taken from this repository, which returns the fictional icat user details given a username in the URL. 
For example, after running `docker compose up`:

Go to the following address in your browser: http://127.0.0.1:8000/icat/Karen482

It should return something like:

```json
{
  "createId": "user",
  "createTime": "2009-02-18T13:40:27+00:00",
  "id": 482,
  "modId": "user",
  "modTime": "2008-12-18T19:17:14+00:00",
  "affiliation": "University Of Cambridge",
  "email": "ruizjason@gmail.com",
  "fullName": "Timothy Buchanan",
  "name": "Karen482",
  "orcidId": "16799"
}
```

## Containerisation Standards

- A single, multistage docker build process helps keep the images lean and allows one docker file for testing and production. 
- In the example, a `base`, `production`, and `test` stages are defined. The type of stage that is run depends on the `target` set in the compose file.

## Logging and metrics

- A `/metrics` endpoint is needed for a service to poll and gather data. The example app uses the Prometheus python client to help collect metrics within the app, metricbeat is then set up to poll this endpoint and forward them to ElasticSearch to persist the data. These can then be visualised in a dashboard in Kibana. 

> **Note:** Equally, a Prometheus server and Gafana dashboard could be set up to visualise metrics, but as a developer, you only need to make sure these are collected within the app and outputted via a /metrics endpoint. 

- The example app also uses the ELK stack for logging. File Beat has been configured to monitor the docker container logs for this application and forward them to Elasticsearch for persistence. In the example stack, these can be seen in Kibana at http://localhost:5601/app/logs. 

  As a developer, you just need to output the logs in a standard JSON format to make filtering/search easier. For example:	

  ```python
  def format(self, record):
      log_record = {
          "level": record.levelname,
          "message": record.getMessage(),
          "timestamp": self.formatTime(record),
          "app": "example_app", #To Help filter on them in Kibana
      }
      return json.dumps(log_record)
  ```

## Testing & Development

- Tests should be run locally against a compose stack, as well as part of the compose stack. In most cases, the app can be developed/debugged/tested in an IDE against a local compose stack (with the app running locally and commented out in the compose file). It should also be able to run as part of the compose stack, proving it can:

  - be tested from within a container which in turn proves it can...
  - be able to communicate with other dependencies (in this example, ICAT) from within a container.

- This does mean more work 😢, as you have to first get the tests running locally and then from within a container.

- In most cases, switching between the full docker-compose stack and running the application locally usually means changing a few URLs. The video clip [here](./images/recording.mp4) shows how, for example, we can go from running the application with production and test targets against a compose stack to locally running the application for debugging and testing purposes.


## Configuration & Dependency Management

- Configuration should be passed in via `.env` files. In the cluster, the real config (and probably any secrets) will be passed in via a third-party tool (like [Vault](https://developer.hashicorp.com/vault/tutorials/getting-started/getting-started-intro)) which will be responsible for injecting the environment variables into the container. The source code should still hold an example `env` files (or equivalent) to facilitate local development and testing.
- In most cases, dependencies can be managed by a simple requirements.txt.
- Where the entire dependency tree needs to be managed through `poetry.lock` and `pyproject.toml` files, Poetry can be installed in the base stage to run `poetry install...`. 
- As Docker itself is a virtual environment it doesn't make sense to have a virtual environment inside a virtual environment. So `poetry.run` should not be used to start the app or run tests.
- Likewise with Ansible. Docker and K8s define how the app is run so Ansible isn't used with these technologies.


## Health Check Endpoint

- K8s will need an endpoint to poll in order to determine whether the application is up or not. This should be a simple endpoint which returns a `200`, Like a `/version` endpoint or an empty `/healthz` endpoint.

## CI Tests

- The CI should be running the tests from within a container against the compose stack. In this example, the CI builds an image with the test target set, runs the tests and, if successful, builds and pushes a production image to Habour.

- This can then be pulled in the compose file and used with the compose stack by using the Harbor URL instead of the local dockerfile. 

  - This will allow other services to use this application in their docker compose file without having to pull the code.

- In the example compose file, a build target can be specified:

  ```yaml
    fastapi-app:
      container_name: fastapi-app
      # This will build from the local Dockerfile
      build:
        target: production # or test
      depends_on:
        icat_mariadb:
          condition: service_healthy
        testdata:
          condition: service_completed_successfully
      ports:
        - "8000:8000"
  ```

  or the image to pull from harbor, but not both:

  ```yaml
  fastapi-app:
    container_name: fastapi-app
   # The following line will pull the prod image from harbor, built by the CI, instead of building it from local code
    image: harbor.stfc.ac.uk/dseg/api:main 
    depends_on:
      icat_mariadb:
        condition: service_healthy
      testdata:
        condition: service_completed_successfully
    ports:
      - "8000:8000"
  ```