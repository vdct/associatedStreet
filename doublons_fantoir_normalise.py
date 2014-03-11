#!/usr/bin/env python
# coding: UTF-8
# import copy
# import glob
# import gc
# import urllib,urllib2
# import sys,shutil
import os,os.path
# import psycopg2
from pg_connexion import get_pgc
# import addr_fantoir_building as afb
# import time 
# import xml.etree.ElementTree as ET
# import xml.sax.saxutils as XSS
# import zipfile

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
		self.ways_osm = {}

	def load_lettre_a_lettre(self):
		self.lettre_a_lettre = {'A':[u'Â',u'À'],
						'C':[u'Ç'],
						'E':[u'È',u'Ê',u'É',u'Ë'],
						'I':[u'Ï',u'Î'],
						'O':[u'Ö',u'Ô'],
						'U':[u'Û',u'Ü']}
	def load_fantoir(self,insee):
		str_query = '''	SELECT 	code_insee||id_voie||cle_rivoli,
								nature_voie||' '||libelle_voie
						FROM	fantoir_voie
						WHERE	code_insee = \''''+insee+'''\' AND
								caractere_annul NOT IN ('O','Q');'''
		cur_fantoir = pgc.cursor()
		cur_fantoir.execute(str_query)
		for c in cur_fantoir:
			cle = ' '.join(c[1].replace('-',' ').split())
			cle = normalize(cle)
			self.fantoir[cle] = c[0]
			self.add_voie('fantoir',cle)
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
		fn = os.path.join(os.path.dirname(__file__), 'abrev_type_voie.txt')
		f = open(fn)
		for l in f:
			c = (l.splitlines()[0]).split('\t')
			self.abrev_type_voie[c[0]] = c[1]
		f.close()
	def load_osm_insee(self):
		finsee_path = os.path.join(os.path.dirname(__file__),'osm_id_ref_insee.csv')
		finsee = open(finsee_path,'r')
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
def normalize(s):
	# s = s.encode('ascii','ignore')
	s = s.upper()				# tout en majuscules
	s = s.replace('-',' ')		# separateur espace
	s = s.replace('\'',' ')		# separateur espace
	s = s.replace('/',' ')		# separateur espace
	s = ' '.join(s.split())		# separateur : 1 espace
	for l in iter(dicts.lettre_a_lettre):
		for ll in dicts.lettre_a_lettre[l]:
			s = s.replace(ll,l)
	s = s.encode('ascii','ignore')
	
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

pgc = get_pgc()
fr = open('doublons_fantoir.txt','wb')

dicts = Dicts()
dicts.load_lettre_a_lettre()
dicts.load_abrev_type_voie()
dicts.load_abrev_titres()
dicts.load_chiffres()
dicts.load_chiffres_romains()
dicts.load_mot_a_blanc()
dicts.load_osm_insee()

str_query = 'SELECT DISTINCT code_insee FROM fantoir_voie ORDER BY 1;'
cur_insee = pgc.cursor()
cur_insee.execute(str_query)

nb_villes = 0
nb_villes_avec_doublons = 0
nb_villes_sans_doublons = 0
nb_voies = 0
nb_doublons = 0
for c_insee in cur_insee:
	nb_villes += 1
	avec_doublon = False
	fr.write(('*** INSEE : %s\n') % (c_insee[0]))
	dic_fantoir = {}
	str_query = '''	SELECT 	code_insee||id_voie||cle_rivoli,
								nature_voie||' '||libelle_voie
						FROM	fantoir_voie
						WHERE	code_insee = \''''+c_insee[0]+'''\' AND
								caractere_annul NOT IN ('O','Q');'''
	cur_fantoir = pgc.cursor()
	cur_fantoir.execute(str_query)
	for c in cur_fantoir:
		nb_voies += 1
		nom_voie = ' '.join(c[1].replace('-',' ').split())
		cle = normalize(nom_voie)
		if cle not in dic_fantoir:
			dic_fantoir[cle] = []
		dic_fantoir[cle].append([c[0],nom_voie])
	for k,v in dic_fantoir.iteritems():
		if len(v)>1:
			nb_doublons += 1
			avec_doublon = True
			for i in v:
				fr.write('%s : %s(%s)\n' % (k, i[1], i[0]))
	if 	avec_doublon:
		nb_villes_avec_doublons += 1
	else:
		nb_villes_sans_doublons += 1
s_bilan = (u'Bilan :\n\t{:d} villes dont :\n\t\t* {:d} villes avec doublons\n\t\t* {:d} villes sans doublons\n\t{:d} voies dont :\n\t\t* {:d} noms normalisés à codes Fantoir multiples ({:.2%})'.format(nb_villes,nb_villes_avec_doublons,nb_villes_sans_doublons,nb_voies,nb_doublons,(float(nb_doublons)/nb_voies)))
print(s_bilan)
fr.write(s_bilan.encode('utf8'))
fr.close()
