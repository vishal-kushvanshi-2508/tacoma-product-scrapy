import scrapy
import json
from tacoma_product_scrape.items import TacomaProductScrapeItem

class TacomaSpiderSpider(scrapy.Spider):
    name = "tacoma_spider"
    allowed_domains = ["www.tacomascrew.com"]
    start_urls = ["https://www.tacomascrew.com/all-categories"]

    def parse(self, response):
        # print(response.body)
        print("------first------")

        all_category = response.xpath("//div[@class='category-card x:px-lg x:mb-xxl']")
        # print("done data", all_category)
        print("done data", len(all_category))
        # base_url = response.url.rsplit("/", 1)[0]
        # new_url = base_url + "/Catalog/abrasives"
        base_url = response.url.strip("/").rsplit("/", 1)[0]
        base_api_url = r"https://www.tacomascrew.com/api/v1/catalogpages?path=%2FCatalog%2F"
        print("base_url ", base_api_url)
        for category_data in all_category:
            category_name = category_data.xpath("//a//p/text()").get().strip()
            category_name_lower = category_name.lower().replace(" ", "-")
            # category_url = base_url + category_data.xpath("//a[@class='product-title']/@href").get()
            # url =  response.

            category_api_url = base_api_url + category_name_lower
            print("done data", category_name, category_name_lower)
            print(category_api_url)

            yield scrapy.Request(
                url=category_api_url,
                callback=self.sub_category,
                meta={
                    "category_name" : category_name,
                    "base_api_url" : base_api_url,
                    "base_url" : base_url,
                    "category_api_url" : category_api_url
                }
            )
            break
        print("done data")


    def sub_category(self, response):
        print("------second------")


        # Convert response to JSON
        data = response.json()   # BEST way
        # print full JSON (for debugging)
        with open("category_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)   # ✅ correct way
        # print(data)
        # print(now_response.body)



        category_name = response.meta.get("category_name")
        base_api_url = response.meta.get("base_api_url")
        base_url = response.meta.get("base_url")
        category_api_url = response.meta.get("category_api_url")

        sub_category_list = data.get("category").get("subCategories") #category.  category.subCategories
        # print(sub_category_list)
        print(len(sub_category_list))
        # sub_category_base_api = f"https://www.tacomascrew.com/api/v1/products/?applyPersonalization=true&categoryId={sub_category_id}abfa01121e6d&expand=pricing,attributes,facets,brand&getAllAttributeFacets=true&includeAlternateInventory=true&includeAttributes=IncludeOnProduct&includeSuggestions=true&makeBrandUrls=false&previouslyPurchasedProducts=false&searchWithin=&stockedItemsOnly=false"
        
        start_api = r"https://www.tacomascrew.com/api/v1/products/?applyPersonalization=true&categoryId="
        end_api = r"abfa01121e6d&expand=pricing,attributes,facets,brand&getAllAttributeFacets=true&includeAlternateInventory=true&includeAttributes=IncludeOnProduct&includeSuggestions=true&makeBrandUrls=false&previouslyPurchasedProducts=false&searchWithin=&stockedItemsOnly=false"
        for dict_data in sub_category_list:
            sub_category_id = dict_data.get("id")[0:24]
            sub_category_name = dict_data.get("name")
            print("sub_category_name : ", sub_category_id)
            

            # change heree delete it ..
            sub_category_id = "3bf5ce4e-5e60-474d-aa47-"

            print("sub_category_name : ", sub_category_name)


            sub_category_base_api = start_api + sub_category_id + end_api
            print(sub_category_base_api)

            yield scrapy.Request(
                url=sub_category_base_api,
                callback=self.product_or_sub_category,
                meta={
                    "category_name" : category_name,
                    "base_api_url" : base_api_url,
                    "base_url" : base_url,
                    "sub_category_name" : sub_category_name,
                    "category_api_url" : category_api_url
                }
            )
            break

    def product_or_sub_category(self, response):
        print("------third------")


        # Convert response to JSON
        # data = response.json()   # BEST way

        # response = requests.get(sub_category_base_api, headers=headers)
        category_name = response.meta.get("category_name")
        base_api_url = response.meta.get("base_api_url")
        base_url = response.meta.get("base_url")
        sub_category_name = response.meta.get("sub_category_name")
        category_api_url = response.meta.get("category_api_url")

        print("product_or_sub_category base url : ", base_url)
        print("2 product_or_sub_category base url : ",sub_category_name.lower().replace(" ", "-"),  category_api_url)
        sub_category_data = response.json()
            
        with open("category_data2.json", "w", encoding="utf-8") as f:
            json.dump(sub_category_data, f, indent=4)   # ✅ correct way
        if sub_category_data.get("products"):
            print("yes products")
            product_data_list = sub_category_data.get("products")
            for dict_data in product_data_list:
                product_id = dict_data.get("id")
                print(product_id )
               
                product_name = dict_data.get("shortDescription")
                print(product_name )

                product_url = base_url + dict_data.get("productDetailUrl")
                print(product_url )

                items = TacomaProductScrapeItem()  
                items["product_id"] = product_id
                # print(product_id )
               
                items["product_name"] = product_name
                # print(product_name )

                items["product_url"] = product_url
                # print(product_url )
                yield items

                break

            print(items)
            print(len(items))






        else:
            ## part 2 now of subCategories
            print("yes subCategories")
            sub_category_name_lower  = sub_category_name.lower().replace(" ", "-")
            child_category_api_url = category_api_url + r"%2F" + sub_category_name_lower
            print("child_category_api_url url : ", child_category_api_url)


            ## checking url 
            check_url = r"https://www.tacomascrew.com/api/v1/catalogpages?path=%2FCatalog%2Fabrasives%2Fcut-off-wheels"
            print("inside inside for check : ", check_url)
            yield scrapy.Request(
                url=check_url,
                callback=self.child_sub_category,
                meta={
                    "category_name" : category_name,
                    "base_api_url" : base_api_url,
                    "base_url" : base_url,
                    "sub_category_name" : sub_category_name,
                    "category_api_url" : category_api_url
                }
            )

    def child_sub_category(self, response):
        print("------fourth------")

        data = response.json()   # BEST way
        # print full JSON (for debugging)
        with open("category_data3.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)   # ✅ correct way
        # print(data)
        # print(now_response.body)



        category_name = response.meta.get("category_name")
        base_api_url = response.meta.get("base_api_url")
        base_url = response.meta.get("base_url")
        sub_category_name = response.meta.get("sub_category_name")
        category_api_url = response.meta.get("category_api_url")

        sub_category_list = data.get("category").get("subCategories") #category.  category.subCategories
        # print(sub_category_list)
        print(len(sub_category_list))
        # sub_category_base_api = f"https://www.tacomascrew.com/api/v1/products/?applyPersonalization=true&categoryId={sub_category_id}abfa01121e6d&expand=pricing,attributes,facets,brand&getAllAttributeFacets=true&includeAlternateInventory=true&includeAttributes=IncludeOnProduct&includeSuggestions=true&makeBrandUrls=false&previouslyPurchasedProducts=false&searchWithin=&stockedItemsOnly=false"
        
        start_api = r"https://www.tacomascrew.com/api/v1/products/?applyPersonalization=true&categoryId="
        end_api = r"&expand=pricing,attributes,facets,brand&getAllAttributeFacets=true&includeAlternateInventory=true&includeAttributes=IncludeOnProduct&includeSuggestions=true&makeBrandUrls=false&previouslyPurchasedProducts=false&searchWithin=&stockedItemsOnly=false"
        for dict_data in sub_category_list:
            sub_category_id = dict_data.get("id")
            sub_category_name = dict_data.get("name")
            print("then sub_category_name : ", sub_category_id)
            

            # # change heree delete it ..________check now _________


            
            # sub_category_id = "3bf5ce4e-5e60-474d-aa47-"

            print("sub_category_name : ", sub_category_name)


            sub_category_base_api = start_api + sub_category_id + end_api
            print(sub_category_base_api)

            yield scrapy.Request(
                url=sub_category_base_api,
                callback=self.child_product_or_sub_category,
                meta={
                    "category_name" : category_name,
                    "base_api_url" : base_api_url,
                    "base_url" : base_url,
                    "sub_category_name" : sub_category_name,
                    "category_api_url" : category_api_url
                }
            )
            break

    def child_product_or_sub_category(self, response):
        print("------fifth------")


        # Convert response to JSON
        # data = response.json()   # BEST way

        # response = requests.get(sub_category_base_api, headers=headers)
        category_name = response.meta.get("category_name")
        base_api_url = response.meta.get("base_api_url")
        base_url = response.meta.get("base_url")
        sub_category_name = response.meta.get("sub_category_name")
        category_api_url = response.meta.get("category_api_url")

        print("product_or_sub_category base url : ", base_url)
        print("2 product_or_sub_category base url : ",sub_category_name.lower().replace(" ", "-"),  category_api_url)
        sub_category_data = response.json()
            
        with open("category_data4.json", "w", encoding="utf-8") as f:
            json.dump(sub_category_data, f, indent=4)   # ✅ correct way
        if sub_category_data.get("products"):
            print("yes products")
            product_data_list = sub_category_data.get("products")
            for dict_data in product_data_list:
                items = TacomaProductScrapeItem()  
                items["product_id"] = dict_data.get("id")
                # print(product_id )
               
                items["product_name"] = dict_data.get("shortDescription")
                # print(product_name )

                items["product_url"] = base_url + dict_data.get("productDetailUrl")
                # print(product_url )
                yield items
            print(items)
            print(len(items))




















        # if response.status_code == 200:
        #     pass
        # else:
        #     print(f"Request failed: {response.status_code}")
        # break








            # print("sub_category_name : ", sub_category_base_api)


        # print(category_name, "\nbaseurl : ", base_url )
        # all_sub_category = now_response.xpath("//div[@ng-repeat='subCategory in vm.category.subCategories']")
        # print(all_sub_category)
        # print("all sub ; ", len(all_sub_category))

