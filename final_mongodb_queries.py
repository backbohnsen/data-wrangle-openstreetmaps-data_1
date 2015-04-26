"""
The cleveland.json file is imported by the mongoimport.
Mongoimport -d citymap -c cleveland --file "cleveland.json"

After that the MongoClient from pymongo can be used to establish a
connection to the cleveland collection in the citymap database. 
"""

import re
from collections import defaultdict

from pymongo import MongoClient
client = MongoClient('localhost:27017')
db = client["citymap"]

#Number of documents
docnumber = db.cleveland.find().count()
print("The Number of documents in the collection:",docnumber)

#number of nodes
nodenumber = db.cleveland.find({"type":"node"}).count()
print("The Number of nodes in the collection:",nodenumber)

#number of ways
waynumber = db.cleveland.find({"type":"way"}).count()
print("The Number of ways in the collection:",waynumber)

#number of unique users
uniqueuser = len(db.cleveland.distinct('created.user'))
print("The number of unique user-ids:", uniqueuser)

#top 1 contributing user
top_user = db.cleveland.aggregate([{"$group":{"_id": "$created.user", "count":{"$sum":1}}},
                        {"$sort":{"count":-1}},
                        {"$limit":1}])
print("The most active User:", top_user["result"][0]["_id"], "is involved in", top_user["result"][0]["count"],"changes")

#Number of users appearing only once:
users_appearing_1time = db.cleveland.aggregate([{"$group":{"_id":"$created.user", "count":{"$sum":1}}},
                                                {"$group":{"_id":"$count", "num_users":{"$sum":1}}},
                                                {"$sort":{"_id":1}},
                                                {"$limit":1}])

print("There are:",users_appearing_1time["result"][0]["num_users"], "users appearing only once" )

#Number of shops:
number_shops = db.cleveland.aggregate([{"$match":{"shop": {"$exists": 1}}},
                                       {"$group": {"_id": "$shop", "count":{"$sum":1}}},
                                       {"$sort":{"count":-1}}])
