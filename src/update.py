from urllib.request import urlopen
import json
from pymongo import MongoClient
import time
import urllib.parse


client = MongoClient("Mongo Key")
db = client["ShopifyBot"]
r = 0
#Inf loop with a sleep on it
def getJSON(url):
    try:
        response = urlopen(url,timeout=20)
    except urllib.error.HTTPError as e:
        print("ERROR")
        print(e)
    data_json = json.loads(response.read())
    return data_json


while True:
    r += 1
    print(f"\nRun #{r}\n")
    #Get all collections in mongo
    collection_names = db.list_collection_names()

    #Loop though collections
    for name in collection_names:
        #Set collections and URL for comparisions
        collection = db[f"{name}"]
        #documents Get
        document_count = collection.count_documents({})
        document_count = document_count - 1 #(dont count _id:0)

        counter = 1
        for x in range(document_count):
            prodData = collection.find_one({"_id": counter})
            title = prodData["title"]
            price = prodData["price"]
            handle_id = prodData["handle"]
            handle_id = urllib.parse.quote(handle_id)
            last_buy = prodData["bought"]
            url = f"https://{name}/products/{handle_id}/products.json"
            data_json = getJSON(url)
            last_sold = data_json["product"]['updated_at']
            counter += 1
            if last_buy != last_sold: #Item Bought
                counter -= 1
                print(f"{title} has been bought!")
                #New Buy Time, New Total Sales/Count Update
                prodData["bought"] = last_sold
                prodData["total_price"] += price
                prodData["total_sales"] += 1
                collection.replace_one({"_id":counter}, prodData)
                #New Total Sales(Week,Alltime) Update 
                salesData = collection.find_one({"_id": 0})
                salesData["total"] += price
                salesData["week"] += price
                collection.replace_one({"_id":0}, salesData)
    time.sleep(30)
