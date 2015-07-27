from bs4 import BeautifulSoup
import logging

from jetcomcrawl import browser
import jetcomcrawl.libs.queue


class Worker(object):
    def __init__(self):
        self.queue = jetcomcrawl.libs.queue.Queue('queue_categories')

    def crawl(self):
        # Retrieve a list of categories to crawl, and throw these into sqs
        page = browser.get('https://jet.com/categories')
        soup = BeautifulSoup(page, 'html.parser')

        # Construct a set of unique category ids
        category_ids = set()
        for link in soup.find('div', {'class': 'level_one'}).findAll('a'):
            if link['href'] != '#' and 'category' in link['href']:
                category_id = link['href'].split('category=')[1].split('&')[0]
                category_ids.add(category_id)

        logging.info('Beginning inserting {} category ids into sqs'.format(len(category_ids)))

        for category_id in category_ids:
            self.queue.insert(category_id)

        logging.info('Completed inserting {} category ids into sqs'.format(len(category_ids)))
