from bs4 import BeautifulSoup
import logging

from jetcomcrawl import browser
import jetcomcrawl.libs.queue


class Worker(object):
    def __init__(self):
        self.queue_categories = jetcomcrawl.libs.queue.Queue('queue_categories')
        self.queue_items = jetcomcrawl.libs.queue.Queue('queue_items')

    def work(self):
        '''Keeps running indefinitely, retrieving jobs from sqs'''
        for x in range(40):
            self.queue_categories.retrieve()
