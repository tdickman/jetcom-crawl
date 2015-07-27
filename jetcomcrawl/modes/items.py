from bs4 import BeautifulSoup
import logging

from jetcomcrawl import browser
import jetcomcrawl.libs.queue


class Worker(object):
    def __init__(self):
        self.queue_categories = jetcomcrawl.libs.queue.Queue('queue_categories')
        self.queue_items = jetcomcrawl.libs.queue.Queue('queue_items')

    def _get_max_page(self, soup):
        pages = [int(a['href'].split('page=')[1]) for a in soup.find('div', {'class': 'pagination'}).findAll('a')]
        return max(pages)

    def work(self):
        '''Keeps running indefinitely, retrieving jobs from sqs'''
        while True:
            cid = self.queue_categories.retrieve()
            # TODO: Paginate here
            max_page = 1
            page = 1
            while page <= max_page:
                html = browser.get('https://jet.com/search/results?category=6000099&page=1'.format(cid, page))
                soup = BeautifulSoup(html, 'html.parser')
                max_page = self._get_max_page(soup)

                results = []
                for item in soup.find('div', {'class': 'products'}).findAll('div', {'class': 'product mobile'}):
                    url = item.a['href']
                    uid = url.split('/')[-1]
                    results.append({'uid': uid, 'url': url})

                logging.info('{} products found for category {}, page {}/{}, inserting into sqs'.format(len(results), cid, page, max_page))
                self.queue_items.insert_bulk(results)
                page += 1
