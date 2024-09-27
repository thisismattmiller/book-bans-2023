import requests
import json
import csv
from collections import OrderedDict
import os.path


titles_compiled = json.load(open('../data/titles_compiled.json'))

authors = {}



all_states = []
all_subject_components = []
all_subject_complex = []
for t in titles_compiled:

	all_states = all_states + titles_compiled[t]['states']
	all_subject_components = all_subject_components + titles_compiled[t]['subjectsComponents']
	for s in titles_compiled[t]['subjects']:
		all_subject_complex = all_subject_complex + [s['label']]


all_states=sorted(list(set(all_states)))
all_subject_components=sorted(list(set(all_subject_components)))


json.dump(all_subject_components,open('../data/export_subject_components.json','w'),indent=2)


print(all_states)
print(all_subject_components)
all_subject_components_count = {}
for s in all_subject_components:
	all_subject_components_count[s] = 0

all_subject_complex_count = {}
for s in all_subject_complex:
	all_subject_complex_count[s] = 0

for t in titles_compiled:
	for s in titles_compiled[t]['subjectsComponents']:
		all_subject_components_count[s] = all_subject_components_count[s] + len(titles_compiled[t]['status'])

	for s in titles_compiled[t]['subjects']:
		all_subject_complex_count[s['label']] = all_subject_complex_count[s['label']] + len(titles_compiled[t]['status'])



all_subject_components_count = dict(sorted(all_subject_components_count.items(), key=lambda item: item[1], reverse=True))
all_subject_complex_count = dict(sorted(all_subject_complex_count.items(), key=lambda item: item[1], reverse=True))


print(all_subject_components_count)
print(all_subject_complex_count)





all_subject_components_count_list = []
for k in all_subject_components_count:
	print(k)
	all_subject_components_count_list.append([k,all_subject_components_count[k]])


all_subject_complex_count_list = []
for k in all_subject_complex_count:
	print(k)
	all_subject_complex_count_list.append([k,all_subject_complex_count[k]])






json.dump(all_subject_components_count_list,open('../data/export_subject_components.json','w'))
json.dump(all_subject_complex_count_list,open('../data/export_subject_complex.json','w'))


states_top_subjects = {}
for s in all_states:
	states_top_subjects[s] = {}

print(states_top_subjects)

for t in titles_compiled:
	for s in titles_compiled[t]['subjectsComponents']:

		for state in states_top_subjects:
			if state in titles_compiled[t]['states']:
				if s not in states_top_subjects[state]:
					states_top_subjects[state][s] = 0

				for status in titles_compiled[t]['status']:
					if status['state'] == state:
						states_top_subjects[state][s] = states_top_subjects[state][s] + 1

for state in states_top_subjects:
	states_top_subjects[state] = dict(sorted(states_top_subjects[state].items(), key=lambda item: item[1], reverse=True))

states_top_subjects_list = {}
for state in states_top_subjects:
	if state not in states_top_subjects_list:
		states_top_subjects_list[state] = []

	for subj in states_top_subjects[state]:
		states_top_subjects_list[state].append([subj, states_top_subjects[state][subj]])



json.dump(states_top_subjects_list,open('../data/export_state_subjects.json','w'))



print(all_states)



dates = {}
for t in titles_compiled:
	# if 'pubDate' in 
	if titles_compiled[t]['pubDate'] != None:
		try:
			date=int(titles_compiled[t]['pubDate'])
		except:
			continue

		if date not in dates:
			dates[date] = 0

		dates[date]=dates[date]+1

sorted_dates = dict(sorted(dates.items()))
print(sorted_dates)

json.dump(sorted_dates,open('../data/export_dates.json','w'))


with open("../data/export_dates.csv",'w') as out:


	writer = csv.writer(out)
	writer.writerow(['year','count'])	
	for d in sorted_dates:
		writer.writerow([d,sorted_dates[d]])


wikidata = json.load(open('../data/authors.json','r'))

print(wikidata)
authors = {}
for t in titles_compiled:
	if titles_compiled[t]['creatorHasAwards'] != None:
		if titles_compiled[t]['creatorHasAwards'] > 0:

			if titles_compiled[t]['creatorLCCN'] not in authors:
				authors[titles_compiled[t]['creatorLCCN']] = {
					'label': titles_compiled[t]['creatorLabel'],
					'awards': [],
					'titles': [titles_compiled[t]['title']],
					'bans':len(titles_compiled[t]['status'])

				}
			else:
				authors[titles_compiled[t]['creatorLCCN']]['bans']=authors[titles_compiled[t]['creatorLCCN']]['bans']+len(titles_compiled[t]['status'])
				authors[titles_compiled[t]['creatorLCCN']]['titles'].append(titles_compiled[t]['title'])



for lccn in authors:
	for a in wikidata[lccn]['awards']:
		authors[lccn]['awards'].append(a)
		authors[lccn]['qid'] = wikidata[lccn]['qid']


json.dump(authors,open('../data/awards.json','w'))

rows = []
for t in titles_compiled:

	for status_item in titles_compiled[t]['status']:


		genres = []
		genres_uri=[]
		subjects = []
		subjects_uri=[]

		for g in titles_compiled[t]['genre']:
			genres.append(g['label'])
			if g['uri'] != None:
				genres_uri.append(g['uri'])

		for s in titles_compiled[t]['subjects']:

			subjects.append(s['label'])
			if type(s['uri']) is list:
				for u in s['uri']:
					if u != None:
						subjects_uri.append(u)
			else:
				if s['uri'] != None:
					subjects_uri.append(s['uri'])


		if titles_compiled[t]['LCCN'] == None:
			titles_compiled[t]['LCCN'] = []


		genres=list(set(genres))
		genres_uri=list(set(genres_uri))
		subjects=list(set(subjects))
		subjects_uri=list(set(subjects_uri))

		marc_file=None
		if titles_compiled[t]['lcBib'] != None:
			if os.path.isfile('../data/marc/'+titles_compiled[t]['lcBib'] + '.xml'):
				marc_file = f"https://thisismattmiller.s3.amazonaws.com/banned-metadata-2023/{titles_compiled[t]['lcBib']}.xml"
			
				

		r = {
			'title': titles_compiled[t]['title'],
			'author': titles_compiled[t]['author'],
			'secondary_author': titles_compiled[t]['secondary_author'],
			'illustrator': titles_compiled[t]['illustrator'],
			'translators': titles_compiled[t]['translators'],
			'series': titles_compiled[t]['series'],
			'lc_bib': titles_compiled[t]['lcBib'],
			'naf_label': titles_compiled[t]['creatorLabel'],
			'naf_lccn': titles_compiled[t]['creatorLCCN'],
			'genre': "|".join(genres),
			'genre_uris': "|".join(genres_uri),
			'subject': "|".join(subjects),
			'subject_uris': "|".join(subjects_uri),
			'lccn': "|".join(titles_compiled[t]['LCCN']),
			'oclc': titles_compiled[t]['OCLC'],
			'isbn': "|".join(titles_compiled[t]['ISBN']),
			'date': titles_compiled[t]['pubDate'],
			'creator_has_awards': titles_compiled[t]['creatorHasAwards'],
			'creator_wiki': titles_compiled[t]['creatorWiki'],
		    "state": status_item['state'],
		    "date_ban": status_item['date_ban'],
		    "ban_status": status_item['ban_status'],
		    "challenge_origin": status_item['challenge_origin'],
		    "district": status_item['district'],
		    "marc_file": marc_file

		}


		rows.append(r)


with open('../data/combined.csv','w') as outfile:

	writer = csv.DictWriter(outfile, fieldnames=OrderedDict([
		('title',None),
		('author',None),
		('secondary_author',None),
		('illustrator',None),
		('translators',None),
		('series',None),
		('lc_bib',None),
		('naf_label',None),
		('naf_lccn',None),
		('genre',None),
		('genre_uris',None),
		('subject',None),
		('subject_uris',None),
		('lccn',None),
		('oclc',None),
		('isbn',None),
		('date',None),
		('creator_has_awards',None),
		('creator_wiki',None),
	    ("state",None),
	    ("date_ban",None),
	    ("ban_status",None),
	    ("challenge_origin",None),
	    ("district",None),
	    ("marc_file",None)

	    

	]))

	writer.writeheader()

	for row in rows:
		writer.writerow(row)






