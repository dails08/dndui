import json
import os

with open("citation_dict.json", 'r') as infile:
    citation_dict = json.load(infile)
#citation_dict = {}

for dir, subdirList, filenameList in os.walk(r"C:\Users\Christopher\Dropbox\CoS\COS2\working assets\visual assets\bg"):
	for filename in filenameList:
        if filename not in citation_dict:
            if filename.endswith("mp4"):
                citation_dict[filename] = "James RPG Art"
            elif filename.endswith("webm"):
                citation_dict[filename] = "Beneos Battlemaps"
			
with open("citation_dict.json", 'w') as outfile:
	json.dump(citation_dict, outfile)