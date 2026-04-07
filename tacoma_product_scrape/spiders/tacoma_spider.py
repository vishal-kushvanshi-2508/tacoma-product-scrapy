import scrapy
import re



class TacomaSpiderSpider(scrapy.Spider):
    name = "tacoma_spider"
    allowed_domains = ["www.tacomascrew.com"]
    start_urls = ["https://www.tacomascrew.com/all-categories"]

    def parse(self, response):
        print("------first------")

        all_category = response.xpath("//div[@class='category-card x:px-lg x:mb-xxl']")

        base_url = response.url.strip("/").rsplit("/", 1)[0]
        
        for category_data in all_category:
            category_name = category_data.xpath(".//a//p/text()").get().strip()
            
            if not category_name:
                continue
            
            category_name_lower = category_name.lower().replace(" / ", "-").replace(" ","-")  #.replace("/","")
            clean_category_name =  re.sub(r"-{2,}", '', category_name_lower)
            category__url = base_url + "/Catalog/" + clean_category_name

            #  Save into DB
            yield {
                "type": "category",
                "category_name": category_name.replace(" / ", "-").replace(" ","-").replace("--", ""),
                "url": category__url
            }


