from bs4 import BeautifulSoup
import logging

from jetcomcrawl import browser
import jetcomcrawl.libs.queue


class Worker(object):
    def __init__(self):
        self.queue = jetcomcrawl.libs.queue.Queue('queue_categories')

    def _get_max_page(self, cid):
        html = browser.get('https://jet.com/search/results?category={}&page={}'.format(cid, 1))
        soup = BeautifulSoup(html.text, 'html.parser')
        pages = [int(a['href'].split('page=')[1]) for a in soup.find('div', {'class': 'pagination'}).findAll('a')]
        return max(pages)

    def crawl(self):
        # Retrieve a list of categories to crawl, and throw these into sqs
        html = browser.get('https://jet.com/categories')
        soup = BeautifulSoup(html.text, 'html.parser')

        # Construct a set of unique category ids
        category_ids = set()
        for link in soup.find('div', {'class': 'level_one'}).findAll('a'):
            if link['href'] != '#' and 'category' in link['href']:
                category_id = link['href'].split('category=')[1].split('&')[0]
                category_ids.add(category_id)

        logging.info('Beginning inserting {} category ids * ?? pages into sqs'.format(len(category_ids)))

        for cid in category_ids:
            logging.info('Beginning inserting pages for category id {}'.format(cid))
            pages = [{'cid': cid, 'page': page} for page in range(1, self._get_max_page(cid))]
            self.queue.insert_bulk(list(pages))
            logging.info('Completed inserting {} pages for category id {}'.format(len(pages), cid))

        logging.info('Completed inserting {} category ids into sqs'.format(len(category_ids)))
