import requests
import time
import random


USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36'
DELAY = 5


def get(url):
    delay()
    headers = {'user-agent': USER_AGENT}
    return requests.get(url, headers=headers)


def delay():
    time.sleep(random.uniform(0, 5))


class Session(object):
    def __init__(self):
        self.s = requests.Session()
        self.s.headers.update({'user-agent': USER_AGENT})

    def get(self, url):
        delay()
        return self.s.get(url)

    def post(self, url, post_data, headers={}):
        delay()
        return self.s.post(url, data=post_data, headers=headers)
