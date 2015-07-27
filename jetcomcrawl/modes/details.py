import logging
import json
import datetime
import decimal
from retrying import retry
import boto.dynamodb2.exceptions

from jetcomcrawl import browser
import jetcomcrawl.libs.queue
import jetcomcrawl.libs.dynamodb


CSRF_REFRESH_INTERVAL = 10


class Worker(object):
    def __init__(self):
        self.queue_items = jetcomcrawl.libs.queue.Queue('queue_items', batch_size=10)
        self.table = jetcomcrawl.libs.dynamodb.Table()
        self.csrf_count = 0

    def _get_max_page(self, soup):
        pages = [int(a['href'].split('page=')[1]) for a in soup.find('div', {'class': 'pagination'}).findAll('a')]
        return max(pages)

    def _process_data(self, jid, data):
        '''Parse out the asin (if it exists). TODO: Clean this up'''
        asins = list(filter(lambda x: x['source'] == 'Amazon', data['comparisons']))
        data['asin'] = None
        if len(asins) > 0:
            data['asin'] = asins[0]['url'].split('/')[-1]
        data['timestamp'] = str(datetime.datetime.utcnow())
        # Covert floats to strings. TODO: Clean this up, and generalize it
        for item in data['quantities']:
            item['price'] = round(decimal.Decimal(item['price']), 2)
            item['savings'] = round(decimal.Decimal(item['savings']), 2)
        for item in data['comparisons']:
            item['price'] = round(decimal.Decimal(item['price']), 2)
        if not data['unavailable']:
            data['price_competitor'] = data['quantities'][0]['price']
            data['price_savings'] = data['quantities'][0]['savings']
            data['price'] = data['price_competitor'] - data['price_savings']
        data['jid'] = jid
        return data

    def _get_csrf(self, url):
        if self.csrf_count < 1:
            self.session = browser.Session()
            resp = self.session.get('https://jet.com{}'.format(url))
            self.csrf = resp.text.split('__csrf":"')[1].split('",')[0]
            self.csrf_count = CSRF_REFRESH_INTERVAL - 1
            logging.info('Retrieving new csrf token')
        self.csrf_count -= 1
        return (self.session, self.csrf)

    @retry(stop_max_attempt_number=5, wait_exponential_multiplier=2000, wait_exponential_max=20000)
    def _get_everything(self, product):
        try:
            (session, csrf) = self._get_csrf(product['url'])
            resp = session.post('https://jet.com/api/product/price', json.dumps({'sku': product['uid']}), headers={
                'referer': product['url'],
                'content-type': 'application/json',
                'origin': 'https://jet.com',
                'x-csrf-token': csrf,
                'x-requested-with': 'XMLHttpRequest'
            })
        except:
            self.csrf_count = 0
            raise
        return resp

    def work(self):
        '''Keeps running indefinitely, retrieving jobs from sqs'''
        while True:
            product = self.queue_items.retrieve()
            try:
                logging.info('Procesing {}'.format(product['uid']))
                if self.table.get_item(jid=product['uid']):
                    logging.info('{} already exists, skipping'.format(product['uid']))
                else:
                    raise boto.dynamodb2.exceptions.ItemNotFound('nope')
            except boto.dynamodb2.exceptions.ItemNotFound:
                logging.info('Beginning to retrieve data for {}:{}'.format(product['uid'], product['url']))
                resp = self._get_everything(product)
                logging.info(resp.text)
                data = self._process_data(product['uid'], resp.json())
                logging.info(data)
                self.table.insert(data)
            self.queue_items.remove_processed()
