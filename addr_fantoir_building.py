# coding: UTF-8
import psycopg2
from pg_connexion import get_pgc
import urllib,urllib2
import sys,os,gc,time
import xml.etree.ElementTree as ET

debut_total = time.time()

class Dicts:
	def __init__(self):
		self.lettre_a_lettre = {}
		self.fantoir = {}
		self.osm_insee = {}
		self.abrev_type_voie = {}
		self.abrev_titres = {}
		self.chiffres = []
		self.chiffres_romains = []
		self.mot_a_blanc = []
		self.abrev_titres = {}
		self.noms_voies = {}
	def load_lettre_a_lettre(self):
		self.lettre_a_lettre = {'A':[u'Â',u'À'],
						'C':[u'Ç'],
						'E':[u'È',u'Ê',u'É',u'Ë'],
						'I':[u'Ï',u'Î'],
						'O':[u'Ö',u'Ô'],
						'U':[u'Û',u'Ü']}
	def load_fantoir(self,insee):
		fndep = 'fantoir/'+insee[0:2]+'0.txt'
		if not os.path.exists(fndep):
			print('Fichier FANTOIR "'+fndep+'" absent du répertoire')
			print('Telechargeable ici : http://www.collectivites-locales.gouv.fr/mise-a-disposition-fichier-fantoir-des-voies-et-lieux-dits')
			print('Abandon')
			os._exit(0)		
		h = open(fndep,'r')
		dictFantoir = {}
		insee_com = insee[2:5]
		for l in h:
		# hors commune
			if l[3:6] != insee_com:
				continue
		# enregistrement != Voie
			if l[108:109] == ' ':
				continue
		# voie annulée
			if l[73:74] != ' ':
				continue
			cle = ' '.join((l[11:15].rstrip().lstrip()+' '+l[15:41].rstrip().lstrip()).replace('-',' ').lstrip().split())
			cle = normalize(cle)
			self.fantoir[cle] = l[0:2]+l[3:11]
			self.add_voie('fantoir',cle)
		h.close()
	def load_chiffres(self):
		self.chiffres = [	['0','ZERO'],
							['1','UN'],
							['2','DEUX'],
							['3','TROIS'],
							['4','QUATRE'],
							['5','CINQ'],
							['6','SIX'],
							['7','SEPT'],
							['8','HUIT'],
							['9','NEUF'],
							[' DIX ',' UNZERO '],
							[' ONZE ',' UNUN '],
							[' DOUZE ',' UNDEUX ']]
	def load_mot_a_blanc(self):
		self.mot_a_blanc = ['DE LA',
							'DU',
							'DES',
							'LE',
							'LA',
							'LES',
							'DE',
							'D']
	def load_abrev_titres(self):
		self.abrev_titres = [['MARECHAL','MAL'],
							['PRESIDENT','PDT'],
							['GENERAL','GAL'],
							['COMMANDANT','CDT'],
							['CAPITAINE','CAP'],
							['REGIMENT','REGT'],
							['SAINTE','STE'],
							['SAINT','ST']]
	def load_chiffres_romains(self):
		self.chiffres_romains = {	'XXIII':'DEUXTROIS',
									'XXII' :'DEUXDEUX',
									'XXI'  :'DEUXUN',
									'XX'   :'DEUXZERO',
									'XIX'  :'UNNEUF',
									'XVIII':'UNHUIT',
									'XVII' :'UNSEPT',
									'XVI'  :'UNSIX',
									'XV'   :'UNCINQ',
									'XIV'  :'UNQUATRE',
									'XIII' :'UNTROIS',
									'XII'  :'UNDEUX',
									'XI'   :'UNUN',
									'X'    :'UNZERO',
									'IX'   :'NEUF',
									'VIII' :'HUIT',
									'VII'  :'SEPT',
									'VI'   :'SIX',
									'V'    :'CINQ',
									'IV'   :'QUATRE',
									'III'  :'TROIS',
									'II'   :'DEUX',
									'I'    :'UN'}
	def load_abrev_type_voie(self):
		fn = 'abrev_type_voie.txt'
		f = open(fn)
		for l in f:
			c = (l.splitlines()[0]).split('\t')
			self.abrev_type_voie[c[0]] = c[1]
		f.close()
	def load_osm_insee(self):
		finsee = open('osm_id_ref_insee.csv','r')
		for e in finsee:
			c = (e.splitlines()[0]).split(',')
			self.osm_insee[str(c[1])] = int(c[0])
		finsee.close()
	def load_all(self,code_insee_commune):
		self.load_lettre_a_lettre()
		self.load_abrev_type_voie()
		self.load_abrev_titres()
		self.load_chiffres()
		self.load_chiffres_romains()
		self.load_mot_a_blanc()
		self.load_osm_insee()
		self.load_fantoir(code_insee_commune)
	def add_voie(self,origine,nom):
		cle = normalize(nom)
		if not cle in self.noms_voies:
			self.noms_voies[cle] = {}
		self.noms_voies[cle][origine] = nom	
def get_part_debut(s,nb_parts):
	resp = ''
	if get_nb_parts(s) > nb_parts:
		resp = ' '.join(s.split()[0:nb_parts])
	return resp
def get_nb_parts(s):
	return len(s.split())
def replace_type_voie(s,nb):
	sp = s.split()
	spd = ' '.join(sp[0:nb])
	spf = ' '.join(sp[nb:len(sp)])
	s = dicts.abrev_type_voie[spd]+' '+spf
	return s
def normalize(s):
	s = s.upper()				# tout en majuscules
	s = s.replace('-',' ')		# separateur espace
	s = s.replace('\'',' ')		# separateur espace
	s = s.replace('/',' ')		# separateur espace
	s = ' '.join(s.split())		# separateur : 1 espace
	for l in iter(dicts.lettre_a_lettre):
		for ll in dicts.lettre_a_lettre[l]:
			s = s.replace(ll,l)
	
	# type de voie
	abrev_trouvee = False
	p = 0
	while (not abrev_trouvee) and p < 3:
		p+= 1
		if get_part_debut(s,p) in dicts.abrev_type_voie:
			s = replace_type_voie(s,p)
			abrev_trouvee = True

	# ordinal
	s = s.replace(' EME ','EME ')

	# chiffres
	for c in dicts.chiffres:
		s = s.replace(c[0],c[1])

	# articles
	for c in dicts.mot_a_blanc:
		s = s.replace(' '+c+' ',' ')

	# titres, etc.
	for r in dicts.abrev_titres:
		s = s.replace(' '+r[0]+' ',' '+r[1]+' ')

	# chiffres romains
	sp = s.split()

	if sp[-1] in dicts.chiffres_romains:
		sp[-1] = dicts.chiffres_romains[sp[-1]]
		s = ' '.join(sp)
			
	return s
def get_line_in_st_line_format(nodelist):
	s = 'ST_LineFromText(\'LINESTRING('
	l_coords = []
	for id in nodelist:
		l_coords.append(str(nodes.n[id].lon)+' '+str(nodes.n[id].lat))
	s = s+','.join(l_coords)+')\')'
	return s
class Node:
	def __init__(self,lon,lat,id,version,tags):
		self.lon = lon
		self.lat = lat
		self.id = id
		self.version = version
		self.tags = tags
		self.sent = False
		self.modified = False
	def get_geom_as_text(self):
		strp = 'ST_PointFromText(\'POINT('+str(self.lon)+' '+str(self.lat)+')\',4326)'
		return strp
	def move_to(self,lon,lat):
		self.lon = lon
		self.lat = lat
	def get_as_osm_xml_node(self):
		s_modified = ""
		if self.modified:
			s_modified = " action=\"modify\" "
		s = "\t<node id=\""+str(self.id)+"\" "+s_modified+"lat=\""+str(self.lat)+"\" lon=\""+str(self.lon)+"\" visible=\"true\" version=\""+str(self.version)+"\""
		if len(self.tags) == 0:
			s = s+"/>\n"
		else:
			s = s+">\n"
			for k in sorted(self.tags.viewkeys()):
				s = s+"\t\t<tag k=\""+k+"\" v=\""+self.tags[k].encode('utf8')+"\"/>\n"
			s = s+"\t</node>\n"
		return s
class Nodes:
	def __init__(self):
		self.n = {}
		self.min_id = 0
	def load_xml_node(self,xml_node,tags):
		id = xml_node.get('id')
		version = xml_node.get('version')
		if not version:
			version = 0
		self.n[id]= Node(xml_node.get('lon'),xml_node.get('lat'),id,version,tags)
		self.min_id = min(self.min_id,int(id))
#		if id == '535300376':
#			os._exit(0)
	def load_new_node_from_xml(self,xml_node,tags):
		n = self.add_new_node(xml_node.get('lon'),xml_node.get('lat'),tags)
		return n
	def add_new_node(self,lon,lat,tags):
		id = str(self.min_id - 1)
		self.n[id] = Node(lon,lat,id,'0',tags)
		self.n[id].modified = True
		self.min_id = min(self.min_id,int(id))
		return id
class WayGeom:
	def __init__(self,a_nodes):
		self.a_nodes = a_nodes
	def get_geom_as_linestring_text(self):
		res = '\'LINESTRING('
		a_n = []
		for ni in self.a_nodes:
			a_n.append(str(nodes.n[ni].lon)+' '+str(nodes.n[ni].lat))
		res = res+','.join(a_n)+')\''
		return res	
class Way:
	def __init__(self,geom,tags,attrib,osm_key):
		self.geom = geom
		self.tags = tags
		self.attrib = attrib
		self.modified = False
		self.sent = False
		self.is_valid = True
		
		self.checks_by_osm_key(osm_key)
	def checks_by_osm_key(self,osm_key):
		if osm_key == 'building':
			self.set_wall()
			self.check_valid_building()
		if osm_key == 'parcelle':
			self.collect_adresses()
	def set_wall(self):
		if 'wall' not in self.tags:
			self.wall = 'yes'
		else:
			self.wall = self.tags['wall']
	def check_valid_building(self):
		if len(self.geom.a_nodes) < 4:
			print('batiment invalide (au mois 4 points) Voir http://www.osm.org/way/'+id)
			self.is_valid = False
		if self.is_valid and self.geom.a_nodes[0] != self.geom.a_nodes[-1]:
			print('batiment invalide (ouvert) Voir http://www.osm.org/way/'+id)
			self.is_valid = False
	def collect_adresses(self):
		tmp_addrs = {}
		self.addrs = {}
		for t in self.tags.viewkeys():
			if t[0:4] == 'addr':
				num_addr = t.split(':')[0][4:]
				if not num_addr in tmp_addrs:
					tmp_addrs[num_addr] = {}
				tmp_addrs[num_addr]['addr:'+t.split(':')[1]] = self.tags[t]
		for sa in tmp_addrs.viewkeys():
			if 'addr:street' in tmp_addrs[sa] and 'addr:housenumber' in tmp_addrs[sa]:
				self.addrs[sa] = tmp_addrs[sa]
				dicts.add_voie('parcelle',tmp_addrs[sa]['addr:street'])
	def add_tag(self,k,v):
		self.tags[k] = v
		self.modified = True
	def insert_new_point(self,n_id,offset):
		b_geom = self.geom.a_nodes
		b_geom.insert(offset+1,n_id)
		self.geom.a_nodes = b_geom
		self.modified = True
	def get_as_osm_xml_way(self):
		s_modified = ""
		if self.modified:
			s_modified = "action=\"modify\" "
		s = "\t<way id=\""+self.attrib['id']+"\" "+s_modified
		for a in self.attrib:
			if a == 'id' or a == 'modify':
				continue
			s = s+" "+a.encode('utf8')+"=\""+self.attrib[a].encode('utf8')+"\""
		s = s+">\n"
		for nl in self.geom.a_nodes:
			s = s+"\t\t<nd ref=\""+str(nl)+"\" />\n"
		for k in sorted(self.tags.viewkeys()):
			s = s+"\t\t<tag k=\""+k+"\" v=\""+self.tags[k].encode('utf8')+"\"/>\n"
		s = s+"\t</way>\n"
		return s
	def get_as_SQL_import_building(self):
		str_query = '''INSERT INTO building_'''+code_insee+'''
							(SELECT ST_Transform(ST_SetSRID(ST_MakePolygon(ST_GeomFromText('''+(self.geom.get_geom_as_linestring_text())+''')),4326),2154),
							'''+self.attrib['id']+''',\''''+self.wall+'''\');'''
		return str_query
	def get_as_SQL_import_building_segment(self,indice):
		s_stline = get_line_in_st_line_format([self.geom.a_nodes[indice],self.geom.a_nodes[indice+1]])
		str_query = '''INSERT INTO building_segments_'''+code_insee+''' 
						(SELECT ST_Transform(ST_SetSRID('''+s_stline+''',4326),2154),
						'''+self.attrib['id']+''',
						'''+self.geom.a_nodes[indice]+''',
						'''+self.geom.a_nodes[indice+1]+''',
						'''+str(indice)+''');'''
		return str_query
	def get_as_SQL_import_parcelle(self):
		str_query = ""
		for a in self.addrs:
			str_query = str_query+'''INSERT INTO parcelles_'''+code_insee+''' 
							(SELECT ST_Transform(ST_SetSRID(ST_MakePolygon(ST_GeomFromText('''+(self.geom.get_geom_as_linestring_text())+''')),4326),2154),
							'''+self.attrib['id']+''',\''''+self.addrs[a]['addr:housenumber']+'''\',\''''+normalize(self.addrs[a]['addr:street'])+'''\');'''
		return str_query
class Ways:
	def __init__(self):
		self.w = {'highway':{},
				'building':{},
				'parcelle':{}}
	def add_way(self,w,id,osm_key):
		self.w[osm_key][id] = w
class Parcelles:
	def __init__(self):
		self.p = {}
	def add_parcelle(self,p,id):
		if id in self.p:
			self.p[id]=self.p[id]+[p]
		else:
			self.p[id]=[p]
class Adresse:
	def __init__(self,node,num,voie):
		self.node = node
		self.numero = num
		self.voie = voie
		self.addr_as_building_way = []
		self.addr_as_node_on_building = []
		self.building_for_addr_node = []
	def add_addr_as_building(self,b_id):
		self.addr_as_building_way = self.addr_as_building_way+[b_id]
	def add_addr_as_node_on_building(self, n_id):
		self.addr_as_node_on_building = self.addr_as_node_on_building+[n_id]
	def add_building_for_addr_node(self,b_id):
		self.building_for_addr_node = self.building_for_addr_node+[b_id]
class Adresses:
	def __init__(self):
		self.a = {}
	def add_adresse(self,ad):
		cle = normalize(ad.voie)
		if not cle in self.a:
			self.a[cle] = {'numeros':{},'batiments_complementaires':[]}
		self.a[cle]['numeros'][ad.numero] = ad
	def add_batiment_complementaire(self,cle,b_id):
		cle = normalize(cle)
		if not cle in self.a:
			self.a[cle] = {'numeros':{},'batiments_complementaires':[]}
		self.a[cle]['batiments_complementaires'] = self.a[cle]['batiments_complementaires'] + [b_id]
def get_as_osm_xml_way(node_list,tags,attrib,modified):
	s_modified = ""
	if modified:
		s_modified = "action=\"modify\" "
	s = "\t<way id=\""+attrib['id']+"\" "+s_modified
	for a in attrib:
		if a == 'id' or a == 'modify':
			continue
		s = s+" "+a.encode('utf8')+"=\""+attrib[a].encode('utf8')+"\""
	s = s+">\n"
	for nl in node_list:
		s = s+"\t\t<nd ref=\""+str(nl)+"\" />\n"
	for k in sorted(tags.viewkeys()):
		s = s+"\t\t<tag k=\""+k+"\" v=\""+tags[k].encode('utf8')+"\"/>\n"
	s = s+"\t</way>\n"
	return s
def load_nodes_from_xml_parse(xmlp):
	for n in xmlp.iter('node'):
		dtags = get_tags(n)
		nodes.load_xml_node(n,dtags)
def load_ways_from_xml_parse(xmlp,osm_key):
	for b in xmlp.iter('way'):
		a_n = []
		for bn in b.iter('nd'):
			a_n.append(bn.get('ref'))
		g = WayGeom(a_n)
		dtags = get_tags(b)
		ways.add_way(Way(g,dtags,b.attrib,osm_key),b.get('id'),osm_key)
def get_tags(xmlo):
	dtags = {}
	for tg in xmlo.iter('tag'):
		dtags[tg.get('k')] = tg.get('v')
	return dtags
def download_ways_from_overpass(way_type,target_file_name):
	d_url = urllib.quote('http://oapi-fr.openstreetmap.fr/oapi/interpreter?data=node(area:'+str(3600000000+dicts.osm_insee[code_insee])+');way(bn);(way._["'+way_type+'"];node(w););out meta;',':/?=')
	d_url = d_url.replace('way._','way%2E%5F').replace('area:','area%3A')
#node(area:3600076381);rel(bn);(relation._["type"="associatedStreet"];);(._;>;);out meta;;
	print('telechargement des '+way_type+' OSM...')
	try:
		resp = urllib2.urlopen(d_url)
		target_file = open(target_file_name,'wb')
		target_file.write(resp.read())
		target_file.close()
		print("ok")
	except urllib2.HTTPError:
		print('\n******* récupération des '+way_type+' KO ********')
		print('Abandon')
		os._exit(0)
def	executeSQL_INSEE(fnsql,code_insee):
	fsql = open(fnsql,'rb')
	str_query = fsql.read()
	fsql.close()
	str_query = str_query.replace('__com__','_'+code_insee)
	cur_sql = pgc.cursor()
	cur_sql.execute(str_query)
	cur_sql.close()
	
def main(args):
	if len(args) < 4:
		print('USAGE : python addr_fantoir_building.py <code INSEE> <code Cadastre> <1|2> (nom de la commune)')
		print('1 : adresses comme points sur les bâtiments')
		print('2 : adresses comme tags des ways building')
		os._exit(0)
		
	global code_insee,code_cadastre
	code_insee = args[1]
	code_cadastre = args[2]
	global dicts
	dicts = Dicts()
	dicts.load_all(code_insee)
	global pgc
	pgc = get_pgc()
	
	tierce = args[3]
	if str(tierce) not in ['1','2']:
		tierce = '1'
	nom_ville = ''
	if len(args) > 4:
		nom_ville = ' '.join(args[4:])
		nom_ville = normalize(nom_ville).replace(' ','_')

	rep_parcelles_adresses = 'parcelles_adresses'
	fnparcelles = rep_parcelles_adresses+'/'+code_cadastre+'-parcelles.osm'
	fnadresses = rep_parcelles_adresses+'/'+code_cadastre+'-adresses.osm'
	root_dir_out = 'osm_output'
	if not os.path.exists(root_dir_out):
		os.mkdir(root_dir_out)
	dirout = root_dir_out+'/'+'_'.join(['adresses',nom_ville,code_insee[0:2],code_cadastre,'style',tierce])
	if not os.path.exists(dirout):
		os.mkdir(dirout)
		
	building_rep = 'cache_buildings'
	if not os.path.exists(building_rep):
		os.mkdir(building_rep)

	global nodes,ways
	nodes = Nodes()
	ways = Ways()
	parcelles = Parcelles()
	adresses = Adresses()

	fnbuilding = building_rep+'/buildings_'+code_insee+'.osm'
	if not os.path.exists(fnbuilding):
		download_ways_from_overpass('building',fnbuilding)
			
	print('mise en cache des buildings...')
	xmlbuldings = ET.parse(fnbuilding)
	print('nodes...')
	load_nodes_from_xml_parse(xmlbuldings)
	print('buildings...')
	load_ways_from_xml_parse(xmlbuldings,'building')
	del xmlbuldings
	gc.collect()

	executeSQL_INSEE('create_tables__com__.sql',code_insee)

	print('chargement des polygones...')
	cur_buildings = pgc.cursor()
	str_query = ""
	for idx,id in enumerate(ways.w['building']):
		if not ways.w['building'][id].is_valid:
			continue
		str_query = str_query+ways.w['building'][id].get_as_SQL_import_building()
		if idx%100 == 0 and str_query != "":
			cur_buildings.execute(str_query+"COMMIT;")
			str_query = ""
	if str_query != "":
		cur_buildings.execute(str_query+"COMMIT;")

	print('chargement des segments...')
	str_query = ""
	for idx,id in enumerate(ways.w['building']):
		if not ways.w['building'][id].is_valid:
			continue
		for nn in range(0,len(ways.w['building'][id].geom.a_nodes)-1):
			str_query = str_query+ways.w['building'][id].get_as_SQL_import_building_segment(nn)
		if idx%100 == 0 and str_query != "":
			cur_buildings.execute(str_query+"COMMIT;")
			str_query = ""
	if str_query != "":
		cur_buildings.execute(str_query+"COMMIT;")
	str_query = ""

	print('mise en cache des parcelles...')
	print('nodes...')
	xmlparcelles = ET.parse(fnparcelles)
	load_nodes_from_xml_parse(xmlparcelles)
	print('parcelles...')
	load_ways_from_xml_parse(xmlparcelles,'parcelle')
	del xmlparcelles
	gc.collect()

	print('chargement...')
	cur_parcelles = pgc.cursor()
	str_query = ""
	for idx,id in enumerate(ways.w['parcelle']):
		str_query = str_query+ways.w['parcelle'][id].get_as_SQL_import_parcelle()
		if idx%100 == 0:
			cur_parcelles.execute(str_query+"COMMIT;")
			str_query = ""
	if str_query != "":
		cur_parcelles.execute(str_query+"COMMIT;")

	print('mise en cache des points adresses...')
	print('nodes...')
	xmladresses = ET.parse(fnadresses)
	dict_node_relations = {}
	for asso in xmladresses.iter('relation'):
		for t in asso.iter('tag'):
			if t.get('k') == 'name':
				for n in asso.iter('member'):
					if not n.get('ref') in dict_node_relations:
						dict_node_relations[n.get('ref')] = []
					dict_node_relations[n.get('ref')] = dict_node_relations[n.get('ref')]+[normalize(t.get('v'))]
			dicts.add_voie('adresse',t.get('v'))

	load_nodes_from_xml_parse(xmladresses)
	for n in xmladresses.iter('node'):
		dtags = get_tags(n)
		n_id = n.get('id')
		nodes.n[n_id].modified = True
		if 'addr:housenumber' in nodes.n[n_id].tags and n_id in dict_node_relations:
			for v in dict_node_relations[n_id]:
				ad = Adresse(nodes.n[n_id],dtags['addr:housenumber'],v)
				adresses.add_adresse(ad)
				
	print('chargement...')
	cur_adresses = pgc.cursor()
	str_query = ""
	for idx,voie in enumerate(adresses.a):
		for num in adresses.a[voie]['numeros']:
			ad = adresses.a[voie]['numeros'][num]
			str_query = str_query+'''INSERT INTO adresses_'''+code_insee+''' 
							(SELECT ST_Transform('''+ad.node.get_geom_as_text()+''',
							2154),'''+str(ad.node.id)+''',\''''+num+'''\',\''''+voie+'''\');'''

		if idx%100 == 0:
			cur_adresses.execute(str_query+"COMMIT;")
			str_query = ""
	if str_query != "":
		cur_adresses.execute(str_query+"COMMIT;")

	highway_rep = 'cache_highways'
	if not os.path.exists(highway_rep):
		os.mkdir(highway_rep)
	fnhighway = highway_rep+'/highways_'+code_insee+'.osm'
	if not os.path.exists(fnhighway):
		download_ways_from_overpass('highway',fnhighway)
	
	print('mise en cache des voies...')
	dict_ways_osm = {}
	xmlways = ET.parse(fnhighway)
	load_nodes_from_xml_parse(xmlways)
	load_ways_from_xml_parse(xmlways,'highway')

	for w in xmlways.iter('way'):
		for t in w.iter('tag'):
			if t.get('k') == 'name':
				name_osm = t.get('v')
				dicts.add_voie('OSM',name_osm)

				name_norm = normalize(name_osm)
				if name_norm not in dict_ways_osm:
					dict_ways_osm[name_norm] = {'name':name_osm,'ids':[]}
				dict_ways_osm[name_norm]['ids'].append(w.get('id'))

	print('Traitements PostGIS...')
	executeSQL_INSEE('adresses_buildings.sql',code_insee)

	if tierce == '1':
		print('Report des adresses sur les buildings en tant que nouveaux points...')
		cur_addr_node_building = pgc.cursor()
		str_query = '''SELECT 	lon,
								lat,
								id_building::integer,
								indice_node_1,
								numero,
								voie,
								id_adresse::integer
						FROM points_adresse_sur_building_'''+code_insee+''';'''
		cur_addr_node_building.execute(str_query)
		for c in cur_addr_node_building:
			nodes.n[str(c[6])].move_to(c[0],c[1])
			ways.w['building'][str(c[2])].insert_new_point(str(c[6]),c[3])
			adresses.a[c[5]]['numeros'][c[4]].add_addr_as_node_on_building(str(c[6]))
			adresses.a[c[5]]['numeros'][c[4]].add_building_for_addr_node(str(c[2]))
		
	if tierce == '2':
		print('Report des adresses sur les buildings en tant que nouveau tag...')
		# batiments modifies
		cur_addr_way_building = pgc.cursor()
		str_query = '''SELECT id_building::integer,
								id_adresse::integer,
								numero,
								voie
						FROM adresse_sur_buildings_'''+code_insee+''';'''
		cur_addr_way_building.execute(str_query)
		for c in cur_addr_way_building:
			ways.w['building'][str(c[0])].add_tag('addr:housenumber',c[2])
			adresses.a[c[3]]['numeros'][c[2]].add_addr_as_building(str(c[0]))

	print('Ajout des autres buildings de la voie...')
	# autres batiments des parcelles de la voie
	cur_addr_building_comp = pgc.cursor()
	str_query = '''SELECT id_building::integer,
							voie
					FROM buildings_complementaires_'''+code_insee+'''
					EXCEPT
					SELECT id_building::integer,
							voie
					FROM adresse_sur_buildings_'''+code_insee+''';'''
	cur_addr_building_comp.execute(str_query)

	for c in cur_addr_building_comp:
		adresses.add_batiment_complementaire(c[1],str(c[0]))

	print('Fichier rapport...')
	fntmpkeys = dirout+'/_rapport.txt'
	ftmpkeys = open(fntmpkeys,'w')
	ftmpkeys.write('--noms de voies OSM normalisés (noms en base OSM)--\n')
	for v in sorted(dict_ways_osm):
		ftmpkeys.write(v.encode('utf8')+' ('+dict_ways_osm[v]['name'].encode('utf8')+')\n')
	ftmpkeys.write('---------------------\n')
	ftmpkeys.write('-- Voies du cadastre non retrouvées ailleurs :\n')

	# compteurs pour le bilan
	nb_voies_total = 0
	nb_voies_fantoir = 0
	nb_voies_osm = 0

	print('Fichiers associatedStreet...')
	for v in adresses.a:
		fout = open(dirout+'/'+code_cadastre+'_'+dicts.noms_voies[v]['parcelle'].replace(' ','_')+'.osm','w')
		fout.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
		fout.write("<osm version=\"0.6\" upload=\"false\" generator=\"addr_fantoir_building.py\">\n")
	# nodes
		for num in adresses.a[v]['numeros']:
			numadresse = adresses.a[v]['numeros'][num]
	## 	point adresse isole
			if not (numadresse.addr_as_building_way or numadresse.addr_as_node_on_building):
				if not numadresse.node.sent:
					fout.write(numadresse.node.get_as_osm_xml_node())
					numadresse.node.sent = True
	## 	point adresse reference par un batiment
			for eb in numadresse.building_for_addr_node:
				for ebn in ways.w['building'][eb].geom.a_nodes:
					if not nodes.n[ebn].sent:
						fout.write(nodes.n[ebn].get_as_osm_xml_node())
						nodes.n[ebn].sent = True
	##	nodes des batiments directement taggues en hsnr
			for eb in numadresse.addr_as_building_way:
				for ebn in ways.w['building'][eb].geom.a_nodes:
					if not nodes.n[ebn].sent:
						fout.write(nodes.n[ebn].get_as_osm_xml_node())
						nodes.n[ebn].sent = True

	##	nodes des batiments complementaires
		for eb in adresses.a[v]['batiments_complementaires']:
			for ebn in ways.w['building'][eb].geom.a_nodes:
				if not nodes.n[ebn].sent:
					fout.write(nodes.n[ebn].get_as_osm_xml_node())
					nodes.n[ebn].sent = True
	## nodes des highways
		if 'OSM' in dicts.noms_voies[v]:
			for w in dict_ways_osm[v]['ids']:
				for wn in ways.w['highway'][w].geom.a_nodes:
					fout.write(nodes.n[wn].get_as_osm_xml_node())

	# ways
	## batiments porteurs d'une adresse
		for num in adresses.a[v]['numeros']:
			numadresse = adresses.a[v]['numeros'][num]
			for eb in (numadresse.addr_as_building_way + numadresse.building_for_addr_node):
				fout.write(ways.w['building'][eb].get_as_osm_xml_way())
	# en prevision des autres fichiers, raz du statut "envoye" des nodes
				for ebn in ways.w['building'][eb].geom.a_nodes:
					nodes.n[ebn].sent = False

	##	batiments complementaires
		for eb in adresses.a[v]['batiments_complementaires']:
			fout.write((ways.w['building'][eb]).get_as_osm_xml_way())
	# en prevision des autres fichiers, raz du statut "envoye" des nodes
			for ebn in ways.w['building'][eb].geom.a_nodes:
				nodes.n[ebn].sent = False

	## ways des highways
		if 'OSM' in dicts.noms_voies[v]:
			for w in dict_ways_osm[v]['ids']:
				fout.write((ways.w['highway'][w]).get_as_osm_xml_way())
				for wn in ways.w['highway'][w].geom.a_nodes:
					nodes.n[wn].sent = False

	# relations	
		fout.write("\t<relation id=\""+str(nodes.min_id - 1)+"\" action=\"modify\" visible=\"true\">\n")
		for num in adresses.a[v]['numeros']:
			numadresse = adresses.a[v]['numeros'][num]
			if not (numadresse.addr_as_building_way or numadresse.addr_as_node_on_building):
				fout.write("\t\t<member type=\"node\" ref=\""+str(numadresse.node.id)+"\" role=\"house\"/>\n")
				nodes.n[numadresse.node.id].sent = False
			else:
				for eb in numadresse.addr_as_node_on_building:
					fout.write("\t\t<member type=\"node\" ref=\""+str(eb)+"\" role=\"house\"/>\n")
					nodes.n[eb].sent = False
				for eb in numadresse.addr_as_building_way:
					fout.write("\t\t<member type=\"way\" ref=\""+str(eb)+"\" role=\"house\"/>\n")
					
		street_name = dicts.noms_voies[v]['adresse'].title()
		if 'OSM' in dicts.noms_voies[v]:
			street_name =  dicts.noms_voies[v]['OSM'].encode('utf8')
			for m in dict_ways_osm[v]['ids']:
				fout.write("		<member type=\"way\" ref=\""+m+"\" role=\"street\"/>\n")
			nb_voies_osm += 1
		else:
			ftmpkeys.write('voie absente dans OSM     	 : '+dicts.noms_voies[v]['adresse']+'\n')
		fout.write("		<tag k=\"type\" v=\"associatedStreet\"/>\n")
		fout.write("		<tag k=\"name\" v=\""+street_name+"\"/>\n")
		if v in dicts.fantoir:
			fout.write("		<tag k=\"ref:FR:FANTOIR\" v=\""+dicts.fantoir[v]+"\"/>\n")
			nb_voies_fantoir += 1
		else:
			ftmpkeys.write('voie absente dans le FANTOIR : '+dicts.noms_voies[v]['adresse']+'\n')
		fout.write("	</relation>\n")
		nb_voies_total +=1
		fout.write("</osm>")
		fout.close()

	ftmpkeys.write(	"---------------- BILAN ----------------\n")
	s = 			"Nombre de relations creees  : "+str(nb_voies_total)
	print(s)
	ftmpkeys.write(s+'\n')
	s = "     avec code FANTOIR      : "+str(nb_voies_fantoir)+" ("+str(int(nb_voies_fantoir*100/nb_voies_total))+"%)"
	print(s)
	ftmpkeys.write(s+'\n')
	s = "     avec rapprochement OSM : "+str(nb_voies_osm)+" ("+str(int(nb_voies_osm*100/nb_voies_total))+"%)"
	print(s)
	ftmpkeys.write(s+'\n')
	ftmpkeys.close()
	fin_total = time.time()

	print('Execution en '+str(int(fin_total - debut_total))+' s.')
	# mode 1 : addr:housenumber comme tag du building
	#			sinon point adresse seul à la place fournie en entree
	# mode 2 : addr:housenumber comme point à mi-longueur du plus proche coté du point initial
	#			sinon point adresse seul à la place fournie en entree
if __name__ == '__main__':
    main(sys.argv)