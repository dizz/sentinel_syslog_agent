import os
import json

import syslog_rcvr
import config

import requests


space_cache = []

admintoken = os.environ.get('SENTINEL_ADMIN_TOKEN', 'somevalue')
u_password = os.environ.get('SENTINEL_SYSLOG_PASSWORD', "apass")
test_payload = payload = {'procid': 1306, 'severity': 'info', 'appname': u'099b894232b7',
                          'timestamp': u'2018-08-09T12:39:03Z',
                          'hostname': u'linuxkit-025000000001',
                          'facility': 'daemon', 'version': 1,
                          'msgid': u'099b894232b7', 'msg': u'INFO:__main__:Press CTRL+C to quit.\r\n', 'sd': {}}


def create_user(base_url, admintoken, username, password):
    url = base_url + "/v1/api/"
    headers = {
        "Content-Type": "application/json",
        "x-auth-token": admintoken
    }

    # user
    data = {"login": username, "password": password}
    res = requests.post(url=url + "user/", headers=headers, data=json.dumps(data))
    res.raise_for_status()
    apikey = res.json()['apiKey']

    return username, password, apikey


def create_srv_inst_space(base_url, username, apikey, space=None):
    url = base_url + "/v1/api/"

    if not space:
        raise Exception('The name of the space to be created is missing')

    if space in space_cache:
        return space

    # space
    headers = {
        "Content-Type": "application/json",
        'x-auth-login': username,
        'x-auth-apikey': apikey
    }

    data = {"name": space}
    res = requests.post(url=url + "space/", headers=headers, data=json.dumps(data))
    res.raise_for_status()
    topic_name = res.json()['topicName']
    space_cache.append(space)
    return space, topic_name
#


# do the ESM setup
def do_esm():
    # ESM: create user as specified to ESM
    username, password, apikey = create_user(
        base_url=config.base_url,
        admintoken=admintoken,
        username=config.username,
        password=u_password
    )
    print(username, password, apikey)

    # ESM: create space per service instance
    space, topic_name = create_srv_inst_space(
        base_url=config.base_url,
        username=config.username,
        apikey=apikey,
        space=config.space
    )
    return apikey, space, topic_name


def do_agent(apikey, space, topic_name):
    # Agent: create a series within the ESM supplied space
    series_name = syslog_rcvr.create_container_series(
        base_url=config.base_url,
        username=config.username,
        user_apikey=apikey,
        space_name=space,
        series_name=test_payload['appname']  # get container ID as series name
    )
    print(series_name)

    # Agent: send the log message on to Sentinel's kafka endpoint
    syslog_rcvr.send_msg(test_payload, topic_name, series_name)


if __name__ == "__main__":
    # create user and service instance space
    apikey, space, topic_name = do_esm()
    print(apikey, space, topic_name)
    # create container series and issue test message
    do_agent(apikey, space, topic_name)
