import json
import os

citation_dict = {}

for dir, subdirList, filenameList in os.walk(r"C:\Users\Christopher\Dropbox\CoS\COS2\working assets\visual assets\bg"):
	for filename in filenameList:
		if filename.endswith("mp4"):
			citation_dict[filename] = "James RPG Art"
			
with open("citation_dict.json", 'w') as outfile:
	json.dump(citation_dict, outfile)