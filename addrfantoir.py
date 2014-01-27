# coding: UTF-8
import sys,os
import urllib,urllib2
import xml.etree.ElementTree as ET
import fonctions as f

fnin  = raw_input('fichier adresses : ')
dirout = 'fichiers_'+fnin.replace('.osm','')
if not os.path.exists(dirout):
	os.mkdir(dirout)

code_insee = raw_input('Code INSEE : ')

fnfantoir = code_insee[0:2]+'0.txt'
if not os.path.exists(fnfantoir):
	print('Fichier FANTOIR "'+fnfantoir+'" absent du répertoire')
	print('Telechargeable ici : http://www.collectivites-locales.gouv.fr/mise-a-disposition-fichier-fantoir-des-voies-et-lieux-dits')
	print('Abandon')
	os._exit(0)
	
dict_fantoir = f.rivoli_dept_vers_dict(fnfantoir,code_insee)

dict_osm_insee = f.get_dict_osm_insee()

highway_rep = 'cache_highways'
if not os.path.exists(highway_rep):
	os.mkdir(highway_rep)
	
fnhighway = highway_rep+'/highways_'+code_insee+'.osm'
if not os.path.exists(fnhighway):
	highway_url = "http://overpass-api.de/api/interpreter?data=way%0A%20%20(area%3A"+str(3600000000+dict_osm_insee[code_insee])+")%0A%20%20%5B%22highway%22%5D%5B%22name%22%5D%3B%0Aout%20meta%3B"
	print("téléchargement des ways OSM...")
	try:
		resp = urllib2.urlopen(highway_url)
		fhighway = open(fnhighway,'wb')
		fhighway.write(resp.read())
		fhighway.close()
		print("ok")
	except urllib2.HTTPError:
		print('\n******* récupération KO ********')
		print('Abandon')
		os._exit(0)
		
print('mise en cache des voies...')

dict_ways_osm = {}
xmlways = ET.parse(fnhighway)
for w in xmlways.iter('way'):
	for t in w.iter('tag'):
		if t.get('k') == 'name':
			name_osm = t.get('v')

	name_norm = f.normalize(name_osm)
	if name_norm not in dict_ways_osm:
		dict_ways_osm[name_norm] = {'name':name_osm,'ids':[]}
	dict_ways_osm[name_norm]['ids'].append(w.get('id'))

fntmpkeys = 'cles_noms_de_voies.txt'
ftmpkeys = open(fntmpkeys,'w')
ftmpkeys.write('--noms de voies OSM normalisés (noms en base OSM)--\n')
for v in sorted(dict_ways_osm):
	ftmpkeys.write(v.encode('utf8')+' ('+dict_ways_osm[v]['name'].encode('utf8')+')\n')
ftmpkeys.write('---------------------\n')

print('mise en cache des adresses...')

xmldoc = ET.parse(fnin)
dict_nodes = {}
for w in xmldoc.iter('node'):
	dict_nodes[w.get('id')] = {'prop':{},'tag':{}}
	dict_nodes[w.get('id')]['prop']['lon'] = w.get('lon')
	dict_nodes[w.get('id')]['prop']['lat'] = w.get('lat')

	for s in w:
		dict_nodes[w.get('id')]['tag'][s.get('k')] = s.get('v')

dict_rels = {}
for w in xmldoc.iter('relation'):
	dict_rels[w.get('id')] = {}
	node_list = []
	for child in w:
		if child.tag == 'member':
			node_list.append(child.get('ref'))
		else:
			dict_rels[w.get('id')][child.get('k')] = child.get('v')
	dict_rels[w.get('id')]['nodes'] = node_list
		
nb_voies_total = 0
nb_voies_fantoir = 0
nb_voies_osm = 0
print('rapprochement...')
for r in dict_rels:
	rel_name = dict_rels[r]['name'];
	rel_name_norm = f.normalize(rel_name)
	
	fout = open(dirout+'/'+rel_name_norm.replace(' ','_')+'.osm','w')
	fout.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
	fout.write("<osm version=\"0.6\" upload=\"false\" generator=\"addrfantoir.py\">\n")

	min_id = 0
	for a in dict_rels[r]['nodes']:
		n = dict_nodes[a]
		fout.write("	<node lat=\""+n['prop']['lat']+"\" lon=\""+n['prop']['lon']+"\" id=\""+a+"\">\n")
		for k,v in n['tag'].iteritems():
			fout.write('		<tag k="'+k+'" v="'+v+'"/>\n')
		fout.write("	</node>\n")
		min_id = min(min_id,int(a))
		
	fout.write("	<relation id=\""+str(min_id - 1)+"\" action=\"modify\" visible=\"true\">\n")
	for a in dict_rels[r]['nodes']:
		fout.write("		<member type=\"node\" ref=\""+a+"\" role=\"house\"/>\n")
	street_name = rel_name.title()
	
	if rel_name_norm in dict_ways_osm:
		street_name =  dict_ways_osm[rel_name_norm]['name'].encode('utf8')
		for m in dict_ways_osm[rel_name_norm]['ids']:
			fout.write("		<member type=\"way\" ref=\""+m+"\" role=\"street\"/>\n")
		nb_voies_osm += 1
	else:
		ftmpkeys.write('Pas OSM     : '+rel_name_norm+' ('+rel_name+')\n')
	fout.write("		<tag k=\"type\" v=\"associatedStreet\"/>\n")
	fout.write("		<tag k=\"name\" v=\""+street_name+"\"/>\n")
	if rel_name_norm in dict_fantoir:
		fout.write("		<tag k=\"ref:FR:FANTOIR\" v=\""+dict_fantoir[rel_name_norm]+"\"/>\n")
		nb_voies_fantoir += 1
	else:
		ftmpkeys.write('Pas FANTOIR : '+rel_name.encode('utf8')+'\n')
	fout.write("	</relation>\n")
	nb_voies_total +=1
	fout.write("</osm>")
	fout.close()

ftmpkeys.close()

# numeros non places / ambigus
fout = open(dirout+'/numeros_ambigus_a_verifier.osm','w')
fout.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
fout.write("<osm version=\"0.6\" upload=\"false\" generator=\"addrfantoir.py\">\n")
nb_ambigu = 0
for a in dict_nodes:
	if 'fixme' in dict_nodes[a]['tag']:
		fout.write("	<node lat=\""+dict_nodes[a]['prop']['lat']+"\" lon=\""+dict_nodes[a]['prop']['lon']+"\" id=\""+a+"\">\n")
		for t in dict_nodes[a]['tag']:
			fout.write("		<tag k=\""+t+"\" v=\""+dict_nodes[a]['tag'][t]+"\"/>\n")
		fout.write("	</node>\n")
		nb_ambigu += 1

fout.write("</osm>")
fout.close()
	
print("Nombre de relations creees  : "+str(nb_voies_total))
print("     avec code FANTOIR      : "+str(nb_voies_fantoir)+" ("+str(int(nb_voies_fantoir*100/nb_voies_total))+"%)")
print("     avec rapprochement OSM : "+str(nb_voies_osm)+" ("+str(int(nb_voies_osm*100/nb_voies_total))+"%)")
if nb_ambigu > 0:
	print(str(nb_ambigu)+" points addresses à affecter manuellement a la bonne rue")
	print("Voir le fichier numeros_ambigus_a_verifier.osm")
