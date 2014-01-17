import sys,os
import xml.etree.ElementTree as ET

fnin  = raw_input('fichier parcelles-adresses : ')
fnout = 'test.osm'

xmldoc = ET.parse(fnin)

dict_global = {}
for w in xmldoc.iter('node'):
	addr_list = []
	for s in w:
		if s.get('k') == 'name' and s.get('v') != '*** PLUSIEURS ADRESSES ***' and s.get('v') != '':
			addr_list.append(s.get('v'))
		if s.get('k')[0:4] == 'addr':
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

fout = open(fnout,'w')
fout.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
fout.write("<osm version=\"0.6\" upload=\"false\" generator=\"addr2associatedStreet.py\">\n")

for r in dict_final:
	for a in dict_final[r]:
		fout.write("	<node lat=\""+dict_final[r][a][2]+"\" lon=\""+dict_final[r][a][1]+"\" id=\""+dict_final[r][a][0]+"\">\n")
		fout.write("		<tag k=\"addr:housenumber\" v=\""+a+"\"/>\n")
		fout.write("	</node>\n")
for r in dict_final:
	id_node -= 1
	fout.write("	<relation id=\""+str(id_node)+"\" action=\"modify\" visible=\"true\">\n")
	for a in dict_final[r]:
		fout.write("		<member type=\"node\" ref=\""+dict_final[r][a][0]+"\" role=\"house\"/>\n")
	fout.write("		<tag k=\"type\" v=\"associatedStreet\"/>\n")
	fout.write("		<tag k=\"name\" v=\""+r.title()+"\"/>\n")
	fout.write("	</relation>\n")
fout.write("</osm>")
