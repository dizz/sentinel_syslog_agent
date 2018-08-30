import json
import requests
import signal
from socket import AF_INET, SOCK_DGRAM, socket
from time import sleep

from kafka import KafkaProducer
from syslog_rfc5424_parser import SyslogMessage, ParseError

import config

# this agent consumes syslog messages (RFC5424 compliant only) and forwards them to EMP/Sentinel
# it sends them to a series specified by the container ID and grouped under the tenant space
# per docker deployment it requires the following docker log options set:
#   --log-opt syslog-address=udp://$SENTINEL_SYSLOG_BIND_ADDR:$SENTINEL_SYSLOG_BIND_PORT
#   --log-opt syslog-format=rfc5424
#
# all these options can be set in a docker-compose file. The ESM is responsible to inject these
# options into every service instance and also provision the syslog agent along side of the
# deployed service


series_cache = []


def create_container_series(base_url, username, user_apikey, space_name, series_name):
    # should create a new series based on the container ID
    # should cache created series to avoid call to sentinel
    # series

    # for testing, if space_name does not existing we should create it

    if not series_name:
        raise Exception('The name of the series to be created is missing')

    if series_name in series_cache:
        return series_name

    url = base_url + "/v1/api/"

    headers = {
        "Content-Type": "application/json",
        'x-auth-login': username,
        "x-auth-apikey": user_apikey,

    }

    data = {"name": series_name, "spaceName": space_name, "msgSignature": 'unixtime:s msgtype:json'}  # default msgSignature
    res = requests.post(url=url + "series/", headers=headers, data=json.dumps(data))
    res.raise_for_status()
    series_cache.append(series_name)
    return series_name


def send_msg(payload: dict, space=None, series=None):
    if space is None and series is None:
        raise Exception('No sentinel space or series supplied.')

    # no auth required
    msg_dict = dict()
    msg_dict["agent"] = config.syslog_agent_name
    msg_dict['msg'] = payload

    print('sending to {kep}: {msg}'.format(kep=config.syslog_agent_kafka_endpoint,msg=msg_dict))

    if config.syslog_agent_key_serializer == "StringSerializer" and config.syslog_agent_value_serializer == "StringSerializer":
        kafka_producer = KafkaProducer(linger_ms=1, acks='all', retries=0, key_serializer=str.encode,
                             value_serializer=str.encode, bootstrap_servers=[config.syslog_agent_kafka_endpoint])
    else:
        raise Exception('Incompatible key_serializer and value_serializer combination')

    kafka_producer.send(space, key=series, value=json.dumps(msg_dict))

    # time required for kafka to get the value
    sleep(0.05)
    kafka_producer.close()


def shutdown_handler(signum=None, frame=None):
    print('Shutting down the UDP Sentinel log forwarder...')
    UDPSock.close()


# this could be done by a serverless app - efficient?
if __name__ == "__main__":
    print('Starting the UDP Sentinel log forwarder...')
    config.print_env_vars()

    # setup shutdown handlers
    for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT]:
        signal.signal(sig, shutdown_handler)

    UDPSock = socket(AF_INET, SOCK_DGRAM)
    UDPSock.bind((config.syslog_agent_host, config.syslog_agent_port))

    # Receive messages - processing this could be a bottleneck - place into thread if so
    while True:
        # if a log message gets truncated that's ok so long as the core syslog info is presented
        data, addr = UDPSock.recvfrom(4096)
        message = None
        try:
            message = SyslogMessage.parse(data.decode('utf-8'))
        except ParseError as e:
            print(e)
        message = message.as_dict()
        print(message)
        if config.active_sentinel:
            # appname in msg is the short container id
            series_name = create_container_series(base_url=config.base_url,
                                                  username=config.username,
                                                  user_apikey=config.syslog_agent_user_apikey,
                                                  space_name=config.space,
                                                  series_name=message['appname'])

            send_msg(json.dumps(message), space=config.topic_name, series=series_name)
