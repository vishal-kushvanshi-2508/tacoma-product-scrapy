import scrapy
import mysql.connector
from datetime import datetime
from tacoma_product_scrape.items import TacomaProductScrapeItem

class ProductUrlFromApiSpider(scrapy.Spider):
    name = "product_url_from_api"

    # allowed_domains = ["www.tacomascrew.com"]
    # start_urls = ["https://www.tacomascrew.com"]


    # =========================
    # SPIDER START / END LOG
    # =========================
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
        category_name = request.meta.get("category_name")

        self.logger.error(f"HTTP Error URL: {request.url}")
        self.logger.error(repr(failure))

    def update_product_api_status(self, status,  product_api_id):
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
                "UPDATE product_api SET status=%s WHERE id=%s",
                (status, product_api_id,)
            )
            connection.commit()
            self.logger.info(f"Updated product_api_id={product_api_id} → {status}")

        except mysql.connector.Error as e:
            self.logger.error(f" DB Update Error: {e}")
        cursor.close()
        connection.close()




    # Fetch all categories from DB
    def fetch_product_api(self):
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="actowiz",
            database="tacoma_scrapy_db",
            port="3306"
        )
        print("------first------")

        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM product_api WHERE status='pending'")
        rows = cursor.fetchall()
        cursor.close()
        connection.close()

        self.logger.info(f"Fetched {len(rows)} records from DB")
        
        return rows


    def start_requests(self):
        print("------second------")

        rows = self.fetch_product_api()  # Fetch all pending categories
        product_base_url = "https://www.tacomascrew.com"

        for row in rows:
            try:

                product_api_id = row["id"]
                category_name = row["category_name"]
                sub_category_id = row["sub_category_id"]
                sub_category_name = row["sub_category_name"]
                api_url = row["api_url"]
                status = row["status"]

                # print("category_name : ", category_name, sub_category_name , api_url, status)

                # here is changes ..
                # if category_name != "Abrasives" :
                #     continue

                # if sub_category_name != "Sheets":

                
                # # if sub_category_name != "Cut-off-Wheels/Metal-and-Stainless-Steel":
                #     continue


                print("right category_name : ", category_name, sub_category_name , api_url, status)
                yield scrapy.Request(
                    url=api_url,
                    callback=self.parse,
                    errback=self.handle_http_error,   #  ADD THIS
                    meta={
                        "handle_httpstatus_all": True,   #  IMPORTANT
                        "category_name": category_name,
                        "sub_category_id" : sub_category_id,
                        "sub_category_name": sub_category_name,
                        "api_url": api_url,
                        "product_api_id" : product_api_id,
                        "product_base_url" : product_base_url
                    }
                )
                # print("7  success error")     

                ## here update all category
                self.update_product_api_status("success", product_api_id) 
                # break
                # print("8  success error")     
                
            except Exception as e:
                self.logger.error(f"Start Request Error: {e}")
                print("9  success error")   
                self.update_product_api_status("pending", product_api_id)  

    def parse(self, response):
        # print("inside parse")
        print("------fifth------")

        category_name = response.meta.get("category_name")
        sub_category_id = response.meta.get("sub_category_id")
        sub_category_name = response.meta.get("sub_category_name")
        api_url = response.meta.get("api_url")
        product_api_id = response.meta.get("product_api_id")
        product_base_url = response.meta.get("product_base_url")


        if response.status != 200:
            print("25 part 2  success error")  
            self.logger.error(f"Error BAD STATUS {response.status}: {response.url}")
            self.update_product_api_status("pending", product_api_id)
            return   #  stop processing


        # print("product_or_sub_category base url : ", product_base_url)

        api_response = response.json()
            
        # with open("category_data5.json", "w", encoding="utf-8") as f:
        #     json.dump(api_response, f, indent=4)   # ✅ correct way

        if api_response.get("products"):
            # print("INSIDE child yes products")
            
            try :
                product_data_list = api_response.get("products")

                for dict_data in product_data_list:

                    items = TacomaProductScrapeItem()  

                    items["type"] = "product_detail"
                    
                    items["category_name"] = category_name
                    items["sub_category_id"] = sub_category_id
                    items["sub_category_name"] = sub_category_name


                    # product_id = dict_data.get("id")
                    items["product_id"] = dict_data.get("id")
                    # print(product_id )
                
                    # product_name = dict_data.get("shortDescription")
                    items["product_name"] = dict_data.get("shortDescription")
                    # print(product_name )

                    # product_url = product_base_url + dict_data.get("productDetailUrl") 
                    items["product_url"] = product_base_url + dict_data.get("productDetailUrl")
                    # print(product_url )
                    # print(items)

                    yield items

            
                # print("check pagination ")
                if api_response.get("pagination").get("nextPageUri"):
                    # print("yes get pagination ")

                    next_page_api = api_response.get("pagination").get("nextPageUri")
                    print("next_page_url : ",next_page_api)
                    self.logger.info(f"Next page: {next_page_api}")
                    
                    yield scrapy.Request(
                        url=next_page_api,
                        callback=self.parse,
                        errback=self.handle_http_error,   #  ADD THIS
                        meta={
                            "handle_httpstatus_all": True,   #  IMPORTANT
                            "category_name": category_name,
                            "sub_category_id" : sub_category_id,
                            "sub_category_name": sub_category_name,
                            "api_url": api_url,
                            "product_api_id" : product_api_id,
                            "product_base_url" : product_base_url
                        }
                    )

            except Exception as e:
                self.logger.error(f"parse Error: {e}")
                print("9  success error")   
                self.update_product_api_status("pending", product_api_id)
                return

