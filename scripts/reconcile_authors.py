import csv
import requests
import time
import json

authors_matches = {}

try:
	authors_matches = json.load(open('../data/authors_matches.json'))
except:
	pass



with open('../data/pen_2022-2023_book_bans_by_author_title.csv') as infile:

	reader = csv.DictReader(infile)
	

	for row in reader:

		if row['author'] not in authors_matches:

			url = "https://id.loc.gov/authorities/names/suggest2/"
			params = {
				'q': row['author'],
				'rdftype': 'PersonalName'
			}

			req = requests.get(url,params=params)
			# print(row)
			# print(params)
			# print(req.text)
			print(row['author'])


			
			authors_matches[row['author']] = {
				'author': row['author'],
				'matches': req.json()
			}


			time.sleep(1)
			json.dump(authors_matches,open('../data/authors_matches.json','w'),indent=2)