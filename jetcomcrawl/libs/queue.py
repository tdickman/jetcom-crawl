import boto.sqs
import logging
import json

from jetcomcrawl.libs import common


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


class Queue(object):
    def __init__(self, sqs_queue, batch_size=1, processing_timeout=30):
        self.batch_size = batch_size
        settings = common.get_settings()
        conn = boto.sqs.connect_to_region(settings['region'])
        self.queue = conn.create_queue(settings[sqs_queue], 30)
        self.queue.set_message_class(boto.sqs.message.RawMessage)
        self.local_cache = []

    def insert(self, data):
        m = boto.sqs.message.Message()
        m.set_body(data)
        self.queue.write(m)

    def insert_bulk(self, items):
        for sub_items in chunker(items, 10):
            messages = []
            for i, item in enumerate(sub_items):
                messages.append((i, json.dumps(item), 0))

            self.queue.write_batch(messages)

    def _reload_cache(self):
        logging.info('Reloading queue cache ({})'.format(self.batch_size))
        assert len(self.local_cache) == 0
        self.local_cache = self.queue.get_messages(self.batch_size)

    def retrieve(self):
        '''This should be called one at a time. This deletes the previous message upon retrieval'''
        if len(self.local_cache) == 0:
            self._reload_cache()
        return json.loads(self.local_cache[-1].get_body())

    def remove_processed(self):
        if len(self.local_cache) > 0:
            self.queue.delete_message(self.local_cache.pop())
