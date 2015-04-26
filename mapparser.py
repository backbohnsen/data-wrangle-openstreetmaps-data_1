import xml.etree.cElementTree as ET
import pprint



"""
Every time the parser finds a tag it will check if the specific tag is allready stored
in the "taglist"-dictionary. If it is in the dictionary, the function will increas the value
of the tag by 1, otherwise the tag is added to the dictionary as a new key. 
"""
def count_tags(filename):
        #The tags will be stored and counted in a dictionary taglist
        taglist = dict()

        #Event based iteration through the xml file. event = 'end' indicates the end of the tag.
        for event, elem in ET.iterparse(filename):
            if event == 'end':
                if elem.tag in taglist:
                    taglist[elem.tag] += 1
                else:
                    taglist[elem.tag] = 1
                elem.clear() #prevents from memory-error with big files
        return taglist

