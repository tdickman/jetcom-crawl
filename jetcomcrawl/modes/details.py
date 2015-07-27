import logging
import json
import datetime
import decimal

from jetcomcrawl import browser
import jetcomcrawl.libs.queue
import jetcomcrawl.libs.dynamodb


class Worker(object):
    def __init__(self):
        self.queue_items = jetcomcrawl.libs.queue.Queue('queue_items', batch_size=10, processing_timeout=5*60)
        self.table = jetcomcrawl.libs.dynamodb.Table()

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
        data['price_competitor'] = data['quantities'][0]['price']
        data['price_savings'] = data['quantities'][0]['savings']
        data['price'] = data['price_competitor'] - data['price_savings']
        data['jid'] = jid
        return data

    def work(self):
        '''Keeps running indefinitely, retrieving jobs from sqs'''
        while True:
            product = self.queue_items.retrieve()
            session = browser.Session()
            logging.info('Beginning to retrieve data for {}:{}'.format(product['uid'], product['url']))
            resp = session.get('https://jet.com{}'.format(product['url']))
            csrf = resp.text.split('__csrf":"')[1].split('",')[0]
            resp = session.post('https://jet.com/api/product/price', json.dumps({'sku': product['uid']}), headers={
                'referer': product['url'],
                'content-type': 'application/json',
                'origin': 'https://jet.com',
                'x-csrf-token': csrf,
                'x-requested-with': 'XMLHttpRequest'
            })
            data = self._process_data(product['uid'], resp.json())
            logging.info(data)
            self.table.insert(data)
            self.queue_items.remove_processed()
