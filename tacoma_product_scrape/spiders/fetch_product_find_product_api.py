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
        # sub_category_name = request.meta.get("sub_category_name")

        # Detect error type
        error_type = type(failure.value).__name__

        self.logger.error(
            f"HTTP ERROR: {url} | TYPE: {error_type}"
        )

        # # Optional: store in DB
        # self.store_failed_request(
        #     url=url,
        #     error=error_type
        # )

    def update_category_status(self, status,  category_id):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="actowiz",
                database="tacoma_scrapy_db",
                port="3306"
            )
            # print("1 success error")     

            cursor = connection.cursor()
            cursor.execute(
                "UPDATE all_category SET status=%s WHERE id=%s",
                (status, category_id,)
            )
            connection.commit()

            self.logger.info(f" Updated category {category_id}")
            # print("2 success error")     


        except mysql.connector.Error as e:
            self.logger.error(f" DB Update Error: {e}")
            # print("3 success error")     


        cursor.close()
        connection.close()




    # -------------------------------
    # Fetch all categories from DB
    # -------------------------------
    def fetch_all_categories(self):
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="actowiz",
            database="tacoma_scrapy_db",
            port="3306"
        )
        print("------first------")
        # print("4 success error")     

        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM all_category WHERE status='pending'")
        rows = cursor.fetchall()
        # print("5 success error")     

        cursor.close()
        connection.close()
        return rows


    def start_requests(self):
        print("------second------")

        rows = self.fetch_all_categories()  # Fetch all pending categories

        for row in rows:
            # print("row now :: ", row)
            try:
                # print("6  success error")     

                category_id = row["id"]
                category_name = row["category_name"]
                category_url = row["url"]
                status = row["status"]

                # print("category_name : ", category_name, category_url, status)

                # here is changes ..
                # if category_name != "Building-Ground-Maintenance" :
                #     continue


                # print("right category_name : ", category_name, category_url, status)
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
                # print("7  success error")     

                ## here update all category
                self.update_category_status("success", category_id) 
                # break
                # print("8  success error")     
                
            except Exception as e:
                self.logger.error(f"1 parse Error: {e}")
                print("9  success error")   
                self.update_category_status("pending", category_id)  



    def parse(self, response):
        print("------third------")
        category_name = response.meta.get("category_name")
        category_url = response.meta.get("category_url")
        category_id = response.meta.get("category_id")

        if response.status != 200:
            print("25 part 2  success error")  
            self.logger.error(f"BAD STATUS {response.status}: {response.url}")
            self.update_category_status("pending", category_id)
            # self.store_failed_request(
            #     url=response.url,
            #     error=f"HTTP {response.status}"
            # )
            return   #  stop processing
        # pass

        # def single_category_url(self, response):
        try:
            # print("10  success error")     

            base_api_url = r"https://www.tacomascrew.com/api/v1/catalogpages?path=%2FCatalog%2F"
            base_url =  "https://www.tacomascrew.com"

            

            category_name_lower = category_name.lower().replace(" / ", "-").replace(" ","-")
            category_api_url = base_api_url + category_name_lower
            print("category_api_url ", category_api_url)
            print("2 category_api_url ", category_name , category_url)

            # print("11  success error")     

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
            # print("12  success error")     

        except Exception as e:
            self.logger.error(f"2 parse Error: {e}")
            print("13  success error")     
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

        if response.status != 200:
            print("25 part 2  success error")  
            self.logger.error(f"BAD STATUS {response.status}: {response.url}")
            self.update_category_status("pending", category_id)
            # self.store_failed_request(
            #     url=response.url,
            #     error=f"HTTP {response.status}"
            # )
            return   #  stop processing

      # Convert response to JSON
        try:
            # print("14  success error")     

            data = response.json()   # BEST way

            # with open("category_data.json", "w", encoding="utf-8") as f:
            #     json.dump(data, f, indent=4)   #  correct way



            

            sub_category_list = data.get("category").get("subCategories") 

            # print(len(sub_category_list))
            
            for dict_data in sub_category_list:
                try:
                    # print("15  success error")     

                    start_api = r"https://www.tacomascrew.com/api/v1/products/?applyPersonalization=true&categoryId="
                    end_api = r"&expand=pricing,attributes,facets,brand&getAllAttributeFacets=true&includeAlternateInventory=true&includeAttributes=IncludeOnProduct&includeSuggestions=true&makeBrandUrls=false&previouslyPurchasedProducts=false&searchWithin=&stockedItemsOnly=false"
                    
                    sub_category_id = dict_data.get("id")
                    sub_category_name = dict_data.get("name").replace("&", "and")
                    print("3sub_category_base_api" , sub_category_id, sub_category_name)
                    

                    ### this  will remove after complete .....now 
                    # if sub_category_name != "Paint and Accessories" :
                    #     continue

                    sub_category_base_api = start_api + sub_category_id + end_api

                    print("3sub_category_base_api" , sub_category_id)

                    print("4 sub_category_base_api" , sub_category_name, sub_category_base_api)
                    # break
                    # print("16  success error")     

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
                            "category_id" : category_id
                        }
                    )
                    # print("17  success error")     

                    # break
                except Exception as e:
                    self.logger.error(f"3 inside parse Error: {e}")
                    print("18  success error")     
                    self.update_category_status("pending", category_id)
                    break
                    

        except Exception as e:
            self.logger.error(f"3 parse Error: {e}")
            print("19  success error") 
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

        if response.status != 200:
            print("25 part 2  success error")  
            self.logger.error(f"BAD STATUS {response.status}: {response.url}")
            self.update_category_status("pending", category_id)
            # self.store_failed_request(
            #     url=response.url,
            #     error=f"HTTP {response.status}"
            # )
            return   #  stop processing

        try:
            # print("20  success error")     
            
            

            sub_category_data = response.json()



            # with open("category_data2.json", "w", encoding="utf-8") as f:
            #     json.dump(sub_category_data, f, indent=4)   #  correct way

            if sub_category_data.get("products"):
                print("yes product",sub_category_name, category_api_url  )


                ## sub_category_base_api is product_api url ...
                # print("yes products")



                yield {
                    "type": "product_api",
                    "category_name": category_name,
                    "sub_category_id" : sub_category_id,
                    "sub_category_name": sub_category_name.replace(" / ", "-").replace(" ","-").replace("--", ""),
                    "api_url" : sub_category_base_api
                }


            else:
                ## part 2 now of subCategories
                print("yes subCategories",sub_category_name, category_api_url  )


                ### her is convert change...
                # sub_category_name_lower  = sub_category_name.lower().replace(" ", "-")

                ## this right 
                sub_category_name_lower  = sub_category_name.lower().replace(" / ", "-").replace(" ","-") #.replace("&", "and")
                clean_sub_category_name =  re.sub(r"-{2,}", '', sub_category_name_lower)
                child_category_api_url = category_api_url + r"%2F" + clean_sub_category_name
                print("child_category_api_url url : ", child_category_api_url)


                ## checking url 
                # check_url = r"https://www.tacomascrew.com/api/v1/catalogpages?path=%2FCatalog%2Fabrasives%2Fcut-off-wheels"
                # print("inside inside for check : ", check_url)
                # print("22  success error")     
                
                yield scrapy.Request(
                    url=child_category_api_url,
                    callback=self.child_sub_category,
                    errback=self.handle_http_error,   #  ADD THIS
                    meta={
                        "handle_httpstatus_all": True,   #  IMPORTANT
                        "category_name" : category_name,
                        "base_api_url" : base_api_url,
                        "base_url" : base_url,
                        "sub_category_id" : sub_category_id,
                        "sub_category_name" : sub_category_name,
                        "category_api_url" : category_api_url,
                        "child_category_api_url" : child_category_api_url,
                        "category_id" : category_id
                    }
                ) 
                # print("23  success error")     
        except Exception as e:

            ## not go in this now so where insert update 
            print("24  success error")     

            self.logger.error(f"4 parse Error: {e}")
            self.update_category_status("pending", category_id)
            return   #  stop processing

            

    def child_sub_category(self, response):
        print("------sixth------")


        category_name = response.meta.get("category_name")
        base_api_url = response.meta.get("base_api_url")
        base_url = response.meta.get("base_url")
        sub_category_id = response.meta.get("sub_category_id")
        sub_category_name = response.meta.get("sub_category_name")
        category_api_url = response.meta.get("category_api_url")
        child_category_api_url = response.meta.get("child_category_api_url") ## ofthonal
        category_id = response.meta.get("category_id")
    
        if response.status != 200:
            print("25 part 2  success error")  
            self.logger.error(f"BAD STATUS {response.status}: {response.url}")
            self.update_category_status("pending", category_id)
            # self.store_failed_request(
            #     url=response.url,
            #     error=f"HTTP {response.status}"
            # )
            return   #  stop processing


        try:
            # print("25  success error")     

            data = response.json()   # BEST way
            # print full JSON (for debugging)
            # with open("category_data3.json", "w", encoding="utf-8") as f:
            #     json.dump(data, f, indent=4)   #  correct way
            # print(data)
            # print(now_response.body)




            sub_category_list = data.get("category").get("subCategories") #category.  category.subCategories

            for dict_data in sub_category_list:
                start_api = r"https://www.tacomascrew.com/api/v1/products/?applyPersonalization=true&categoryId="
                end_api = r"&expand=pricing,attributes,facets,brand&getAllAttributeFacets=true&includeAlternateInventory=true&includeAttributes=IncludeOnProduct&includeSuggestions=true&makeBrandUrls=false&previouslyPurchasedProducts=false&searchWithin=&stockedItemsOnly=false"
                child_sub_category_id = dict_data.get("id")
                child_sub_category_name = dict_data.get("name")
                # print("then sub_category_name : ", child_sub_category_id, child_sub_category_name)
                
                sub_category_base_api = start_api + child_sub_category_id + end_api
                print("sub_category_name : ",sub_category_base_api)

                # print("26  success error")     

                yield scrapy.Request(
                    url=sub_category_base_api,
                    callback=self.child_product_or_sub_category,
                    errback=self.handle_http_error,   #  ADD THIS
                    meta={
                        "handle_httpstatus_all": True,   #  IMPORTANT
                        "category_name" : category_name,
                        "base_api_url" : base_api_url,
                        "base_url" : base_url,
                        "sub_category_id" : sub_category_id,
                        "sub_category_name" : sub_category_name,
                        "category_api_url" : category_api_url,
                        "child_sub_category_id" : child_sub_category_id,
                        "child_sub_category_name" : child_sub_category_name,
                        "sub_category_base_api" : sub_category_base_api,
                        "category_id" : category_id

                    }
                )
                # print("27  success error")     

                # break
        except Exception as e:
            self.logger.error(f"5 parse Error: {e}")
            print("28  success error") 
            self.update_category_status("pending", category_id)
            return    
            

    def child_product_or_sub_category(self, response):
        print("------fifth------")

        category_name = response.meta.get("category_name")
        base_api_url = response.meta.get("base_api_url")
        base_url = response.meta.get("base_url")
        sub_category_id = response.meta.get("sub_category_id")
        sub_category_name = response.meta.get("sub_category_name")
        category_api_url = response.meta.get("category_api_url")
        child_sub_category_id = response.meta.get("child_sub_category_id")
        child_sub_category_name = response.meta.get("child_sub_category_name")
        sub_category_base_api = response.meta.get("sub_category_base_api")
        category_id = response.meta.get("category_id")

        if response.status != 200:
            print("25 part 2  success error")  
            self.logger.error(f"BAD STATUS {response.status}: {response.url}")
            self.update_category_status("pending", category_id)
            # self.store_failed_request(
            #     url=response.url,
            #     error=f"HTTP {response.status}"
            # )
            return   #  stop processing

        try:


            # print("final product api : ", sub_category_base_api)
            
            child_sub_category_data = response.json()
                
            # with open("category_data4.json", "w", encoding="utf-8") as f:
            #     json.dump(child_sub_category_data, f, indent=4)   #  correct way
            if child_sub_category_data.get("products"):
                # print("INSIDE child yes products")



                yield {
                    "type": "product_api",
                    "category_name": category_name,
                    "sub_category_id" : sub_category_id,
                    "sub_category_name": sub_category_name.replace(" / ", "-").replace(" ","-").replace("--", "") + "/" + child_sub_category_name.replace(" / ", "-").replace(" ","-").replace("--", ""),
                    "api_url" : sub_category_base_api
                }
        except Exception as e:
            self.logger.error(f"6 parse Error: {e}")
            self.update_category_status("pending", category_id)
            return
        








