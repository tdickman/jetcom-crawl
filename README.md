# What is this?

A script for crawling jet.com for a list of all products, and storing them in a redis database.

# How does it work?

Crawling involves a two step process. First the master node is run, and inserts urls to be crawled into sqs. These are then crawled by the worker node(s), and results are placed in a redis database for serving up to clients.
