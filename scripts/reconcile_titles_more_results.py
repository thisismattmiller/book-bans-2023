import csv
import requests
import time
import json
import math

titles_matched = {}

try:
	titles_matched = json.load(open('../data/titles_matched.json'))
except:
	pass


for key in titles_matched:
	# print(titles_matched[key])
	# if type(titles_matched[key]['hits']['results']) is not list:
	# 	lccn_group['hits']['results'] = [lccn_group['hits']['results']]
	for results_group in titles_matched[key]['results']:

		if results_group['hits'] and results_group['hits']['summary']:

			if results_group['hits']['summary']['total'] > 50 and results_group['hits']['summary']['total'] < 1001:
				total_pages = math.ceil(results_group['hits']['summary']['total'] / 50)
				# print(results_group['hits']['summary'], total_pages)
				print(results_group['hits']['results'])



				for count in range(1,total_pages):

					url = "https://id.loc.gov/resources/works/relationships/contributorto/"
					params = {
						'label': 'http://id.loc.gov/authorities/names/' + results_group['lccn'],
						'page': count
					}				
					x = 'http://id.loc.gov/authorities/names/' + results_group['lccn']
					y = count	
					print(f"https://id.loc.gov/resources/works/relationships/contributorto/?label={x}&page={y}")
					req = requests.get(url,params=params)
					res = req.json()
					if res['results'] != None:

						if type(res['results']) is not list:
							res['results'] = [res['results']]


						results_group['hits']['results']=results_group['hits']['results']+res['results']


					json.dump(titles_matched,open('../data/titles_matched_all.json','w'),indent=2)

json.dump(titles_matched,open('../data/titles_matched_all.json','w'),indent=2)

# with open('../data/pen_2022-2023_book_bans_by_author_title.csv') as infile:

# 	reader = csv.DictReader(infile)
	
# 	for row in reader:

# 		title_author = row['author'] + ' ' + row['title']

# 		if title_author not in titles_matched:

# 			print(row['author'], row['title'])
# 			titles_matched[title_author] = {
# 				'author': row['author'],
# 				'title': row['title'],
# 				'results': []
# 			}

# 			for hit in authors_matches[row['author']]['matches']['hits']:

# 				lccn = hit['uri'].split('/')[-1]

# 				print(lccn)


# 				url = "https://id.loc.gov/resources/works/relationships/contributorto/"
# 				params = {
# 					'label': 'http://id.loc.gov/authorities/names/' + lccn,
# 					'page': '0'
# 				}

# 				req = requests.get(url,params=params)
# 				titles_matched[title_author]['results'].append({
# 					'lccn':lccn,
# 					'hits': req.json()
# 					})

# 				time.sleep(1)


# 				json.dump(titles_matched,open('../data/titles_matched.json','w'),indent=2)

