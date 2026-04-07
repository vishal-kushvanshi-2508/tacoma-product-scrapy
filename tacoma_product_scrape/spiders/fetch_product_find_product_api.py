
import scrapy
import json
import mysql.connector
import re


class FetchProductFindProductApiSpider(scrapy.Spider):
    name = "fetch_product_find_product_api"
    # allowed_domains = ["www.tacomascrew.com"]

    # start_urls = ["https://www.tacomascrew.com"]


    def handle_http_error(self, failure):
        request = failure.request

        url = request.url
        category_name = request.meta.get("category_name")

        # Detect error type
        error_type = type(failure.value).__name__

        self.logger.error(
            f"HTTP ERROR: {url} | TYPE: {error_type}"
        )

    def update_category_status(self, status,  category_id):
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
                "UPDATE all_category SET status=%s WHERE id=%s",
                (status, category_id,)
            )
            connection.commit()

            self.logger.info(f" Updated category {category_id}")

        except mysql.connector.Error as e:
            self.logger.error(f" DB Update Error: {e}")

        cursor.close()
        connection.close()


    # Fetch all categories from DB
    def fetch_all_categories(self):
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="actowiz",
            database="tacoma_scrapy_db",
            port="3306"
        )
        print("------first------")

        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM all_category WHERE status='pending'")
        rows = cursor.fetchall()

        cursor.close()
        connection.close()
        return rows


    def start_requests(self):
        print("------second------")

        rows = self.fetch_all_categories()  # Fetch all pending categories

        for row in rows:
            try:
                category_id = row["id"]
                category_name = row["category_name"]
                category_url = row["url"]
                status = row["status"]

                yield scrapy.Request(
                    url=category_url,
                    callback=self.parse,
                    errback=self.handle_http_error,   #  ADD THIS
                    meta={
                        "handle_httpstatus_all": True,   #  IMPORTANT
                        "category_name": category_name,
                        "category_url": category_url,
                        "category_id" : category_id
                    }
                )

                ## here update all category
                self.update_category_status("success", category_id) 
                
            except Exception as e:
                self.logger.error(f"1 parse Error: {e}")
                self.update_category_status("pending", category_id)  



    def parse(self, response):
        print("------third------")
        category_name = response.meta.get("category_name")
        category_url = response.meta.get("category_url")
        category_id = response.meta.get("category_id")

        if response.status != 200:
            self.logger.error(f"BAD STATUS {response.status}: {response.url}")
            self.update_category_status("pending", category_id)
            return   #  stop processing

        try:
            base_api_url = r"https://www.tacomascrew.com/api/v1/catalogpages?path=%2FCatalog%2F"
            base_url =  "https://www.tacomascrew.com"
            category_name_lower = category_name.lower().replace(" / ", "-").replace(" ","-")
            category_api_url = base_api_url + category_name_lower

            yield scrapy.Request(
                url=category_api_url,
                callback=self.sub_category,
                errback=self.handle_http_error,   #  ADD THIS
                meta={
                    "handle_httpstatus_all": True,   #  IMPORTANT
                    "category_name": category_name,
                    "category_url": category_url,
                    "category_api_url" : category_api_url,
                    "base_api_url" : base_api_url,
                    "base_url" : base_url,
                    "category_id" : category_id
                    
                }
            )

        except Exception as e:
            self.logger.error(f"2 parse Error: {e}")
            self.update_category_status("pending", category_id)
            return


    def sub_category(self, response):
        print("------fourth------")

        category_name = response.meta.get("category_name")
        category_url = response.meta.get("category_url")
        category_api_url = response.meta.get("category_api_url")
        base_api_url = response.meta.get("base_api_url")
        base_url = response.meta.get("base_url")
        category_id = response.meta.get("category_id")
        child_sub_category_name = response.meta.get("child_sub_category_name", "")

        if response.status != 200:
            print("25 part 2  success error")  
            self.logger.error(f"BAD STATUS {response.status}: {response.url}")
            self.update_category_status("pending", category_id)
            return   #  stop processing

        try:
            data = response.json()   # BEST way
            sub_category_list = data.get("category").get("subCategories") 
            for dict_data in sub_category_list:
                try:
                    start_api = r"https://www.tacomascrew.com/api/v1/products/?applyPersonalization=true&categoryId="
                    end_api = r"&expand=pricing,attributes,facets,brand&getAllAttributeFacets=true&includeAlternateInventory=true&includeAttributes=IncludeOnProduct&includeSuggestions=true&makeBrandUrls=false&previouslyPurchasedProducts=false&searchWithin=&stockedItemsOnly=false"
                    
                    sub_category_id = dict_data.get("id")
                    sub_category_name = dict_data.get("name").replace("&", "and")
                    sub_category_base_api = start_api + sub_category_id + end_api

                    yield scrapy.Request(
                        url=sub_category_base_api,
                        callback=self.product_or_sub_category,
                        errback=self.handle_http_error,   #  ADD THIS
                        meta={
                            "handle_httpstatus_all": True,   #  IMPORTANT
                            "category_name" : category_name,
                            "base_api_url" : base_api_url,
                            "base_url" : base_url,
                            "sub_category_id" : sub_category_id,
                            "sub_category_name" : sub_category_name,
                            "category_api_url" : category_api_url,
                            "sub_category_base_api" : sub_category_base_api,
                            "child_sub_category_name" : child_sub_category_name,
                            "category_id" : category_id
                        }
                    )
                except Exception as e:
                    self.logger.error(f"3 inside parse Error: {e}")
                    self.update_category_status("pending", category_id)
                    break
                    

        except Exception as e:
            self.logger.error(f"3 parse Error: {e}")
            self.update_category_status("pending", category_id)
            return    

            


    def product_or_sub_category(self, response):
        print("------fifth------")
        category_name = response.meta.get("category_name")
        base_api_url = response.meta.get("base_api_url")
        base_url = response.meta.get("base_url")
        sub_category_id = response.meta.get("sub_category_id")
        sub_category_name = response.meta.get("sub_category_name")
        category_api_url = response.meta.get("category_api_url")
        sub_category_base_api = response.meta.get("sub_category_base_api")
        category_id = response.meta.get("category_id")
        child_sub_category_name = response.meta.get("child_sub_category_name")

        if response.status != 200:
            self.logger.error(f"BAD STATUS {response.status}: {response.url}")
            self.update_category_status("pending", category_id)
            return   #  stop processing

        try:
            if child_sub_category_name:
                child_sub_category_name = child_sub_category_name.replace(" / ", "-").replace(" ","-").replace("--", "") + "/" + sub_category_name.replace(" / ", "-").replace(" ","-").replace("--", "")
            elif not child_sub_category_name :
                child_sub_category_name = sub_category_name.replace(" / ", "-").replace(" ","-").replace("--", "")
            
            sub_category_data = response.json()
            if sub_category_data.get("products"):

                yield {
                    "type": "product_api",
                    "category_name": category_name,
                    "sub_category_id" : sub_category_id,
                    "sub_category_name": child_sub_category_name,
                    "api_url" : sub_category_base_api
                }

            else:
                print("yes subCategories",sub_category_name, category_api_url  )

                sub_category_name_lower  = sub_category_name.lower().replace(" / ", "-").replace(".", "-").replace(" ","-").replace("--", "").replace(',-', "")
                clean_sub_category_name =  re.sub(r"[^a-zA-Z0-9]+", '-', sub_category_name_lower)
                clean_sub_category_name = clean_sub_category_name.strip('-').lower()              # remove extra - and lowercase
                child_category_api_url = category_api_url + r"%2F" + clean_sub_category_name
                print("child_category_api_url url : ", child_category_api_url)

                yield scrapy.Request(
                    url=child_category_api_url,
                    callback=self.sub_category,
                    errback=self.handle_http_error,   #  ADD THIS
                    meta={
                        "handle_httpstatus_all": True,   #  IMPORTANT
                        "category_name" : category_name,
                        "base_api_url" : base_api_url,
                        "base_url" : base_url,
                        "sub_category_id" : sub_category_id,
                        "sub_category_name" : sub_category_name,
                        "category_api_url" : category_api_url,
                        "category_id" : category_id,
                        "child_sub_category_name" : child_sub_category_name,
                        "category_api_url" : child_category_api_url
                    }
                ) 

        except Exception as e:

            print("24  success error")     
            self.logger.error(f"4 parse Error: {e}")
            self.update_category_status("pending", category_id)
            return   #  stop processing

        










#######------
# chatGPT code 
#######------



# import scrapy
# import mysql.connector
# import re


# class FetchProductFindProductApiSpider(scrapy.Spider):
#     name = "fetch_product_find_product_api"

#     def __init__(self):
#         self.category_request_count = {}

#     # -------------------------------
#     # DB CONNECTION
#     # -------------------------------
#     def get_connection(self):
#         return mysql.connector.connect(
#             host="localhost",
#             user="root",
#             password="actowiz",
#             database="tacoma_scrapy_db",
#             port="3306"
#         )

#     # -------------------------------
#     # UPDATE STATUS
#     # -------------------------------
#     def update_category_status(self, status, category_id):
#         try:
#             conn = self.get_connection()
#             cursor = conn.cursor()

#             cursor.execute(
#                 "UPDATE all_category SET status=%s WHERE id=%s",
#                 (status, category_id)
#             )
#             conn.commit()

#             self.logger.info(f"Category {category_id} → {status}")

#         except Exception as e:
#             self.logger.error(f"DB Error: {e}")

#         finally:
#             cursor.close()
#             conn.close()

#     # -------------------------------
#     # FETCH CATEGORY
#     # -------------------------------
#     def fetch_all_categories(self):
#         conn = self.get_connection()
#         cursor = conn.cursor(dictionary=True)

#         cursor.execute("SELECT * FROM all_category WHERE status='pending'")
#         rows = cursor.fetchall()

#         cursor.close()
#         conn.close()
#         return rows

#     # -------------------------------
#     # START REQUESTS
#     # -------------------------------
#     def start_requests(self):
#         rows = self.fetch_all_categories()

#         for row in rows:
#             category_id = row["id"]

#             # initialize counter
#             self.category_request_count[category_id] = 1

#             yield scrapy.Request(
#                 url=row["url"],
#                 callback=self.parse,
#                 errback=self.handle_error,
#                 meta={
#                     "category_id": category_id,
#                     "category_name": row["category_name"],
#                     "category_url": row["url"]
#                 }
#             )

#     # -------------------------------
#     # ERROR HANDLER
#     # -------------------------------
#     def handle_error(self, failure):
#         request = failure.request
#         category_id = request.meta.get("category_id")

#         self.logger.error(f"Request failed: {request.url}")

#         self.decrease_counter(category_id)

#     # -------------------------------
#     # COUNTER LOGIC
#     # -------------------------------
#     def increase_counter(self, category_id):
#         self.category_request_count[category_id] += 1

#     def decrease_counter(self, category_id):
#         self.category_request_count[category_id] -= 1

#         if self.category_request_count[category_id] == 0:
#             self.update_category_status("success", category_id)

#     # -------------------------------
#     # PARSE CATEGORY
#     # -------------------------------
#     def parse(self, response):
#         category_id = response.meta["category_id"]
#         category_name = response.meta["category_name"]

#         try:
#             base_api = "https://www.tacomascrew.com/api/v1/catalogpages?path=%2FCatalog%2F"

#             slug = category_name.lower().replace(" / ", "-").replace(" ", "-")
#             api_url = base_api + slug

#             self.increase_counter(category_id)

#             yield scrapy.Request(
#                 url=api_url,
#                 callback=self.sub_category,
#                 errback=self.handle_error,
#                 meta={**response.meta, "category_api_url": api_url}
#             )

#         except Exception as e:
#             self.logger.error(e)

#         self.decrease_counter(category_id)

#     # -------------------------------
#     # SUB CATEGORY
#     # -------------------------------
#     def sub_category(self, response):
#         category_id = response.meta["category_id"]

#         try:
#             data = response.json()
#             sub_categories = data.get("category", {}).get("subCategories", [])

#             for sub in sub_categories:
#                 sub_id = sub.get("id")
#                 sub_name = sub.get("name", "")

#                 api = f"https://www.tacomascrew.com/api/v1/products/?categoryId={sub_id}"

#                 self.increase_counter(category_id)

#                 yield scrapy.Request(
#                     url=api,
#                     callback=self.product_or_sub_category,
#                     errback=self.handle_error,
#                     meta={
#                         **response.meta,
#                         "sub_category_id": sub_id,
#                         "sub_category_name": sub_name,
#                         "sub_api": api
#                     }
#                 )

#         except Exception as e:
#             self.logger.error(e)

#         self.decrease_counter(category_id)

#     # -------------------------------
#     # PRODUCT OR CHILD CATEGORY
#     # -------------------------------
#     def product_or_sub_category(self, response):
#         category_id = response.meta["category_id"]

#         try:
#             data = response.json()

#             #  PRODUCTS FOUND
#             if data.get("products"):
#                 yield {
#                     "type": "product_api",
#                     "category_name": response.meta["category_name"],
#                     "sub_category_name": response.meta["sub_category_name"],
#                     "api_url": response.meta["sub_api"]
#                 }

#             #  NO PRODUCTS → GO DEEPER
#             else:
#                 sub_name = response.meta["sub_category_name"]
#                 base_api = response.meta["category_api_url"]

#                 clean = re.sub(r"-{2,}", "", sub_name.lower().replace(" ", "-"))
#                 new_url = base_api + "%2F" + clean.replace("-/", "").replace("-/-", "-").replace("&", "and")

#                 self.increase_counter(category_id)

#                 yield scrapy.Request(
#                     url=new_url,
#                     callback=self.child_sub_category,
#                     errback=self.handle_error,
#                     meta={**response.meta, "child_url": new_url}
#                 )

#         except Exception as e:
#             self.logger.error(e)

#         self.decrease_counter(category_id)

#     # -------------------------------
#     # CHILD CATEGORY
#     # -------------------------------
#     def child_sub_category(self, response):
#         category_id = response.meta["category_id"]

#         try:
#             data = response.json()
#             subs = data.get("category", {}).get("subCategories", [])

#             for sub in subs:
#                 sub_id = sub.get("id")
#                 sub_name = sub.get("name", "")

#                 api = f"https://www.tacomascrew.com/api/v1/products/?categoryId={sub_id}"

#                 self.increase_counter(category_id)

#                 yield scrapy.Request(
#                     url=api,
#                     callback=self.child_product,
#                     errback=self.handle_error,
#                     meta={
#                         **response.meta,
#                         "child_sub_name": sub_name,
#                         "sub_api": api
#                     }
#                 )

#         except Exception as e:
#             self.logger.error(e)

#         self.decrease_counter(category_id)

#     # -------------------------------
#     # FINAL PRODUCT LEVEL
#     # -------------------------------
#     def child_product(self, response):
#         category_id = response.meta["category_id"]

#         try:
#             data = response.json()

#             if data.get("products"):
#                 yield {
#                     "type": "product_api",
#                     "category_name": response.meta["category_name"],
#                     "sub_category_name": response.meta["sub_category_name"]
#                     + "/" + response.meta["child_sub_name"],
#                     "api_url": response.meta["sub_api"]
#                 }

#         except Exception as e:
#             self.logger.error(e)

#         self.decrease_counter(category_id)

