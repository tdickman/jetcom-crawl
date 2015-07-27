# What is this?

A script for crawling jet.com for a list of all products, and storing them in a redis database.

# How does it work?

Crawling involves a two step process. First the master node is run, and inserts urls to be crawled into sqs. These are then crawled by the worker node(s), and results are placed in a redis database for serving up to clients.

# Setup

Inject the following environment variables into the running container:
* AWS_ACCESS_KEY_ID
* AWS_SECRET_ACCESS_KEY

# How do I use it?

1. Follow the setup steps from above, and then run the tool using all three of the following modes: ```python3 run.py [get_categories|get_items|get_details]```
2. get_categories retrieves a list of categories to crawl against, and places them in sqs.
3. get_items retrieves a list of items to crawl.
4. get_details retrieves the price details for each item.
