# coding: UTF-8
def rivoli_brut_vers_dict(fn):
	h = open(fn,'r')
	dictFantoir = {}
	for l in h:
		if l[73:74] != ' ':
			continue
		cle = ' '.join((l[11:15].rstrip().lstrip()+' '+l[15:41].rstrip().lstrip()).replace('-',' ').lstrip().split())
		dictFantoir[cle] = l[0:2]+l[3:11]
	h.close()
	return dictFantoir

def rivoli_dept_vers_dict(fn,insee):
	h = open(fn,'r')
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
		dictFantoir[normalize(cle)] = l[0:2]+l[3:11]
	h.close()
	return dictFantoir

def get_dict_osm_insee():
	dict_osm_insee = {}
	finsee = open('osm_id_ref_insee.csv','r')
	for e in finsee:
		c = (e.splitlines()[0]).split(',')
		dict_osm_insee[str(c[1])] = int(c[0])
	return dict_osm_insee
	
def normalize(s):
	dict_replace_lettres = get_dict_replace_lettres()
	dict_abbrev_debut = get_dict_abbrev_debut()
	
	s = s.upper()				# tout en majuscules
	s = s.replace('-',' ')		# separateur espace
	s = s.replace('\'',' ')		# separateur espace
	s = ' '.join(s.split())		# separateur : 1 espace
	for l in iter(dict_replace_lettres.viewkeys()):
		for ll in dict_replace_lettres[l]:
			s = s.replace(ll,l)
	
	spart = s.partition(' ')
	if spart[0] in dict_abbrev_debut:
		s = dict_abbrev_debut[spart[0]]+' '+spart[2]
		
	return s
	
def get_dict_replace_lettres():
	dict_replace_lettres = {'A':[u'Â',u'À'],
							'C':[u'Ç'],
							'E':[u'È',u'Ê',u'É',u'Ë'],
							'I':[u'Ï',u'Î'],
							'O':[u'Ö'],
							'U':[u'Û',u'Ü']}
	return dict_replace_lettres

def get_dict_abbrev_debut():
	dict_replace_debut = {	'ANCIEN CHEMIN':'ACH',
							'AERODROME':'AER',
							'AGGLOMERATION':'AGL',
							'AIRE':'AIRE',
							'ALLEE':'ALL',
							'ANGLE':'ANGL',
							'ARCADE':'ARC',
							'ANCIENNE ROUTE':'ART',
							'AUTOROUTE':'AUT',
							'AVENUE':'AV',
							'BASE':'BASE',
							'BOULEVARD':'BD',
							'BERGE':'BER',
							'BORD':'BORD',
							'BARRIERE':'BRE',
							'BOURG':'BRG',
							'BRETELLE':'BRTL',
							'BASSIN':'BSN',
							'CARRIERA':'CAE',
							'CALLE':'CALL',
							'CAMIN':'CAMI',
							'CAMP':'CAMP',
							'CANAL':'CAN',
							'CARREFOUR':'CAR',
							'CARRIERE':'CARE',
							'CASERNE':'CASR',
							'CHEMIN COMMUNAL':'CC',
							'CHEMIN DEPARTEMENTAL':'CD',
							'CHEMIN FORESTIER':'CF',
							'CHASSE':'CHA',
							'CHEMIN':'CHE',
							'CHEMINEMENT':'CHEM',
							'CHALET':'CHL',
							'CHAMP':'CHP',
							'CHAUSSEE':'CHS',
							'CHATEAU':'CHT',
							'CHEMIN VICINAL':'CHV',
							'CITE':'CITE',
							'COURSIVE':'CIVE',
							'CLOS':'CLOS',
							'COULOIR':'CLR',
							'COIN':'COIN',
							'COL':'COL',
							'CORNICHE':'COR',
							'CORON':'CORO',
							'COTE':'COTE',
							'COUR':'COUR',
							'CAMPING':'CPG',
							'CHEMIN RURAL':'CR',
							'COURS':'CRS',
							'CROIX':'CRX',
							'CONTOUR':'CTR',
							'CENTRE':'CTRE',
							'DARSE':'DARS',
							'DEVIATION':'DEVI',
							'DIGUE':'DIG',
							'DOMAINE':'DOM',
							'DRAILLE':'DRA',
							'DESCENTE':'DSC',
							'ÉCART':'ECA',
							'ECLUSE':'ECL',
							'EMBRANCHEMENT':'EMBR',
							'ENCLOS':'ENC',
							'ENCLAVE':'ENV',
							'ESCALIER':'ESC',
							'ESPLANADE':'ESP',
							'ESPACE':'ESPA',
							'ETANG':'ETNG',
							'FOND':'FD',
							'FAUBOURG':'FG',
							'FONTAINE':'FON',
							'FORT':'FORT',
							'FOSSE':'FOS',
							'FERME':'FRM',
							'GALERIE':'GAL',
							'GARE':'GARE',
							'GRAND BOULEVARD':'GBD',
							'GRAND PLACE':'GPL',
							'GRANDE RUE':'GR',
							'HABITATION':'HAB',
							'HAMEAU':'HAM',
							'HALLE':'HLE',
							'HALAGE':'HLG',
							'HLM':'HLM',
							'ÎLE':'ILE',
							'ILOT':'ILOT',
							'IMPASSE':'IMP',
							'JARDIN':'JARD',
							'JETEE':'JTE',
							'LAC':'LAC',
							'LEVEE':'LEVE',
							'LICES':'LICE',
							'LIGNE':'LIGN',
							'LOTISSEMENT':'LOT',
							'MAIL':'MAIL',
							'MAISON':'MAIS',
							'MARCHE':'MAR',
							'MAS':'MAS',
							'MARINA':'MRN',
							'MONTEE':'MTE',
							'NOUVELLE ROUTE':'NTE',
							'PETITE AVENUE':'PAE',
							'PARC':'PARC',
							'PASSAGE':'PAS',
							'PASSE':'PASS',
							'PETIT CHEMIN':'PCH',
							'PHARE':'PHAR',
							'PISTE':'PIST',
							'PARKING':'PKG',
							'PLACE':'PL',
							'PLACA':'PLA',
							'PLAGE':'PLAG',
							'PLAN':'PLAN',
							'PLACIS':'PLCI',
							'PASSERELLE':'PLE',
							'PLAINE':'PLN',
							'PLATEAU':'PLT',
							'POINTE':'PNT',
							'PONT':'PONT',
							'PORTIQUE':'PORQ',
							'PORT':'PORT',
							'POSTE':'POST',
							'POTERNE':'POT',
							'PROMENADE':'PROM',
							'PETITE ROUTE':'PRT',
							'PARVIS':'PRV',
							'PETITE ALLEE':'PTA',
							'PORTE':'PTE',
							'PETITE RUE':'PTR',
							'PLACETTE':'PTTE',
							'QUARTIER':'QUA',
							'QUAI':'QUAI',
							'RACCOURCI':'RAC',
							'REMPART':'REM',
							'RESIDENCE':'RES',
							'RIVE':'RIVE',
							'RUELLE':'RLE',
							'ROCADE':'ROC',
							'RAMPE':'RPE',
							'ROND POINT':'RPT',
							'ROTONDE':'RTD',
							'ROUTE':'RTE',
							'RUE':'RUE',
							'RUETTE':'RUET',
							'RUISSEAU':'RUIS',
							'RUELLETTE':'RULT',
							'RAVINE':'RVE',
							'SAS':'SAS',
							'SENTIER':'SEN',
							'SQUARE':'SQ',
							'STADE':'STDE',
							'TOUR':'TOUR',
							'TERRE PLEIN':'TPL',
							'TRAVERSE':'TRA',
							'TRABOULE':'TRAB',
							'TERRAIN':'TRN',
							'TERTRE':'TRT',
							'TERRASSE':'TSSE',
							'TUNNEL':'TUN',
							'VAL':'VAL',
							'VALLON':'VALL',
							'VOIE COMMUNALE':'VC',
							'VIEUX CHEMIN':'VCHE',
							'VENELLE':'VEN',
							'VILLAGE':'VGE',
							'VIA':'VIA',
							'VIADUC':'VIAD',
							'VILLE':'VIL',
							'VILLA':'VLA',
							'VOIE':'VOIE',
							'VOIRIE':'VOIR',
							'VOUTE':'VOUT',
							'VOYEUL':'VOY',
							'VIEILLE ROUTE':'VTE',
							'ZA':'ZA',
							'ZAC':'ZAC',
							'ZAD':'ZAD',
							'ZI':'ZI',
							'ZONE':'ZONE',
							'ZUP':'ZUP'}
	return dict_replace_debut