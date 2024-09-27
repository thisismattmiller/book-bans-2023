import requests
import json

titles_compiled = json.load(open('../data/titles_compiled.json'))

authors = {}

for t in titles_compiled:


	if titles_compiled[t]['creatorLCCN'] != None:

		if titles_compiled[t]['creatorLCCN'] not in authors:

			print(t)

			sparql = f"""
				SELECT ?item ?itemLabel ?award ?awardLabel
				WHERE
				{{
				  ?item wdt:P244 "{titles_compiled[t]['creatorLCCN']}". # Must be a cat
				  optional{{
					?item wdt:P166 ?award.
				  }}
				  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],mul,en". }} # Helps get the label in your language, if not, then default for all languages, then en language
				}}
			"""
			params = {
				'query' : sparql
			}

			headers = {
				'Accept' : 'application/json',
				'User-Agent': 'user:thisismattmiller - data scripts'
			}
			url = "https://query.wikidata.org/sparql"

			# print(sparql)
			r = requests.get(url, params=params, headers=headers)

			data = r.json()

			awards = []
			qid = None
			# did we get any results
			if len(data['results']['bindings']) > 0:
				for result in data['results']['bindings']:
					qid = result['item']['value'].split("/")[-1]
					if 'awardLabel' in result:
						awards.append({'label':result['awardLabel']['value'],'uri':result['award']['value'], })
					



			authors[titles_compiled[t]['creatorLCCN']] = {
				'qid':qid,
				'awards':awards
			}
			json.dump(authors,open('../data/authors.json','w'),indent=2)


# for t in titles_compiled:

# 	titles_compiled[t]['creatorHasAwards'] = None
# 	titles_compiled[t]['creatorWiki'] = None

# 	if titles_compiled[t]['creatorLCCN'] != None:

# 		titles_compiled[t]['creatorWiki'] = authors[titles_compiled[t]['creatorLCCN']]['qid']
# 		titles_compiled[t]['creatorHasAwards'] = len(authors[titles_compiled[t]['creatorLCCN']]['awards'])


# json.dump(titles_compiled,open('../data/titles_compiled.json','w'),indent=2)



