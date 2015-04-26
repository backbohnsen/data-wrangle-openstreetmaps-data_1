#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import re
"""
The function process map returns a set of the unique user-ids that contributed to the file. 
"""
users = set()

def get_user(element):
    for elem in element.iter():
        try:
            uid = (elem.attrib['uid'])
            users.add(uid)
            
        except: 
            None
    


def process_map(filename):
   
    for _, element in ET.iterparse(filename):
        get_user(element)
        element.clear()
    print ("There are :",len(users)," unique User-IDs in the file.")
    return users
    
