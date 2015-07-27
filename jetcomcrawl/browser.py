import requests
import time
import random
from retrying import retry

from jetcomcrawl.libs import common


USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36'
DELAY = common.get_settings()['request_delay']


@retry(stop_max_attempt_number=5, wait_exponential_multiplier=2000, wait_exponential_max=20000)
def get(url):
    delay()
    headers = {'user-agent': USER_AGENT}
    resp = requests.get(url, headers=headers, timeout=30)
    assert resp.status_code == 200
    return resp


def delay():
    time.sleep(random.uniform(0, DELAY))


class Session(object):
    def __init__(self):
        self.s = requests.Session()
        self.s.headers.update({'user-agent': USER_AGENT})

    @retry(stop_max_attempt_number=5, wait_exponential_multiplier=2000, wait_exponential_max=20000)
    def get(self, url):
        delay()
        resp = self.s.get(url, timeout=30)
        assert resp.status_code == 200
        return resp

    @retry(stop_max_attempt_number=5, wait_exponential_multiplier=2000, wait_exponential_max=20000)
    def post(self, url, post_data, headers={}):
        delay()
        resp = self.s.post(url, data=post_data, headers=headers, timeout=30)
        assert resp.status_code == 200
        return resp
