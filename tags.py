#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import re
"""
Program checks if the keys are valid for monngodb. The "k" values for each "<tag>" will be checked.
The regular expressions check for certain patterns. 
"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


"""
The key_type method checks if there is a key "k" in the tags and checks if the
regular expressions (defined above) are met and raises the value of the corresponding type of
value in the keys-dicitonary in the process_map method.
. 
"""
def key_type(element, keys):

    if element.tag == "tag":
        
        if lower.search(str(element.get("k"))) is not None:
            keys['lower'] += 1
        elif lower_colon.search(str(element.get("k"))) is not None:
            keys['lower_colon'] += 1
        elif problemchars.search(str(element.get("k"))) is not None:
            keys['problemchars'] += 1
        else:
            keys['other'] += 1

        
    return keys



def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
        element.clear() #prevents memory error in big files
    return keys
