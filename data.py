#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import re
import codecs
import json
import pymongo
import audit
from bson import json_util
"""
The data is transformed into Your task is to wrangle the data and transform the shape of the data
into the model we mentioned earlier. The output should be a list of dictionaries
that look like this:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}

You have to complete the function 'shape_element'.
We have provided a function that will parse the map file, and call the function with the element
as an argument. You should return a dictionary, containing the shaped data for that element.
We have also provided a way to save the data in a file, so that you could use
mongoimport later on to import the shaped data into MongoDB. 

Note that in this exercise we do not use the 'update street name' procedures
you worked on in the previous exercise. If you are using this code in your final
project, you are strongly encouraged to use the code from previous exercise to 
update the street names before you save them to JSON. 

In particular the following things should be done:
- you should process only 2 types of top level tags: "node" and "way"
- all attributes of "node" and "way" should be turned into regular key/value pairs, except:
    - attributes in the CREATED array should be added under a key "created"
    - attributes for latitude and longitude should be added to a "pos" array,
      for use in geospacial indexing. Make sure the values inside "pos" array are floats
      and not strings. 
- if second level tag "k" value contains problematic characters, it should be ignored
- if second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
- if second level tag "k" value does not start with "addr:", but contains ":", you can process it
  same as any other tag.
- if there is a second ":" that separates the type/direction of a street,
  the tag should be ignored, for example:

<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>

  should be turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}

- for "way" specifically:

  <nd ref="305896090"/>
  <nd ref="1719825889"/>

should be turned into
"node_refs": ["305896090", "1719825889"]
"""

#regular expressions to check for characters, that might me problematic for mongodb
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"] #list with "created" arguments
COORDINATES = ['lat','lon'] #list to check for coordinates

def shape_element(element):
    node = {}
    
    if element.tag == "node" or element.tag == "way" :

        # created and position elements: 
        node['type'] = element.tag
        
        for attribute in element.attrib:


            #created dictionary
            if attribute in CREATED: 
                if 'created' not in node:
                    node['created'] = {}
                #timestamp is not json serializeable    
                if attribute == "timestamp":
                    node['created'][attribute] = str(element.attrib[attribute])

                else: 
                    node['created'][attribute] = element.attrib[attribute]

            #position list
            elif attribute in COORDINATES:
                if 'pos' not in node:
                    node['pos'] = [None,None]
                    
                if attribute == 'lat':
                    node['pos'][0] = float(element.attrib[attribute])
                if attribute == 'lon': 
                    node['pos'][1] = float(element.attrib[attribute])
            else:
                node[attribute] = element.attrib[attribute]
     
        #iterate over child-tags:   
        for tag in element.iter("tag"):
            if not problemchars.search(tag.attrib['k']):

                # Tags with single colon and beginning with addr
                if lower_colon.search(tag.attrib['k']) and tag.attrib['k'].find('addr') == 0:
                    if 'address' not in node:
                        node['address'] = {}

                    small_attribute = tag.attrib['k'].split(':', 1)

                    if audit.is_street_name(tag):
                        better_name = audit.update_name(tag.attrib['v'], audit.mapping_road)
                        better_name_direction = audit.update_direction(better_name, audit.mapping_directions)
                        node['address'][small_attribute[1]] = better_name_direction

                    else:    
                        node['address'][small_attribute[1]] = tag.attrib['v']

                # All other tags that don't begin with "addr"
                elif not tag.attrib['k'].find('addr') == 0:
                    if tag.attrib['k'] not in node:
                        node[tag.attrib['k']] = tag.attrib['v']
                else:
                    node["tag:" + tag.attrib['k']] = tag.attrib['v']
            
                    
       # change node_refs in way elements
        for nd in element.iter("nd"):
            if 'node_refs' not in node:
                node['node_refs'] = []
            node['node_refs'].append(nd.attrib['ref'])      
        return node
        
    else:
        return None

    
    
def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2, default=json_util.default)+"\n")
                    
                else:
                    fo.write(json.dumps(el, default=json_util.default) + "\n")
                    
                element.clear() #prevents from memory error
    return data


def run():
    data = process_map('cleveland-original.osm', False)

if __name__ == "__main__":
    run()
