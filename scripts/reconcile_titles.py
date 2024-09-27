import csv
import requests
import time
import json

authors_matches = {}

try:
	authors_matches = json.load(open('../data/authors_matches.json'))
except:
	pass


titles_matched = {}

try:
	titles_matched = json.load(open('../data/titles_matched.json'))
except:
	pass






with open('../data/pen_2022-2023_book_bans_by_author_title.csv') as infile:

	reader = csv.DictReader(infile)
	
	for row in reader:

		title_author = row['author'] + ' ' + row['title']

		if title_author not in titles_matched:

			print(row['author'], row['title'])
			titles_matched[title_author] = {
				'author': row['author'],
				'title': row['title'],
				'results': []
			}

			for hit in authors_matches[row['author']]['matches']['hits']:

				lccn = hit['uri'].split('/')[-1]

				print(lccn)


				url = "https://id.loc.gov/resources/works/relationships/contributorto/"
				params = {
					'label': 'http://id.loc.gov/authorities/names/' + lccn,
					'page': '0'
				}

				req = requests.get(url,params=params)
				titles_matched[title_author]['results'].append({
					'lccn':lccn,
					'hits': req.json()
					})

				# time.sleep(1)


				json.dump(titles_matched,open('../data/titles_matched.json','w'),indent=2)

