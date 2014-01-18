addr2associatedStreet.py : regroupement des adresses du cadastre dans des relations "associatedStreet"

En entrée : les fichiers de type parcelles-adresses.osm produits ici : http://37.187.60.59/cadastre-housenumber/adresses.php

En sortie, un répertoire "fichiers_"+"nom du fichier d'adresses" dans le répertoire du script.

Les fichier en sortie reprennent toutes les adresses indiquées en entrée, dès lors qu'elles commencent par un numéro. Un point d'adresse est fabriqué pour chaque numéro. Lorsque plusieurs points correspondent au même numero dans le fichier d'entrée, c'est la moyenne des coordonnées des points qui est utilisée en sortie.
Chaque point (node) a un unique tag : addr:housenumber.
Chaque point est rattaché à une relation de type associatedStreet qui porte le nom de la rue telle que donnée par le cadastre.
Un fichier est créé par relation associatedStreet, il porte comme nom celui de la voie.

Les fichiers en sortie n'ont pas vocation à être envoyés vers la base OSM. Chaque point d'adresse doit être replacé sur un bâtiment (ou, selon les pratiques, en limite de propriété). Le cas échéant, le point doit être intégré au contour d'un bâtiment. Même sans vraie convention, les noms dans les relations associatedStreet devraient reprendre les noms portés par les rues dans OSM : sans abréviation, sans majuscule systématique en début de mot. Le code Fantoir n'est pas présent dans les fichiers produits.

Testé avec Python 2.7.6
