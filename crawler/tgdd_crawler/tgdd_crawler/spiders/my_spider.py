import scrapy
import logging
from scrapy.http import XmlResponse
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import os
from scrapy.signals import spider_closed
from scrapy.signalmanager import dispatcher
from tgdd_crawler.spiders.convert_text import convert_text
cnt = 0
categories = []
class MySpider(scrapy.Spider):
    name = 'my_spider'
    allowed_domains = ['thegioididong.com']
    def __init__(self, daily=None, *args, **kwargs):
        logging.info(f"envihihi: {os.environ}")
        super(MySpider, self).__init__(*args, **kwargs)
        self.start_urls = ['https://www.thegioididong.com/newsitemap/sitemap-product']
        self.ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        self.data_buffer = []
        self.chunk_size = 100
        self.chunk_index = 0
        self.daily = daily
        if self.daily and os.path.exists('metadata.json'):
            with open('metadata.json', 'r') as f:
                metadata = json.load(f)
                self.last_mod = metadata.get('last_mod', None)
        else:
            self.last_mod = None
        dispatcher.connect(self.spider_closed_handler, signal=spider_closed)

    def parse(self, response):
        body = response.body if isinstance(response, XmlResponse) else None
        if body:
            root = ET.fromstring(body)
            loc_elements = root.findall('.//ns:sitemap/ns:loc', self.ns)
            for url in loc_elements:
                yield scrapy.Request(url.text, callback=self.parse_list_product)

    def parse_list_product(self, response):
        global cnt, categories
        body = response.body if isinstance(response, XmlResponse) else None
        if body:
            root = ET.fromstring(body)
            loc_elements = root.findall('.//ns:url', self.ns)
            for url in loc_elements:
                url_text = url.find('.//ns:loc', self.ns).text
                lastmod = url.find('.//ns:lastmod', self.ns).text
                if self.last_mod is None or self.last_mod and datetime.strptime(lastmod, "%Y-%m-%d") > datetime.strptime(self.last_mod, "%Y-%m-%d"):
                    yield scrapy.Request(url_text, callback=self.parse_detail_product, meta = {'lastmod': lastmod})

    def parse_detail_product(self, response):
        global cnt
        logging.info(f"URL: {response.url}")
        lastmod = response.meta.get('lastmod', None)
        data = {}
        data['url'] = response.url
        data['updated_at'] = lastmod
        data['crawled_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        url_parts = response.url.replace('https://www.thegioididong.com/', '').split('/')
        data['category'], data['product_id'] = url_parts[0], url_parts[1]
        productld = json.loads(response.xpath('//*[@id="productld"]/text()').get())
        data['product_name'] = productld.get('name', None)
        data['price_origin'] = response.xpath('//*[@id="PriceOriginGTM"]/@value').get()
        data['price_present'] = response.xpath('//*[@id="DisPriceGTM"]/@value').get()
        data['price'] = productld.get('offers', {}).get('price', None)
        data['image'] = productld.get('image', None)
        data['description'] = productld.get('description', None)
        data['brand'] = productld.get('brand', {}).get('name', [])
        data['review'] = productld.get('review', None)
        data['price_valid_ultil'] = productld.get('offers', {}).get('priceValidUntil', None)
        specification_boxes = response.xpath('//div[@class="box-specifi"]')
        # Get product specification
        for box_specifi in specification_boxes:
            text_specifi = box_specifi.xpath('.//ul/li')
            name_specifi = box_specifi.xpath('.//a/h3/text()').get() or 'Thông số kỹ thuật'
            spec_dict = {}
            for spec_feature in text_specifi:
                key = spec_feature.xpath('.//aside/strong/text() | .//a/text()').get() 
                value = spec_feature.xpath('.//aside/span/text() | .//a/text()').get() 
                if key:
                    key = key.strip(':').strip()
                if value:
                    value = value.strip('.').strip() 
                if key and value:
                    spec_dict[convert_text(key)] = value
                else:
                    logging.info(f"Missing data for feature: key={key}, value={value}")
            
            data[convert_text(name_specifi)] = spec_dict
        self.data_buffer.append(data)
        cnt += 1
        logging.info(f"cnt: {cnt}")

        if len(self.data_buffer) >= self.chunk_size:
            save_data(self.data_buffer, self.chunk_index)
            self.data_buffer.clear()
            self.chunk_index += 1

    def spider_closed_handler(self, spider, reason):
        logging.info(f"Spider closed: {reason}")
        save_data(self.data_buffer, self.chunk_index)
        metadata = {"last_mod": datetime.now().strftime('%Y-%m-%d')}
        with open('metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)

def save_data(data, chunk_index):
    today = datetime.now().strftime('%Y%m%d')
    output_dir = os.path.join('../../warehouse', 'daily', 'tgdd', today)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    file_name = f"{chunk_index}.json"
    file_path = os.path.join(output_dir, file_name)
    with open(file_path, 'a', encoding='utf-8') as json_file:
        for record in data:
            json.dump(record, json_file, ensure_ascii=False)
            json_file.write('\n')