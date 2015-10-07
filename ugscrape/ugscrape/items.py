# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UgscrapeItem(scrapy.Item):
	artistName = scrapy.Field()
	songName = scrapy.Field()
	version = scrapy.Field()
	tuning = scrapy.Field()
	views = scrapy.Field()
	tab = scrapy.Field()