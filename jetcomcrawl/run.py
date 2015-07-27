import sys
import modes.categories
import logging


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) < 2:
        print('Please enter the mode you wish to run:\npython3 crawler.py [master|worker]')
        sys.exit()
    mode = sys.argv[1]
    if mode == 'get_categories':
        # Run master
        worker = modes.categories.Worker()
        worker.crawl()
    elif mode == 'get_items':
        # Run worker
        pass
    elif mode == 'get_details':
        pass
