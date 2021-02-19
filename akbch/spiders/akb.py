import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from akbch.items import Article


class AkbSpider(scrapy.Spider):
    name = 'akb'
    start_urls = ['https://www.akb.ch/die-akb/kommunikation-medien/news']

    def parse(self, response):
        links = response.xpath('//div[@class="news-list-link"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//ul[@class="lfr-pagination-buttons pager"]/li[last()]/a/@href').get()
        if next_page and 'https' in next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//span[@itemprop="datePublished"]/@content').get()
        if date:
            date = datetime.strptime(date.strip(), '%Y-%m-%dT00:00:00.000+%H:00')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@class="details-page-webcontent html-content"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
