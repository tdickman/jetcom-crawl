import boto.sqs
import logging

from jetcomcrawl.libs import common

BATCH_SIZE = 10


class Queue(object):
    def __init__(self, sqs_queue):
        settings = common.get_settings()
        conn = boto.sqs.connect_to_region(settings['region'])
        self.queue = conn.create_queue(settings[sqs_queue], 30)
        self.local_cache = []

    def insert(self, data):
        m = boto.sqs.message.Message()
        m.set_body(data)
        self.queue.write(m)

    def _reload_cache(self):
        logging.info('Reloading queue cache ({})'.format(BATCH_SIZE))
        assert len(self.local_cache) == 0
        self.local_cache = self.queue.get_messages(BATCH_SIZE)

    def retrieve(self):
        '''This should be called one at a time. This deletes the previous message upon retrieval'''
        if len(self.local_cache) > 0:
            self.queue.delete_message(self.local_cache.pop())
        if len(self.local_cache) == 0:
            self._reload_cache()
        return self.local_cache[-1].get_body()
