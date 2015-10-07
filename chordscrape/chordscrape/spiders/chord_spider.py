'''
Scrapy spider to crawl 'scales-chords.com' for chord and transcription information to match to tabs
'''

import scrapy
import re

from chordscrape.items import ChordscrapeItem

class chordSpider(scrapy.Spider):
    name = "chords"
    allowed_domains = ["scales-chords.com"]
    keys = ["A","A%23","B","C","C%23","D","D%23","E","F","F%23","G","G%23"]
    start_urls = ["http://www.scales-chords.com/showchbykey.php?key=" + k for k in keys]

    def parse(self, response):
        # Select each page of results
        pages2 = response.xpath("//span/a/@href").extract()
        pages = pages2[0:len(pages2)/2] # as there are two sets of links on each page
        for page in pages:
            url = response.urljoin(page)
            yield scrapy.Request(url, self.parse_notes)

    def parse_notes(self, response):
        for row in response.xpath("//table/tbody/tr/td/b/a"):
            href = row.xpath("@href").extract()
            url = response.urljoin(href[0])
            yield scrapy.Request(url, callback=self.parse_chords)

    def parse_chords(self, response):
        item = ChordscrapeItem() 

        item['chordName'] = response.xpath("//table[@class = 'chordtable']/tbody/tr/td/b/text()").extract()[0]
        transcriptions = response.xpath("//text()[.='Simplified notation:']/following::text()[position()=1]").extract()
        difficulties = response.xpath("//text()[.='Difficulty level:']/following::text()[position()=1]").extract()
        for trans, diff in zip(transcriptions, difficulties):
            item['transcription'] = trans
            item['difficulty'] = diff
            yield item