# :whale: Docker: best practices for application development 

This document provides best practices for developing applications targeted for deployment in a Kubernetes (K8s) environment.

Kubernetes introduces specific requirements and considerations for application architecture, particularly in containerisation, configuration management, logging, monitoring, and security. These guidelines aim to streamline the development process, improve scalability, and reduce deployment issues.

This document includes detailed guidance on:

- **Containerisation Standards** – Structuring, building, and optimising container images.
- **Configuration Management** – Managing environment variables, secrets, and configurations.
- **Logging and Monitoring** – Enabling observability with standardised logging and metrics tools.
- **Security Considerations** – Key security practices.
- **Testing Strategies** – Techniques for testing an app within a container.

Note: These are recommendations, not requirements. Not all applications require this set-up, but if the application is to be deployed in a K8s environment then building these recommendations into the application will help streamline deployment later on.

## End goal

As a developer, the end goal is to have an application which is tested in the CI, in a container and then pushed to [our Harbor repository](https://harbor.stfc.ac.uk/). This means that the image will be:

- Tested from inside a container, like it is going to be ran
  - Be able to have the necessary config passed to it at runtime
- Be available in Harbor for deployment
- Be available for other apps to use as a dependency, pulled from Harbor

## Example FastAPI Project

The code snippets in this document are taken from [an example stack](https://github.com/moonraker595/dockerBestPractices) which returns the fictional icat user details given a username. 
For example, after running `docker compose up`:

 http://127.0.0.1:8000/icat/Karen482

should return something like:

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

- A single, multistage docker build process helps keep the images lean and allows one docker file for testing and production. In the example, a base, production, and test stages are defined. The type of stage that is run depends on the `target` set during the image build process.

## Logging and metrics

- A `/metrics` endpoint is needed for a service to poll and gather data. The example app uses the Prometheus python client to help collect metrics within the app, metricbeat is then set up to poll this endpoint and forward them to Elastic Search to persist the data, which can then be visualised in a dashboard in Kibana. 


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

- Test locally against a compose stack, as well as part of the compose stack. In most cases, the app can be developed/debugged/tested in an IDE against a local compose stack (with the app running locally and commented out in the compose file). It should also be run as part of the compose stack, proving it can:

  - be tested from within a container which in turn proves it can...
  - be able to communicate with other dependencies (for example, ICAT) from within a container.

- This does mean more work 😢, as you have to first get the tests running locally and then from within a container.

- The video clip [here](./images/recording.mov) shows how, for example, we can go from running the application with production and test targets against a compose stack, to locally running the application for debugging and testing purposes.

  

## Configuration Management 





## Health Check Endpoint

- K8s will need an endpoint to poll in order to determine whether the application is up or not. This should be a `/version` endpoint