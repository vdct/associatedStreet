addr_fantoir_building.py

Reprend les fonctionnalités de addrfantoir.py et ajoute le rattachement des n° d'adresse aux bâtiments sous forme de tag porté par le way building.

Requiert le script adresses_buildings.sql, accès en RO à une base OSM Monde (schema osm2pgsql) et un accès en RW à une base PostGIS.


Le fichier pg_connexion.py.txt est à renommer en pg_connexion.py et à adapter en modifiant les parties entre <>.

***************
addrfantoir.py : recherche du code FANTOIR des voies pour enrichissement d'un fichier d'adresses déjà regroupées en relations associatedStreet.
Le fichier des relations provient de http://37.187.60.59/cadastre-housenumber/adresses.php
En local, il faut dans le répertoire où se situe ce fichier ET le script python, ajouter :
- le fichier Fantoir brut du département correspondant, obtenu (par zip de régions) ici :
https://www.collectivites-locales.gouv.fr/mise-a-disposition-gratuite-fichier-des-voies-et-des-lieux-dits-fantoir
- le fichier osm_id_ref_insee.csv qui donne pour chaque code INSEE le n° de relation admin 8 dans OSM. Cette relation est utilisée pour extraire tous les highways nommés de la commune, via un appel Overpass

Le script a besoin de 2 paramètres, demandés en invite de commande : le nom du fichier d'adresses, et le code INSEE de la commune correspondante (pour filtrer les bonnes entrées du FANTOIR et interroger l'Overpass)

En sortie :
- un répertoire "fichiers_"+ le nom du fichier d'adresses avec autant de fichiers .osm que de relations associatedStreet créées. Un fichier additionnel peut être crée, nommé "numeros_ambigus_a_verifier.osm" si des adresses contenaient en entrée un tag 'fixme'
- un fichier "cles_noms_de_voies.txt" dans le répertoire initial : fichier qui liste les noms de voies trouvés dans OSM, et ceux sans correspondance. Utile pour analyser le taux de réussite et éventuellement enrichir la liste des abréviations.

Les fichiers en sortie n'ont pas vocation à être envoyés vers la base OSM. Chaque point d'adresse doit être replacé sur un bâtiment (ou, selon les pratiques, en limite de propriété). Le cas échéant, le point doit être intégré au contour d'un bâtiment. Même sans vraie convention, les noms dans les relations associatedStreet devraient reprendre les noms portés par les rues dans OSM : sans abréviation, sans majuscule systématique en début de mot.

Testé avec Python 2.7.6
