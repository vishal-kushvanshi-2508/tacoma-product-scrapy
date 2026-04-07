# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TacomaProductScrapeItem(scrapy.Item):
    # define the fields for your item here like:
    type = scrapy.Field()
    p_id = scrapy.Field()
    name = scrapy.Field()
    
    url = scrapy.Field()
    
    img_url = scrapy.Field()
    price = scrapy.Field()
    price_value = scrapy.Field()
    description = scrapy.Field()
    product_url = scrapy.Field()
 
    shipping_weight = scrapy.Field()
    
    
    stock_qty = scrapy.Field()
    specification = scrapy.Field()

    status = scrapy.Field()
