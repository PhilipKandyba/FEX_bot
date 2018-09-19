import config
import requests


def short_link(link):
    request = requests.get('{HOST}/j_link_create?url={long_link}'.format(HOST=config.HOST, long_link=link))

    request_result = request.json()

    new_link = '{HOST}/{tag}'.format(HOST=config.HOST, tag=request_result['tag'])

    return new_link


def new_object():
    request = requests.post('{HOST}/j_object_create'.format(HOST=config.HOST))

    response = request.json()

    object_id = response['token']

    object_url = '{HOST}/{object_id}'.format(HOST=config.HOST, object_id=object_id)

    return object_url
