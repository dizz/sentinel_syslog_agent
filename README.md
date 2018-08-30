# Nexus to Sentinel Syslog Agent

This agent runs and listens upon a UDP port for syslog messages. Those received messages are then converted into a format suitable for consumption by [Sentinel](https://github.com/elastest/elastest-monitoring-platform). The agent can run stand alone, however
it is typically transparently inserted into an application deployment by [Nexus](https://github.com/elastest/elastest-service-manager).

## How to Run

In order to run you need an existing deployment of Sentinel. There is a basic docker-compose description under [test/docker-compose.yml](test/docker-compose.yml)

Once Sentinel is available you will need to create a user (e.g. `syslog_agent`):

```shell
curl -v -X POST http://localhost:9100/v1/api/user/ --header "Content-Type: application/json" --header "x-auth-token: somevalue" -d '{"login":"syslog_agent", "password":"really?!"}'
```

You will then also need a space and its corresponding kafka topic. See the [Sentinel documentation](https://sentinel-monitoring.readthedocs.io/en/latest/api.html#v1-api-space-post) on this.

Now you can create the syslog agent container instance. Using the [docker python library](https://github.com/docker/docker-py) it can be ran in the following way (on the command line it's rather the same).

```python
import docker
dockerclient = docker.DockerClient(base_url='unix://var/run/docker.sock')
dockerclient.containers.run(image=config.syslog_agent_sentinel_image, 
        labels={'creator': 'nexus'}, network='my_net', detach=True,
        environment=[
        "SENTINEL_SYSLOG_SPACE_NAME=A_SPACE",
        "SENTINEL_SYSLOG_TOPIC_NAME=A_TOPIC",
        "SENTINEL_AVAILABLE=False",
        "SENTINEL_API=http://localhost:9100",
        "SENTINEL_KAFKA_ENDPOINT=localhost:9092",
        "SENTINEL_SYSLOG_USERNAME=syslog_agent",
        "SENTINEL_SYSLOG_USER_API_KEY=XXX-YYY-ZZZ",
        "SENTINEL_SYSLOG_BIND_ADDR=0.0.0.0",
        "SENTINEL_SYSLOG_BIND_PORT=4243",
        ]
)
```

To see all configuration parameters (incl. defaults) see: [src/config.py](src/config.py).

Image is available on [docker hub](https://hub.docker.com/r/dizz/sentinel_syslog_agent/).