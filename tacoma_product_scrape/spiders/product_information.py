import scrapy
from datetime import datetime
import mysql.connector
import re
import json

class ProductInformationSpider(scrapy.Spider):
    name = "product_information"

    # allowed_domains = ["www.tacomascrew.com"]
    # start_urls = ["https://www.tacomascrew.com"]


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
        # category_name = request.meta.get("category_name")

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

                # print("category_name : ", category_name, sub_category_name , api_url, status)

                # here is changes ..
                # if category_name != "Abrasives" :
                #     continue

                # if sub_category_name != "Sheets":

                
                # # # if sub_category_name != "Cut-off-Wheels/Metal-and-Stainless-Steel":
                #     continue

                start_base_api = r"https://www.tacomascrew.com/api/v1/products/"
                middle_base_api = r"?addToRecentlyViewed=true&applyPersonalization=true&categoryId="
                end_base_api = r"&expand=documents,specifications,styledproducts,htmlcontent,attributes,crosssells,pricing,relatedproducts,brand&getLastPurchase=true&includeAlternateInventory=true&includeAttributes=IncludeOnProduct,NotFromCategory&replaceProducts=false"

                product_info_api = start_base_api + product_id + middle_base_api + sub_category_id + end_base_api
                
                # print("right category_name : ",product_id, category_name, sub_category_name,sub_category_id, product_url , status)
                # print("3 right category_name : ", product_info_api)

                yield scrapy.Request(
                    url=product_info_api,
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

                # print("7  success error")     

                ## here update all category
                self.update_product_detail_status("success", product_detail_id) 
                # break
                # print("8  success error")     
                
            except Exception as e:
                self.logger.error(f"Start Request Error: {e}")
                print("9  success error")   
                self.update_product_detail_status("pending", product_detail_id)  


    def parse(self, response):


        category_name = response.meta.get("category_name")
        sub_category_name = response.meta.get("sub_category_name")
        product_detail_id = response.meta.get("product_detail_id")
        product_id = response.meta.get("product_id")
        product_name = response.meta.get("product_name")
        product_base_url = response.meta.get("product_base_url")
        product_url = response.meta.get("product_url")
        # print("parse method right category_name : ", category_name, sub_category_name, product_url)


        if response.status != 200:
            print("25 part 2  success error")  
            self.logger.error(f"Error BAD STATUS {response.status}: {response.url}")
            self.update_product_detail_status("pending", product_detail_id)
            return   #  stop processing
        
        try:
            #### get response and process it ...

            # og_url=response.meta.get('url')
            data = response.json()
            product = data.get("product", {})
            desc = product.get("htmlContent")
            desc_list = [ item.strip() for item in re.split(r"<br\s*/?>|•", desc) if item.strip()]
            id=product.get("name")
            img=product.get("largeImagePath")
            price=product.get("basicListPrice")
            weight=product.get("shippingWeight")
            stock=product.get("availability").get("message")

            #specifications
            att_data=[]
            for att in product.get("attributeTypes",[]):
                temp={}
                temp["key"]=att.get("name")
                for val in att.get("attributeValues",[]):
                        temp["value"]=val.get("value")
                        att_data.append(temp)
                    
            
            yield {
                "type": "product_info",
                "product_id":id,
                "product_name": product_name,
                "url":product_url,
                "img_url":img,
                "price":price,
                "description": json.dumps(desc_list),
                "shipping_weight":weight,
                "in_stock":stock,
                "specification":json.dumps(att_data)
            }
        except Exception as e:
            self.logger.error(f"6 parse Error: {e}")
            self.update_product_detail_status("pending", product_detail_id)
            return



## here cheking api now 
## product detail in id = 28  sub_category_id = a87b152d-ba7c-4f1c-a05e-abfa01123a28 product_id = f94bb57a-217f-4920-8d59-ab9101529617

# https://www.tacomascrew.com/api/v1/products/f94bb57a-217f-4920-8d59-ab9101529617?addToRecentlyViewed=true&applyPersonalization=true&categoryId=a87b152d-ba7c-4f1c-a05e-abfa01123a28  &expand=documents,specifications,styledproducts,htmlcontent,attributes,crosssells,pricing,relatedproducts,brand&getLastPurchase=true&includeAlternateInventory=true&includeAttributes=IncludeOnProduct,NotFromCategory&replaceProducts=false