import csv
import requests
import json
import unicodedata
import string
import sys
import os
from thefuzz import fuzz



# OCLC_SEC = os.environ['OCLC_SEC']
# OCLC_TOKEN = os.environ['OCLC_TOKEN']

# response = requests.post(
# 	'https://oauth.oclc.org/token',
# 	data={"grant_type": "client_credentials", 'scope': ['wcapi']},
# 	auth=(OCLC_SEC, OCLC_TOKEN),
# )

# print(response.text)
# token = response.json()["access_token"]

# headers = {
# 	'accept': 'application/json',
# 	'Authorization': f'Bearer {token}'
# }
# OCLC_URL = 'https://americas.discovery.api.oclc.org/worldcat/search/v2/bibs'

output_titles = {}

def normalize_string(s):
    s = str(s)
    s = s.replace(".",'PERIOOOOOD')
    s = s.translate(str.maketrans('', '', string.punctuation))
    s = " ".join(s.split())
    s = s.lower()
    s = s.casefold()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    s = s.replace('perioooood',".")
    return s

def query_yes_no(question, default="no"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


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






found_count =0
for title_author in titles_matched:

	output_titles[title_author] = {
		'lc_works': None,
		'worldcat': None,
	}

	look_for_title = titles_matched[title_author]['title']
	look_for_normalized = normalize_string(titles_matched[title_author]['title'])


	found = False
	match = None
	for lccn_group in titles_matched[title_author]['results']:

		author_lccn = lccn_group['lccn']

		if lccn_group['hits']['results'] != None:

			if type(lccn_group['hits']['results']) is not list:
				lccn_group['hits']['results'] = [lccn_group['hits']['results']]

			for hit in lccn_group['hits']['results']:

				if look_for_normalized in normalize_string(hit['label']):
					# print('FOUND')
					# print(look_for_title,'in',hit)
					found = True
					match = {'author_lccn':author_lccn,'hit':hit}
					break

			if found != True:

				# modify the search title to remove the subtitle
				look_for_normalized = normalize_string(titles_matched[title_author]['title'].split(':')[0])
				for hit in lccn_group['hits']['results']:

					if look_for_normalized in normalize_string(hit['label']):
						# print('FOUND')
						# print(look_for_title,'in',hit)
						found = True
						match = {'author_lccn':author_lccn,'hit':hit}
						break

			if found == True:

				s1 = fuzz.partial_ratio(titles_matched[title_author]['author'] + ' ' + titles_matched[title_author]['title'], match['hit']['label'])
				s2 = fuzz.partial_ratio(titles_matched[title_author]['title'], match['hit']['label'])

				score = s1
				if s2>s1:
					score=s2

				# blank it out if its really bad and try another method
				if score <= 50:
					found=False
					match=None

				if found == True:
					output_titles[title_author]['lc_works'] = [match]


				break



	if found != True:

		# look into the works endpoint with the name though
		if 'work_hits' not in titles_matched[title_author] and 'worldcat' not in titles_matched[title_author]:

			url = "https://id.loc.gov/resources/works/suggest2/"
			params = {
				'q': normalize_string(titles_matched[title_author]['author'] + ' ' + titles_matched[title_author]['title']),
				'searchtype': 'keyword',
				'rdftype': 'Text'
			}


			req = requests.get(url,params=params)
			url = req.history[0].url if req.history else req.url
			res = req.json()
			if len(res['hits']) > 0:
				print(titles_matched[title_author]['author'])
				print(titles_matched[title_author]['title'])
				print(res['hits'])
				found = True
				titles_matched[title_author]['work_hits'] = res['hits']
				print("---------------")
				# json.dump(titles_matched,open('../data/titles_matched.json','w'),indent=2)
		else:
			found = True


	if found != True:

		# look into the works endpoint with the name though
		if 'work_hits' not in titles_matched[title_author]:

			url = "https://id.loc.gov/resources/works/suggest2/"
			params = {
				'q': normalize_string(titles_matched[title_author]['title']),
				'searchtype': 'keyword',
				'rdftype': 'Text'
			}


			req = requests.get(url,params=params)
			url = req.history[0].url if req.history else req.url
			print(url)
			res = req.json()
			if len(res['hits']) > 0 and len(res['hits']) <= 5:
				print("~~~~~~~~~~~~~~~~")
				print(titles_matched[title_author]['author'])
				print(titles_matched[title_author]['title'])
				# print(json.dumps(res['hits'],indent=2))
				print("---------------")

				if query_yes_no("Looks good?") == True:
					titles_matched[title_author]['work_hits'] = res['hits']
					# json.dump(titles_matched,open('../data/titles_matched.json','w'),indent=2)
					found = True

		else:
			found = True


	if found == False:
		if 'worldcat' not in titles_matched[title_author]:
			print(title_author)
			# ask worldcat for some data
			params = {
				'q' : f"au:{titles_matched[title_author]['author']} ti:{titles_matched[title_author]['title']}",
				'orderBy':'mostWidelyHeld',
				'limit' : 10

			}
			response = requests.get(OCLC_URL,params=params,headers=headers)
			urlout = response.history[0].url if response.history else response.url
			print(urlout)
			found = True
			titles_matched[title_author]['worldcat'] = response.json()
			json.dump(titles_matched,open('../data/titles_matched.json','w'),indent=2)
		else:
			found = True



	if 'work_hits' in titles_matched[title_author]:
		for hit in titles_matched[title_author]['work_hits']:

			s1 = fuzz.ratio(titles_matched[title_author]['author'] + ' ' + titles_matched[title_author]['title'], hit['aLabel'])
			s2 = fuzz.ratio(titles_matched[title_author]['title'], hit['aLabel'])

			score = s1
			if s2>s1:
				score=s2
			# print("\t",score,hit['aLabel'])
			hit['score'] = score

		matches_sorted_by_score = sorted(titles_matched[title_author]['work_hits'], key=lambda d: d['score'],reverse=True)
		best = []
		best_score = 0
		for hit in matches_sorted_by_score:
			if hit['score'] >= best_score:
				best.append(hit)
				best_score=hit['score']
		
		output_titles[title_author]['lc_works'] = best




	if 'worldcat' in titles_matched[title_author]:

		if 'bibRecords' in titles_matched[title_author]['worldcat']:
			print("-----------")
			print(title_author)

			for hit in titles_matched[title_author]['worldcat']['bibRecords']:

				oclc_title=hit['title']['mainTitles'][0]['text'].split("/")[0]
				oclc_name=''

				if 'creators' in hit['contributor']:
					for c in hit['contributor']['creators']:
						if c['isPrimary']:
							oclc_name = c['firstName']['text']
							if 'secondName' in c:
								if 'text' in c['secondName']:
									oclc_name = c['secondName']['text'] + ', ' + oclc_name


				title_score = fuzz.ratio(titles_matched[title_author]['title'],oclc_title)

				name_score = fuzz.ratio(titles_matched[title_author]['author'],oclc_name)

				total_score = title_score + name_score
				hit['score'] = total_score



			worldcat_matches_sorted_by_score = sorted(titles_matched[title_author]['worldcat']['bibRecords'], key=lambda d: d['score'],reverse=True)


			best_worldcat = []
			best_worldcat_score = 0
			for hit in worldcat_matches_sorted_by_score:
				# print(hit)
				if hit['score'] >= best_worldcat_score:
					best_worldcat.append(hit)
					best_worldcat_score=hit['score']


			for hit in best_worldcat:
				oclc_title=hit['title']['mainTitles'][0]['text'].split("/")[0]
				oclc_name=''
				if 'creators' in hit['contributor']:
					for c in hit['contributor']['creators']:
						if c['isPrimary']:
							oclc_name = c['firstName']['text']
							if 'secondName' in c:
								if 'text' in c['secondName']:
									oclc_name = c['secondName']['text'] + ', ' + oclc_name



				print('\t',hit['score'],oclc_name,oclc_title)
			print(title_author, len(best_worldcat))
			# print(json.dumps(best,indent=2))
			output_titles[title_author]['worldcat'] = best_worldcat


	if found == False:
		print("Not Found")
		print(title_author)
		print(look_for_normalized)
		print("---------------")
		# print(titles_matched[title_author])
	else:
		found_count=found_count+1


# json.dump(titles_matched,open('../data/titles_matched.json','w'),indent=2)

print(found_count, len(titles_matched))
print(len(output_titles))
json.dump(output_titles,open('../data/titles_data.json','w'),indent=2)


		# if title_author not in titles_matched:

		# 	print(row['author'], row['title'])
		# 	titles_matched[title_author] = {
		# 		'author': row['author'],
		# 		'title': row['title'],
		# 		'results': []
		# 	}

		# 	for hit in authors_matches[row['author']]['matches']['hits']:

		# 		lccn = hit['uri'].split('/')[-1]

		# 		print(lccn)


		# 		url = "https://id.loc.gov/resources/works/relationships/contributorto/"
		# 		params = {
		# 			'label': 'http://id.loc.gov/authorities/names/' + lccn,
		# 			'page': '0'
		# 		}

		# 		req = requests.get(url,params=params)
		# 		titles_matched[title_author]['results'].append({
		# 			'lccn':lccn,
		# 			'hits': req.json()
		# 			})

		# 		time.sleep(1)


				# json.dump(titles_matched,open('../data/titles_matched.json','w'),indent=2)

