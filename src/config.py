import os


# shared
active_sentinel = bool(os.environ.get('SENTINEL_AVAILABLE', 'False'))
base_url = os.environ.get('SENTINEL_API', "http://localhost:9100")
syslog_agent_kafka_endpoint = os.environ.get('SENTINEL_KAFKA_ENDPOINT', 'localhost:9092')

username = os.environ.get('SENTINEL_SYSLOG_USERNAME', "auser")
syslog_agent_user_apikey = os.environ.get('SENTINEL_SYSLOG_USER_API_KEY', "akey")
space = os.environ.get('SENTINEL_SYSLOG_SPACE_NAME', "spacename")
topic_name = os.environ.get('SENTINEL_SYSLOG_TOPIC_NAME', "topicname")

# Syslog agent
syslog_agent_host = os.environ.get('SENTINEL_SYSLOG_BIND_ADDR', '0.0.0.0')
syslog_agent_port = int(os.environ.get('SENTINEL_SYSLOG_BIND_PORT', '4243'))

# Syslog internals
syslog_agent_key_serializer = os.environ.get('SENTINEL_KAFKA_KEY_SERIALIZER', 'StringSerializer')
syslog_agent_value_serializer = os.environ.get('SENTINEL_KAFKA_VALUE_SERIALIZER', 'StringSerializer')
syslog_agent_name = os.environ.get('SENTINEL_SYSLOG_AGENT', 'sentinel-internal-syslog-agent')


def print_env_vars():
    print('\nActive environment variables:\n ')
    for k, v in os.environ.items():
        print(k + '=' + v)
