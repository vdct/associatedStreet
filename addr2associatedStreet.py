import sys,os
import xml.etree.ElementTree as ET
import fonctions as f

fnin  = raw_input('fichier parcelles-adresses : ')
dirout = 'fichiers_'+fnin.replace('.osm','')
if not os.path.exists(dirout):
	os.mkdir(dirout)
	
fnfantoir = raw_input('Fichier Fantoir : ')
dict_fantoir = f.rivoli_brut_vers_dict(fnfantoir)

xmldoc = ET.parse(fnin)

dict_global = {}
for w in xmldoc.iter('node'):
	addr_list = []
	for s in w:
		if s.get('k') == 'name' and s.get('v') != '*** PLUSIEURS ADRESSES ***' and len(s.get('v')) > 0:
			addr_list.append(s.get('v'))
		if s.get('k')[0:4] == 'addr' and len(s.get('v')) > 0:
			addr_list.append(s.get('v'))
	
		for a in addr_list:
			if a[0].isdigit():
				numAddr = a.partition(' ')[0]
				nomRue = a.partition(' ')[2]

				if nomRue not in dict_global:
					dict_global[nomRue] = {}
				if numAddr not in dict_global[nomRue]:
					dict_global[nomRue][numAddr] = [[w.get('lon'),w.get('lat')]]
				else :
					dict_global[nomRue][numAddr].append([w.get('lon'),w.get('lat')])
dict_final = {}
id_node = 0
for r in dict_global:
	dict_final[r] = {}
	for a in dict_global[r]:
		lon = 0
		lat = 0
		for c in dict_global[r][a]:
			lon = lon+float(c[0])
			lat = lat+float(c[1])
		lon = lon / len(dict_global[r][a])
		lat = lat / len(dict_global[r][a])
		id_node -= 1
		dict_final[r][a] = [str(id_node),str(lon),str(lat)]

nb_voies_total = 0
nb_voies_fantoir = 0
for r in dict_final:
	fout = open(dirout+'/'+r.replace(' ','_')+'.osm','w')
	fout.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
	fout.write("<osm version=\"0.6\" upload=\"false\" generator=\"addr2associatedStreet.py\">\n")
	for a in dict_final[r]:
		fout.write("	<node lat=\""+dict_final[r][a][2]+"\" lon=\""+dict_final[r][a][1]+"\" id=\""+dict_final[r][a][0]+"\">\n")
		fout.write("		<tag k=\"addr:housenumber\" v=\""+a+"\"/>\n")
		fout.write("	</node>\n")
#for r in dict_final:
	cle_fantoir = r.replace('-',' ')
	id_node -= 1
	fout.write("	<relation id=\""+str(id_node)+"\" action=\"modify\" visible=\"true\">\n")
	for a in dict_final[r]:
		fout.write("		<member type=\"node\" ref=\""+dict_final[r][a][0]+"\" role=\"house\"/>\n")
	fout.write("		<tag k=\"type\" v=\"associatedStreet\"/>\n")
	fout.write("		<tag k=\"name\" v=\""+r.title()+"\"/>\n")
	if cle_fantoir in dict_fantoir:
		fout.write("		<tag k=\"ref:FR:FANTOIR\" v=\""+dict_fantoir[cle_fantoir]+"\"/>\n")
		nb_voies_fantoir += 1
	else:
		print('Pas de rapprochement FANTOIR pour : '+r)
	fout.write("	</relation>\n")
	nb_voies_total +=1
	fout.write("</osm>")
	fout.close()

print("Nombre de relations creees : "+str(nb_voies_total))
print("Dont avec code FANTOIR     : "+str(nb_voies_fantoir)+" ("+str(int(nb_voies_fantoir*100/nb_voies_total))+"%)")
