import requests
import json
import csv

import os.path

import xml.etree.ElementTree as ET

titles_data = json.load(open('../data/titles_data.json'))
titles_compiled = {}


for t in titles_data:

	titles_compiled[t] = {
		'lcBib':None,
		'creatorLabel':None,
		'creatorLCCN': None,
		'genre':[],
		'subjects':[],
		'LCCN': None,
		'OCLC':None,
		'ISBN':[],
		'pubDate':None,
		'states': [],
		'status': []


	}

	if titles_data[t]['lc_works'] != None:
		
		for hit in titles_data[t]['lc_works']:
			uri = None
			if 'uri' in hit:
				uri = hit['uri']
			else:
				uri = hit['hit']['uri']


			work_id = uri.split("/")[-1]


			if os.path.isfile(f'../data/lc_data/{work_id}.json'):
				continue

			print(work_id)
			work_req = requests.get(f'{uri}.json')
			work_data = work_req.json()
			instance_uri = uri.replace('/works/','/instances/')

			instance_req = requests.get(f'{instance_uri}.json')
			instance_data = instance_req.json()

			out = {
				'work': work_data,
				'instance':instance_data
			}
			json.dump(out,open(f'../data/lc_data/{work_id}.json','w'),indent=2)


for t in titles_data:

	if titles_data[t]['lc_works'] != None:

		author_lccn = None
		author_label = None
		author_uri = None

		for hit in titles_data[t]['lc_works']:
			uri = None
			if 'uri' in hit:
				uri = hit['uri']
			else:
				uri = hit['hit']['uri']
				author_lccn = hit['author_lccn']
				author_uri = f'http://id.loc.gov/rwo/agents/{author_lccn}'

			work_id = uri.split("/")[-1]


			data = json.load(open(f'../data/lc_data/{work_id}.json'))
			
			if author_lccn == None:
				for g in data['work']:
					if '@type' in g:
						if 'http://id.loc.gov/ontologies/bibframe/PrimaryContribution' in g['@type']:
							author_lccn = g['http://id.loc.gov/ontologies/bibframe/agent'][0]['@id'].split("/")[-1]
							author_uri = g['http://id.loc.gov/ontologies/bibframe/agent'][0]['@id']

			for g in data['work']:
				if '@id' in g:
					if g['@id'] == author_uri:
						author_label = g['http://www.w3.org/2000/01/rdf-schema#label'][0]['@value']

		if author_lccn != None:
			if '_:' in author_lccn: 
				author_lccn = None

		if author_lccn == None and author_label == None:

			for g in data['work']:
				if '@type' in g:
					if 'http://id.loc.gov/ontologies/bibframe/Contribution' in g['@type']:
						author_lccn = g['http://id.loc.gov/ontologies/bibframe/agent'][0]['@id'].split("/")[-1]
						author_uri = g['http://id.loc.gov/ontologies/bibframe/agent'][0]['@id']

			for g in data['work']:
				if '@id' in g:
					if g['@id'] == author_uri:
						author_label = g['http://www.w3.org/2000/01/rdf-schema#label'][0]['@value']
						break


		titles_compiled[t]['creatorLCCN'] = author_lccn
		titles_compiled[t]['creatorLabel'] = author_label
		titles_compiled[t]['lcBib'] = work_id



		subjects = []
		genre_form = []
		for hit in titles_data[t]['lc_works']:
			uri = None
			if 'uri' in hit:
				uri = hit['uri']
			else:
				uri = hit['hit']['uri']
				author_lccn = hit['author_lccn']
				author_uri = f'http://id.loc.gov/rwo/agents/{author_lccn}'

			work_id = uri.split("/")[-1]


			data = json.load(open(f'../data/lc_data/{work_id}.json'))
			for g in data['work']:
				if 'http://www.loc.gov/mads/rdf/v1#isMemberOfMADSScheme' in g:
					if 'http://id.loc.gov/authorities/' in g['http://www.loc.gov/mads/rdf/v1#isMemberOfMADSScheme'][0]['@id']:
						

						label = g['http://www.loc.gov/mads/rdf/v1#authoritativeLabel'][0]['@value']
						lcsh_uris = []
						if 'http://www.loc.gov/mads/rdf/v1#componentList' in g:
							for lcsh_uri in g['http://www.loc.gov/mads/rdf/v1#componentList'][0]['@list']:
								if '_:' in lcsh_uri['@id']:
									lcsh_uris.append(None)
								else:
									lcsh_uris.append(lcsh_uri['@id'])

						type = "lcsh"
						if 'childrensSubjects' in g['http://www.loc.gov/mads/rdf/v1#isMemberOfMADSScheme'][0]['@id']:
							type = 'clcsh'

						subjects.append({'label':label, 'uri':lcsh_uris, 'type': type})

				if 'http://id.loc.gov/ontologies/bibframe/Topic' in g['@type'] and 'http://www.loc.gov/mads/rdf/v1#ComplexSubject' not in g['@type']:
					if 'id.loc.gov/authorities' in g['@id']:
							
						lc_uri = g['@id']
						label = None

						try:
							label = g['http://www.loc.gov/mads/rdf/v1#authoritativeLabel'][0]['@value']
						except:
							pass
						try:
							label = g['http://www.w3.org/2000/01/rdf-schema#label'][0]['@value']
						except:
							pass

						type = "lcsh"
						if 'childrensSubjects' in lc_uri:
							type = 'clcsh'

						if label != None:
							subjects.append({'label':label, 'uri':lc_uri, 'type': type})


						'http://id.loc.gov/authorities/childrensSubjects'
					elif '_:' in g['@id'] and 'http://www.loc.gov/mads/rdf/v1#isMemberOfMADSScheme' in g:
						if 'childrensSubjects' in g['http://www.loc.gov/mads/rdf/v1#isMemberOfMADSScheme'][0]['@id']:

							lc_uri = None
							label = None

							try:
								label = g['http://www.loc.gov/mads/rdf/v1#authoritativeLabel'][0]['@value']
							except:
								pass
							try:
								label = g['http://www.w3.org/2000/01/rdf-schema#label'][0]['@value']
							except:
								pass

							if label != None:
								subjects.append({'label':label, 'uri':lc_uri, 'type': 'clcsh'})


					else:
						pass
						# FAST / OTHER HERE


				
				if 'http://id.loc.gov/ontologies/bibframe/GenreForm' in g['@type']:
					lc_uri = g['@id']
					label = None

					try:
						label = g['http://www.loc.gov/mads/rdf/v1#authoritativeLabel'][0]['@value']
					except:
						pass
					try:
						label = g['http://www.w3.org/2000/01/rdf-schema#label'][0]['@value']
					except:
						pass

					if 'id.loc.gov' in lc_uri:
						genre_form.append({'label':label, 'uri':lc_uri})



		titles_compiled[t]['subjects'] = subjects
		titles_compiled[t]['genre'] = genre_form




		# print(work_id,genre_form)
		isbns = []
		lccns = []
		pubdate = None
		for g in data['instance']:
			if 'http://id.loc.gov/ontologies/bibframe/Isbn' in g['@type']:

				if 'http://id.loc.gov/ontologies/bibframe/status' not in g:
					isbns.append(g['http://www.w3.org/1999/02/22-rdf-syntax-ns#value'][0]['@value'])

			if 'http://id.loc.gov/ontologies/bibframe/Lccn' in g['@type']:

				if 'http://id.loc.gov/ontologies/bibframe/status' not in g:
					lccns.append(g['http://www.w3.org/1999/02/22-rdf-syntax-ns#value'][0]['@value'])


			if "http://id.loc.gov/ontologies/bibframe/ProvisionActivity" in  g['@type']:
				if 'http://id.loc.gov/ontologies/bibframe/date' in g:
					pubdate = g['http://id.loc.gov/ontologies/bibframe/date'][0]['@value'].split('/')[0]

		titles_compiled[t]['pubDate'] = pubdate
		titles_compiled[t]['LCCN'] = lccns
		titles_compiled[t]['ISBN'] = isbns

	elif titles_data[t]['worldcat'] != None:

		subjects = []
		pubdate = []
		subjects_labels =[]
		isbns = []
		genre_form = []
		oclcnum = None


		for wc in titles_data[t]['worldcat']:

			oclcnum = wc['identifier']['oclcNumber']

			data = ET.parse(f'../data/oclc/{oclcnum}.xml')
			root = data.getroot()
			for datafield in root.findall("{http://www.loc.gov/MARC21/slim}datafield"):
				if datafield.attrib['tag'] == '650' and (datafield.attrib['ind2'] == '1' or datafield.attrib['ind2'] == '0'):
					for subfield in datafield:
						if subfield.attrib['code'] != 'v':

							type = 'lcsh'
							if datafield.attrib['ind2'] == '1':
								type='clcsh'

							if subfield.text not in subjects_labels:
								subjects_labels.append(subfield.text)
								subjects.append({'label':subfield.text,'uri':None,'type':type})

							


			if 'date' in wc:
				if 'machineReadableDate' in wc['date']:
					pubdate.append(int(wc['date']['machineReadableDate']))
				elif 'createDate' in wc['date']:
					pubdate.append(int(wc['date']['createDate'][0:3]))
				else:
					print("NO TDATRE")
					print(wc['date'])

			if 'isbns' in wc['identifier']:
				
				isbns = isbns + wc['identifier']['isbns']


			if 'subjects' in wc:
				for s in wc['subjects']:
					if 'subjectType' in s:
						if s['subjectType'] == 'genreFormTerm' and ('LC' in s['vocabulary'] or 'lcgft' in s['vocabulary'] ):

							genre_form.append({'label':s['subjectName']['text'], 'uri':None})






		pubdate=min(pubdate)
		isbns=list(set(isbns))


		titles_compiled[t]['subjects'] = subjects
		titles_compiled[t]['genre'] = genre_form
		titles_compiled[t]['pubDate'] = pubdate
		titles_compiled[t]['ISBN'] = isbns
		titles_compiled[t]['OCLC'] = oclcnum



	titles_compiled[t]['subjectsComponents']=[]

	for s in titles_compiled[t]['subjects']:
		if s['label'][-1] == '.':			
			s['label'] = s['label'][:-1]

	for s in titles_compiled[t]['subjects']:
		titles_compiled[t]['subjectsComponents'] = titles_compiled[t]['subjectsComponents'] + s['label'].split("--")


	titles_compiled[t]['subjectsComponents']=list(set(titles_compiled[t]['subjectsComponents']))
	for sh in ['Fiction','Large type books','Juvenile fiction','Graphic novels','Comic books, strips, etc']:
		if sh in titles_compiled[t]['subjectsComponents']:
			titles_compiled[t]['subjectsComponents'].remove(sh)



# load in the org data

with open('../data/pen_2022-2023_book_bans_by_author_title.csv') as infile:

	reader = csv.DictReader(infile)
	
	for row in reader:

		title_author = row['author'] + ' ' + row['title']

		titles_compiled[title_author]['title'] = row['title']
		titles_compiled[title_author]['author'] = row['author']
		titles_compiled[title_author]['secondary_author'] = row['secondary_author']
		titles_compiled[title_author]['illustrator'] = row['illustrator']
		titles_compiled[title_author]['translators'] = row['translators']
		titles_compiled[title_author]['series'] = row['series']

		if row['state'] not in titles_compiled[title_author]['states']:
			titles_compiled[title_author]['states'].append(row['state'])

		titles_compiled[title_author]['status'].append({
				'state':row['state'],
				'date_ban':row['date_ban'],
				'ban_status':row['ban_status'],
				'challenge_origin':row['challenge_origin'],
				'district':row['district']
		})

		if len(titles_compiled[title_author]['states']) > 1:
			print(titles_compiled[title_author])







json.dump(titles_compiled,open('../data/titles_compiled.json','w'),indent=2)
