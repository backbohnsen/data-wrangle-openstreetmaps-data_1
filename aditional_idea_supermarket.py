import re
from collections import defaultdict

from pymongo import MongoClient
client = MongoClient('localhost:27017')
db = client["citymap"]

#Number of supermarkets:
number_supermarkets = db.cleveland.aggregate([{"$match":{"shop": "supermarket"}},
                                            {"$group":{"_id": "$supermarket", "count": {"$sum":1}}}
                                            ])

#Supermarkets in descending order:
all_supermarkets = db.cleveland.aggregate([{"$match":{"shop": "supermarket"}},
                                            {"$group":{"_id": "$name", "count": {"$sum":1}}},
                                            {"$sort": {"count":-1}}
                                            ])
#print all supermarkets:
print("All supermarket names in descending order of quantity:\n",all_supermarkets["result"] )

#The output shows that there are some supermarket-chains that occur under different names. 
#Analysing the names:

#build a list of supermarket names: 
all_supermarkets_list = []
for name in range(0,len(all_supermarkets["result"])):
    print (all_supermarkets["result"][name]["_id"])
    all_supermarkets_list.append(all_supermarkets["result"][name]["_id"])
    

#A regex to search for walmart-like names: 
walmart = re.compile('(wal)', re.IGNORECASE)
#A regex to search for acme-like names: 
acme = re.compile(r'acme', re.IGNORECASE)
#A regex to search for aldi-like names: 
aldi = re.compile('(aldi)', re.IGNORECASE)

#loop through the supermarket names list and safe the walmart-like names to a set for further inspection:
nameset = defaultdict(set)
namecount = 0

def audit_supermarket_name(name):

    for i in all_supermarkets_list:
        print (i)
        m = name.search(str([i]))
        if m:
            print (i)
            nameset[name].add(i)
    print(nameset)

#use the audit_supermarket_name function with the regex defined above.
audit_supermarket_name(walmart)
audit_supermarket_name(acme)
audit_supermarket_name(aldi)
