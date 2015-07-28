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
        while True:
            # TODO: Handle no items left in queue
            data = self.queue_categories.retrieve()
            cid = data['cid']
            page = data['page']
            logging.info('Finding products for category {}, page {}'.format(cid, page))
            html = browser.get('https://jet.com/search/results?category={}&page={}'.format(cid, page))
            try:
                soup = BeautifulSoup(html.text, 'html.parser')

                if soup.find('div', {'class': 'no_results'}):
                    logging.info('Skipping process of {}:{}. No results available'.format(cid, page))
                else:
                    results = []
                    for item in soup.find('div', {'class': 'products'}).findAll('div', {'class': 'product mobile'}):
                        url = item.a['href']
                        uid = url.split('/')[-1]
                        results.append({'uid': uid, 'url': url})
            except:
                logging.info(html.text)
                raise

            logging.info('{} products found for category {}, page {}, inserting into sqs'.format(len(results), cid, page))
            self.queue_items.insert_bulk(results)

            self.queue_categories.remove_processed()
