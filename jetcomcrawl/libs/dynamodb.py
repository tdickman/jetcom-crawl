import boto.dynamodb2
import boto.dynamodb2.table

from jetcomcrawl.libs import common


class Table(object):
    def __init__(self):
        settings = common.get_settings()
        conn = boto.dynamodb2.connect_to_region('us-west-2')
        self.table = boto.dynamodb2.table.Table(settings['dynamodb_table'], connection=conn)

    def insert(self, data):
        '''TODO: Batch these requests'''
        self.table.put_item(data=data, overwrite=True)

    def get_item(self, **kwargs):
        return self.table.get_item(**kwargs)
