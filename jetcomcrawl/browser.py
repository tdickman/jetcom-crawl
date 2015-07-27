import requests


USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36'


def get(url):
    headers = {'User-Agent': USER_AGENT}
    return requests.get(url, headers=headers).text
