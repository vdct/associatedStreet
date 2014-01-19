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
		dictFantoir[cle] = l[0:2]+l[3:11]
	h.close()
	return dictFantoir
	
def normalize(s):
	s = s.replace('-',' ')
	s = ' '.join(s.split()).upper()
	return s