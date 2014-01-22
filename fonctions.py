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
	s = s.replace('/',' ')		# separateur espace
	s = ' '.join(s.split())		# separateur : 1 espace
	for l in iter(dict_replace_lettres.viewkeys()):
		for ll in dict_replace_lettres[l]:
			s = s.replace(ll,l)
	
	spart = s.partition(' ')
	s_comp = spart[0]
	s_reste = spart[2]
	
	abrev_trouvee = False
	nb_parts = len(s.split())
	
	# type de voie
	if s_comp in dict_abbrev_debut:
		s = dict_abbrev_debut[s_comp]+' '+s_reste
		abrev_trouvee = True
	if not abrev_trouvee and nb_parts > 3:
		s_comp = s_comp+' '+s_reste.partition(' ')[0]
		s_reste = s_reste.partition(' ')[2]
		if s_comp in dict_abbrev_debut:
			s = dict_abbrev_debut[s_comp]+' '+s_reste
			abrev_trouvee = True
	if not abrev_trouvee and nb_parts > 4:
		s_comp = s_comp+' '+s_reste.partition(' ')[0]
		s_reste = s_reste.partition(' ')[2]
		if s_comp in dict_abbrev_debut:
			s = dict_abbrev_debut[s_comp]+' '+s_reste
			abrev_trouvee = True
	
	# ordinal
	s = s.replace(' EME ','EME ')
	
	# chiffres
	s = s.replace('0','ZERO').replace('1','UN').replace('2','DEUX').replace('3','TROIS').replace('4','QUATRE').replace('5','CINQ').replace('6','SIX').replace('7','SEPT').replace('8','HUIT').replace('9','NEUF')
	s = s.replace(' DIX ',' UNZERO ').replace(' ONZE ',' UNUN ').replace(' DOUZE ',' UNDEUX ')
	
	# articles
	list_replace_blanc = ['DE LA','DU','DES','LE','LA','LES','DE','D']
	for r in list_replace_blanc:
		s = s.replace(' '+r+' ',' ')
	
	# titres, etc.
	list_replace_titre = [	['MARECHAL','MAL'],
							['PRESIDENT','PDT'],
							['GENERAL','GAL'],
							['COMMANDANT','CDT'],
							['CAPITAINE','CAP'],
							['REGIMENT','REGT'],
							['SAINTE','STE'],
							['SAINT','ST']]
	for r in list_replace_titre:
		s = s.replace(' '+r[0]+' ',' '+r[1]+' ')
	
	# chiffres romains
	sp = s.split()
	dict_replace_romains = {'XXIII':'DEUXTROIS',
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
	if sp[-1] in dict_replace_romains:
		sp[-1] = dict_replace_romains[sp[-1]]
		s = ' '.join(sp)
		
	return s
	
def get_dict_replace_lettres():
	dict_replace_lettres = {'A':[u'Â',u'À'],
							'C':[u'Ç'],
							'E':[u'È',u'Ê',u'É',u'Ë'],
							'I':[u'Ï',u'Î'],
							'O':[u'Ö',u'Ô'],
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
							'GR GRANDE RUE':'GR',
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
							'PCH PETIT CHEMIN':'PCH',
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
							'PTR PETITE RUE':'PTR',
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