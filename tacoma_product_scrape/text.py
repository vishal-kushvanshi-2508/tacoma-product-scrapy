import requests
import json

# url = "https://www.tacomascrew.com/api/v1/catalogpages"
# sub_category_base_api = f"https://www.tacomascrew.com/api/v1/products/?applyPersonalization=true&categoryId={sub_category_id}abfa01121e6d&expand=pricing,attributes,facets,brand&getAllAttributeFacets=true&includeAlternateInventory=true&includeAttributes=IncludeOnProduct&includeSuggestions=true&makeBrandUrls=false&previouslyPurchasedProducts=false&searchWithin=&stockedItemsOnly=false"

# abrasives = r"https://www.tacomascrew.com/api/v1/products/?applyPersonalization=true&categoryId=ed165dca-f64a-4ed3-b8f3-abfa01122fcb&expand=pricing,attributes,facets,brand&getAllAttributeFacets=true&includeAlternateInventory=true&includeAttributes=IncludeOnProduct&includeSuggestions=true&makeBrandUrls=false&previouslyPurchasedProducts=false&searchWithin=&stockedItemsOnly=false"


# abrasives = r"https://www.tacomascrew.com/api/v1/products?page=2&categoryId=ed165dca-f64a-4ed3-b8f3-abfa01122fcb&expand=pricing%2Cattributes%2Cfacets%2Cbrand"

# abrasives = r"https://www.tacomascrew.com/api/v1/products?page=3&categoryId=ed165dca-f64a-4ed3-b8f3-abfa01122fcb&expand=pricing%2Cattributes%2Cfacets%2Cbrand"

url = "https://www.tacomascrew.com/Catalog/soldering-welding/welding/658-007"

new_url = url.replace("https://www.tacomascrew.com","https://www.tacomascrew.com/api/v1/catalogpages?path=")


print("url is : ", new_url)

api_url = "be8d38c3-0213-4825-8387-abfa01124161"
api = f"https://www.tacomascrew.com/api/v1/products/?categoryId={api_url}&page=1&pageSize=5"
print("api  is : ", api)


params = {
    "path": "/Catalog/abrasives/belts"
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

# # response = requests.get(url, params=params, headers=headers)
# response = requests.get(abrasives, headers=headers)

# if response.status_code == 200:
#     data = response.json()
#     with open("text1.json", "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=4)   # ✅ correct way


#     print("check pagination ")
#     if data.get("pagination").get("nextPageUri"):
#         print("yes get pagination ")
#         url = data.get("pagination").get("nextPageUri")
#         print(url)


#     # sub_category_list = data.get("category").get("subCategories") #category.  category.subCategories
#     # # print(sub_category_list)
#     # print(len(sub_category_list))
#     # start_api = r"https://www.tacomascrew.com/api/v1/products/?applyPersonalization=true&categoryId="
#     # end_api = r"abfa01121e6d&expand=pricing,attributes,facets,brand&getAllAttributeFacets=true&includeAlternateInventory=true&includeAttributes=IncludeOnProduct&includeSuggestions=true&makeBrandUrls=false&previouslyPurchasedProducts=false&searchWithin=&stockedItemsOnly=false"
    
#     # for dict_data in sub_category_list:
#     #     sub_category_id = dict_data.get("id")[0:24]
#     #     sub_category_name = dict_data.get("name")
#     #     print("sub_category_name : ", sub_category_id)

#     #     print("sub_category_name : ", sub_category_name)
#     #     sub_category_base_api = start_api + sub_category_id + end_api
#     #     print(sub_category_base_api)

#     #     response = requests.get(sub_category_base_api, headers=headers)

#     #     if response.status_code == 200:
#     #         sub_category_data = response.json()
            
#     #         with open("text2.json", "w", encoding="utf-8") as f:
#     #             json.dump(sub_category_data, f, indent=4)   # ✅ correct way
#     #         if "products" in sub_category_data:
#     #             print("yes products")

#     #         else:
#     #             print("yes subCategories")

                
#     #     else:
#     #         print(f"Request failed: {response.status_code}")
#     #     break




# else:
#     print(f"Request failed: {response.status_code}")




