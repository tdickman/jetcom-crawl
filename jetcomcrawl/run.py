import sys
import logging

from jetcomcrawl.modes import categories, items, details


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) < 2:
        print('Please enter the mode you wish to run:\npython3 run.py [get_categories|get_items|get_details]')
        sys.exit()
    mode = sys.argv[1]
    if mode == 'get_categories':
        worker = categories.Worker()
        worker.crawl()
    elif mode == 'get_items':
        worker = items.Worker()
        worker.work()
    elif mode == 'get_details':
        worker = details.Worker()
        worker.work()
