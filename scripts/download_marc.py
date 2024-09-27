import requests
import json

titles_compiled = json.load(open('../data/titles_compiled.json'))


for t in titles_compiled:
	if titles_compiled[t]['lcBib'] != None:

		url = f"https://id.loc.gov/data/bibs/{titles_compiled[t]['lcBib']}.marcxml.xml"
		marcreq = requests.get(url)
		if marcreq.status_code == 200:
			marc = marcreq.text
			
			with open(f"../data/marc/{titles_compiled[t]['lcBib']}.xml",'w') as out:
				out.write(marc)
			
			
		else:
			print("Error with",url)
