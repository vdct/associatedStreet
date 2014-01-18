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