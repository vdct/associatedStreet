import psycopg2

def get_pgc():
	pgc = psycopg2.connect("dbname='<nom de la base PostGIS>' user='<user>' host='<hote>' password='<mot de passe>'")
	return pgc