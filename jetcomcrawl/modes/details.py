import logging
import json

from jetcomcrawl import browser
import jetcomcrawl.libs.queue


class Worker(object):
    def __init__(self):
        self.queue_items = jetcomcrawl.libs.queue.Queue('queue_items', batch_size=10, processing_timeout=60)

    def _get_max_page(self, soup):
        pages = [int(a['href'].split('page=')[1]) for a in soup.find('div', {'class': 'pagination'}).findAll('a')]
        return max(pages)

    def work(self):
        '''Keeps running indefinitely, retrieving jobs from sqs'''
        while True:
            product = self.queue_items.retrieve()
            session = browser.Session()
            resp = session.get('https://jet.com{}'.format(product['url']))
            csrf = resp.text.split('__csrf":"')[1].split('",')[0]
            resp = session.post('https://jet.com/api/product/price', json.dumps({'sku': product['uid']}), headers={
                'referer': product['url'],
                'content-type': 'application/json',
                'origin': 'https://jet.com',
                'x-csrf-token': csrf,
                'x-requested-with': 'XMLHttpRequest'
            })
            logging.info(resp.json())
            self.queue_items.remove_processed()
