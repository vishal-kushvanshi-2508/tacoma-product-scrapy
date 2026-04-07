import scrapy
from datetime import datetime
import mysql.connector
import re
import json
import os
import gzip


class ProductInformationSpider(scrapy.Spider):
    name = "product_information"

    # allowed_domains = ["www.tacomascrew.com"]
    # start_urls = ["https://www.tacomascrew.com"]

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.tacomascrew.com",
        "Referer": "https://www.tacomascrew.com/"
    }


    def open_spider(self, spider):
        self.start_time = datetime.now()
        self.logger.info(f"Spider started at {self.start_time}")

    def close_spider(self, spider):
        end_time = datetime.now()
        duration = end_time - self.start_time
        self.logger.info(f"Spider finished at {end_time}")
        self.logger.info(f"Total runtime: {duration}")


    def handle_http_error(self, failure):
        request = failure.request
        self.logger.error(f"HTTP Error URL: {request.url}")
        self.logger.error(repr(failure))

    def update_product_detail_status(self, status,  product_detail_id):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="actowiz",
                database="tacoma_scrapy_db",
                port="3306"
            )

            cursor = connection.cursor()
            cursor.execute(
                "UPDATE product_detail SET status=%s WHERE id=%s",
                (status, product_detail_id,)
            )
            connection.commit()
            self.logger.info(f"Updated product_api_id={product_detail_id} → {status}")

        except mysql.connector.Error as e:
            self.logger.error(f" DB Update Error: {e}")
        cursor.close()
        connection.close()


    # Fetch all categories from DB
    def fetch_product_detail(self):
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="actowiz",
            database="tacoma_scrapy_db",
            port="3306"
        )
        print("------first------")

        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM product_detail WHERE status='pending'")
        rows = cursor.fetchall()
        cursor.close()
        connection.close()

        self.logger.info(f"Fetched {len(rows)} records from DB")     
        return rows


    def start_requests(self):
        print("------second------")

        rows = self.fetch_product_detail()  # Fetch all pending categories
        product_base_url = "https://www.tacomascrew.com"

        for row in rows:
            try:
                product_detail_id = row["id"]
                category_name = row["category_name"]
                sub_category_id = row["sub_category_id"]
                sub_category_name = row["sub_category_name"]
                product_id = row["product_id"]
                product_name = row["product_name"]
                product_url = row["product_url"]
                status = row["status"]

                start_base_api = r"https://www.tacomascrew.com/api/v1/products/"
                middle_base_api = r"?addToRecentlyViewed=true&applyPersonalization=true&categoryId="
                end_base_api = r"&expand=documents,specifications,styledproducts,htmlcontent,attributes,crosssells,pricing,relatedproducts,brand&getLastPurchase=true&includeAlternateInventory=true&includeAttributes=IncludeOnProduct,NotFromCategory&replaceProducts=false"

                product_info_api = start_base_api + product_id + middle_base_api + sub_category_id + end_base_api
                
                yield scrapy.Request(
                    url=product_info_api,
                    headers=self.headers,
                    callback=self.parse,
                    errback=self.handle_http_error,   #  ADD THIS
                    meta={
                        "handle_httpstatus_all": True,   #  IMPORTANT
                        "category_name": category_name,
                        "sub_category_id": sub_category_id,
                        "sub_category_name": sub_category_name,
                        "product_detail_id" : product_detail_id,
                        "product_id" : product_id,
                        "product_name" : product_name,
                        "product_base_url" : product_base_url,
                        "product_url" : product_url
                    }
                )

                ## here update all category
                self.update_product_detail_status("success", product_detail_id) 
                
            except Exception as e:
                self.logger.error(f"Start Request Error: {e}")
                print("9  success error")   
                self.update_product_detail_status("pending", product_detail_id)  

    
    def parse(self, response):

        product_detail_id = response.meta.get("product_detail_id")

        if response.status != 200:
            print("25 part 2  success error")  
            self.logger.error(f"Error BAD STATUS {response.status}: {response.url}")
            self.update_product_detail_status("pending", product_detail_id)
            return   #  stop processing
        
        data = response.json()
        product = data.get("product", {})
        product_id = response.meta["product_id"]

        # SAVE PRODUCT JSON
        folder = r"D:\vishal_kushvanshi\scrapy\tacoma\product_info_pages"
        os.makedirs(folder, exist_ok=True)

        with open(f"{folder}\\{product_id}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

        # description
        desc = product.get("htmlContent") or ""
        desc_list = [x.strip() for x in re.split(r"<br\s*/?>|•", desc) if x.strip()]

        # specifications
        att_data = []
        for att in product.get("attributeTypes", []):
            key = att.get("name")
            for val in att.get("attributeValues", []):
                att_data.append({
                    "key": key,
                    "value": val.get("value")
                })

        item = {
            "type" : "product_info",
            "name": response.meta["product_name"],
            "p_id": product.get("name"),
            "url": response.meta["product_url"],   # IMPORTANT FIX
            "img_url": product.get("largeImagePath"),
            "description": json.dumps(desc_list),
            "shipping_weight": product.get("shippingWeight"),
            "specification": json.dumps(att_data),
        }

        # ---------------- INVENTORY ----------------
        yield scrapy.Request(
            url="https://www.tacomascrew.com/api/v1/realtimeinventory",
            method="POST",
            headers=self.headers,
            body=json.dumps({"productIds": [product_id]}),
            callback=self.parse_inventory,
            meta={
                **response.meta,
                "item": item,
                "product_id": product_id
            }
        )

    # ---------------- INVENTORY ----------------
    def parse_inventory(self, response):
        data = response.json()
        product_id = response.meta["product_id"]

        #  SAVE INVENTORY JSON.GZ
        # D:\vishal_kushvanshi\scrapy\tacoma\product_info_pages
        folder = r"D:\vishal_kushvanshi\scrapy\tacoma\product_info_pages\inventory_pages"
        os.makedirs(folder, exist_ok=True)

        with gzip.open(f"{folder}\\{product_id}_inventory.json.gz", "wt", encoding="utf-8") as f:
            json.dump(data, f)

        inventory = response.json().get("realTimeInventoryResults", [{}])[0]
        available=inventory.get("inventoryAvailabilityDtos",[])[0]
        stock_qty = available.get("availability").get("message")

        # ---------------- PRICE ----------------
        yield scrapy.Request(
            url="https://www.tacomascrew.com/api/v1/realtimepricing",
            method="POST",
            headers=self.headers,
            body=json.dumps({
                "productPriceParameters": [{
                    "productId": product_id,
                    "unitOfMeasure": "EA",
                    "qtyOrdered": 1
                }]
            }),
            callback=self.parse_price,
            meta={
                **response.meta,
                "stock_qty": stock_qty
            }
        )

    # ---------------- PRICE ----------------
    def parse_price(self, response):
        data = response.json()
        product_id = response.meta["product_id"]

        #  SAVE PRICE JSON.GZ
        folder = r"D:\vishal_kushvanshi\scrapy\tacoma\product_info_pages\price_pages"
        os.makedirs(folder, exist_ok=True)

        with gzip.open(f"{folder}\\{product_id}_price.json.gz", "wt", encoding="utf-8") as f:
            json.dump(data, f)

        price = None
        price_value = None

        results = data.get("realTimePricingResults", [])
        if results:
            r = results[0]
            price = r.get("extendedActualPriceDisplay")
            price_value = r.get("extendedActualPrice")

        item = response.meta["item"]

        item.update({
            "price": price,
            "price_value": price_value,
            "stock_qty": response.meta["stock_qty"]
        })

        yield item









####------
# this is my first parse logic 
####------

    # def parse(self, response):


    #     category_name = response.meta.get("category_name")
    #     sub_category_name = response.meta.get("sub_category_name")
    #     product_detail_id = response.meta.get("product_detail_id")
    #     product_id = response.meta.get("product_id")
    #     product_name = response.meta.get("product_name")
    #     product_base_url = response.meta.get("product_base_url")
    #     product_url = response.meta.get("product_url")
    #     # print("parse method right category_name : ", category_name, sub_category_name, product_url)


    #     if response.status != 200:
    #         print("25 part 2  success error")  
    #         self.logger.error(f"Error BAD STATUS {response.status}: {response.url}")
    #         self.update_product_detail_status("pending", product_detail_id)
    #         return   #  stop processing
        
    #     try:
    #         #### get response and process it ...

    #         # og_url=response.meta.get('url')
    #         data = response.json()
    #         product = data.get("product", {})
    #         desc = product.get("htmlContent")
    #         desc_list = [ item.strip() for item in re.split(r"<br\s*/?>|•", desc) if item.strip()]
    #         id=product.get("name")
    #         img=product.get("largeImagePath")
    #         price=product.get("basicListPrice")
    #         weight=product.get("shippingWeight")
    #         stock=product.get("availability").get("message")

    #         #specifications
    #         att_data=[]
    #         for att in product.get("attributeTypes",[]):
    #             temp={}
    #             temp["key"]=att.get("name")
    #             for val in att.get("attributeValues",[]):
    #                     temp["value"]=val.get("value")
    #                     att_data.append(temp)
                    
            
    #         yield {
    #             "type": "product_info",
    #             "product_id":id,
    #             "product_name": product_name,
    #             "url":product_url,
    #             "img_url":img,
    #             "price":price,
    #             "description": json.dumps(desc_list),
    #             "shipping_weight":weight,
    #             "in_stock":stock,
    #             "specification":json.dumps(att_data)
    #         }
    #     except Exception as e:
    #         self.logger.error(f"6 parse Error: {e}")
    #         self.update_product_detail_status("pending", product_detail_id)
    #         return




