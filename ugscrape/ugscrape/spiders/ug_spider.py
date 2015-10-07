'''
Scrapy spider to crawl 'ultimate-guitar.com' for guitar tab information
'''

import scrapy
import re

from ugscrape.items import UgscrapeItem

class ugSpider(scrapy.Spider):
    name = "ultimateguitar"
    allowed_domains = ["ultimate-guitar.com"]
    start_urls = ["http://www.ultimate-guitar.com"]

    '''Parse top level directory (pull out letter links)'''
    def parse(self, response):
        # for url in response.xpath("//a[@class='wb']/@href").extract()[15:17]:     # all bands
        #     yield scrapy.Request(url, callback=self.parse_band_dirs)
        url = response.xpath("//a[@class='wb']/@href").extract()[26]    # only z's ######
        yield scrapy.Request(url, callback=self.parse_band_dirs)

    '''Follow links to bands / artists from alphabetic band directory'''
    def parse_band_dirs(self, response):
        letter = response.url.split("/")[-1][0]
        for row in response.xpath("//tr"):
            try:
                numTabs = int(row.xpath("td/font/text()").extract()[0])
                band = row.xpath("td/a/text()").extract()[0][:-5]
            # Ignore bands not in the standard ultimate-guitar format
            except:
                continue
            # Only consider bands with over 100 tabs (of any type)
            if numTabs < 100:
                continue
            # Assuring that scraper only selects bands / links that should be on that page
            if letter == "0":
                if re.match('[0-9]',band[0]) is None:
                    continue
            else:
                if band[0].lower() != letter.lower():
                    continue
            href = row.xpath("td/a/@href").extract()
            url = response.urljoin(href[0])
            yield scrapy.Request(url, callback=self.parse_songs)

        # Jump to next page if it exists
        next_page = response.xpath("//a[@class='ys']")[-1]
        if next_page.xpath("text()").extract()[0][0:4] == "Next":
            url = response.urljoin(next_page.xpath("@href")[0].extract())
            yield scrapy.Request(url, self.parse_band_dirs)

    '''Follow links to tabs from band tab list'''
    def parse_songs(self, response):
        for row in response.xpath("//tr"):
            try:
                tabType = row.xpath("td/b/text()").extract()[0]
                song = row.xpath("td/a/text()").extract()[0][:-4]
            except:
                continue
            if tabType == "Tabs":   # Only pull out raw tabs (i.e. not TabPro, GuitarPro files etc)
                href = row.xpath("td/a/@href").extract()
                url = response.urljoin(href[0])
                yield scrapy.Request(url, callback=self.parse_tabs)

        # Jump to next page if it exists
        next_page = response.xpath("//a[@class='ys']")[-1]
        if next_page.xpath("text()").extract()[0][0:4] == "Next":
            url = response.urljoin(next_page.xpath("@href")[0].extract())
            yield scrapy.Request(url, self.parse_songs)

    '''Pull out details from tab pages in a general way'''
    def parse_tabs(self, response):
        item = UgscrapeItem()

        # Get artist, song and tab version information from the url
        url = response.url.split("/")
        item['artistName'] = url[-2].replace("_"," ").title()

        if "ver" in url[-1]:
            item['songName'] = url[-1].split('ver')[0][:-1].replace("_"," ").title()
            item['version'] = int(re.sub(r'[^0-9]',"",url[-1].split('ver')[-1]))
        else:
            item['songName'] = url[-1][:-8].replace("_"," ").title()
            item['version'] = 1

        # Tab views
        item['views'] = int(re.sub(r'[^0-9]','',response.xpath("//div[@class='stats']/text()")[1].extract()))

        tabText = response.xpath("//pre/text()")[-1].extract()     # take last <pre>, it contains the tab

        ## Find the tuning if it exists
        try:
            i = [f.strip().lower() for f in response.xpath("//div[@class='t_dt']/text()").extract()].index('tuning')
            item['tuning'] = response.xpath("//div[@class='t_dtde']/text()").extract()[i+1].strip()
        except:
            lower = tabText.lower()
            if "tuning" in lower:
                startPos = lower.find("tuning") + 6
                endPos = lower[startPos:].find("\n")
                item['tuning'] = re.sub(r'[^\w\s]','',lower[startPos:(startPos+endPos)]).strip()
            else:
                item['tuning'] = "eadgbe"
            
        tabText = re.sub(r'[hpbrv\|\(\)]','-',tabText)   # remove hammerons, pulloffs, slides, etc.
        item['tab'] = re.sub(r'[^0-9\-~\nx\/\\\\]','',tabText)  # only keep tab elements

        yield item