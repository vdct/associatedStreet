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
	print('Abandon')
	os._exit(0)
	
dict_fantoir = f.rivoli_dept_vers_dict(fnfantoir,code_insee)

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
for r in dict_rels:
	rel_name = dict_rels[r]['name'];
	fout = open(dirout+'/'+rel_name.replace(' ','_')+'.osm','w')
	fout.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
	fout.write("<osm version=\"0.6\" upload=\"false\" generator=\"addrfantoir.py\">\n")

	min_id = 0
	for a in dict_rels[r]['nodes']:
		n = dict_nodes[a]
		fout.write("	<node lat=\""+n['prop']['lat']+"\" lon=\""+n['prop']['lon']+"\" id=\""+a+"\">\n")
		fout.write("		<tag k=\"addr:housenumber\" v=\""+n['tag']['addr:housenumber']+"\"/>\n")
		fout.write("	</node>\n")
		min_id = min(min_id,int(a))
		
	cle_fantoir = rel_name.replace('-',' ')

	fout.write("	<relation id=\""+str(min_id - 1)+"\" action=\"modify\" visible=\"true\">\n")
	for a in dict_rels[r]['nodes']:
		fout.write("		<member type=\"node\" ref=\""+a+"\" role=\"house\"/>\n")
	street_name = rel_name.title()

	fout.write("		<tag k=\"type\" v=\"associatedStreet\"/>\n")
	fout.write("		<tag k=\"name\" v=\""+street_name+"\"/>\n")
	if cle_fantoir in dict_fantoir:
		fout.write("		<tag k=\"ref:FR:FANTOIR\" v=\""+dict_fantoir[cle_fantoir]+"\"/>\n")
		nb_voies_fantoir += 1
	else:
		print('Pas de rapprochement FANTOIR pour : '+rel_name)
	fout.write("	</relation>\n")
	nb_voies_total +=1
	fout.write("</osm>")
	fout.close()

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
	
print("Nombre de relations creees : "+str(nb_voies_total))
print("Dont avec code FANTOIR     : "+str(nb_voies_fantoir)+" ("+str(int(nb_voies_fantoir*100/nb_voies_total))+"%)")
if nb_ambigu > 0:
	print(str(nb_ambigu)+" points addresses à affecter manuellement a la bonne rue")
	print("Voir le fichier numeros_ambigus_a_verifier.osm")