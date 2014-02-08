DROP TABLE IF EXISTS parcelles_union__com__ CASCADE;
CREATE TABLE parcelles_union__com__
AS
SELECT ST_Union(geometrie) AS geometrie,
		numero,
		voie
FROM	parcelles__com__
GROUP BY 2,3;

DROP TABLE IF EXISTS parcelles_union_buffer__com__ CASCADE;
CREATE TABLE parcelles_union_buffer__com__
AS
SELECT ST_Buffer(geometrie,1,'quad_segs=2') AS geometrie,
		numero,
		voie
FROM	parcelles_union__com__;

CREATE INDEX gidx_building__com__ 
ON building__com__
USING GIST(geometrie);

DROP TABLE IF EXISTS building_parcelle__com__ CASCADE;
CREATE TABLE building_parcelle__com__
AS
SELECT b.*,
		p.numero,
		p.voie
FROM parcelles_union_buffer__com__ p
JOIN building__com__ b
ON ST_Contains(p.geometrie,b.geometrie);

-- Election des batiments
--1 batiments en dur de + de 25m2 au sol
DROP TABLE IF EXISTS batiments_possibles__com__ CASCADE;
CREATE TABLE batiments_possibles__com__
AS
SELECT 	b.*,1 etape
FROM	building_parcelle__com__ b
WHERE	ST_Area(b.geometrie) > 25 AND
		b.wall != 'no';
--2 batiments en dur de + de 15m2 au sol
INSERT INTO batiments_possibles__com__
SELECT 	b.*,2 etape
FROM	building_parcelle__com__ b
LEFT OUTER JOIN batiments_possibles__com__ bj
ON		b.numero = bj.numero 		AND
		b.voie = bj.voie
WHERE	ST_Area(b.geometrie) > 15 	AND
		b.wall != 'no' 				AND
		bj.numero IS NULL;
--3 batiments legers de + de 30m2 au sol
INSERT INTO batiments_possibles__com__
SELECT 	b.*,3 etape
FROM	building_parcelle__com__ b
LEFT OUTER JOIN batiments_possibles__com__ bj
ON		b.numero = bj.numero 		AND
		b.voie = bj.voie
WHERE	ST_Area(b.geometrie) > 30 	AND
		b.wall = 'no' 				AND
		bj.numero IS NULL;
--4 le + grand batiment pour les parcelles restantes
INSERT INTO batiments_possibles__com__
SELECT 	b.*,3 etape
FROM	building_parcelle__com__ b
JOIN 	(SELECT id_building,rank() OVER (PARTITION BY numero,voie ORDER BY ST_Area(geometrie) desc) rang
		FROM building_parcelle__com__)r
ON	b.id_building = r.id_building
LEFT OUTER JOIN building_parcelle__com__ bj
ON		b.numero = bj.numero 	AND
		b.voie = bj.voie
WHERE	r.rang = 1 				AND
		bj.numero IS NULL;
		
DROP TABLE IF EXISTS building_mono_parcelle__com__ CASCADE;
CREATE TABLE building_mono_parcelle__com__
AS
SELECT bp.geometrie,
	bp.id_building,
	bp.numero,
	bp.voie
FROM	(SELECT id_building
		FROM	batiments_possibles__com__
		GROUP BY 1
		HAVING COUNT(*) = 1) bm
JOIN batiments_possibles__com__ bp
ON bm.id_building = bp.id_building;

DROP TABLE IF EXISTS adresse_sur_buildings__com__ CASCADE;
CREATE TABLE adresse_sur_buildings__com__
AS
SELECT b.id_building,
	a.id_adresse,
	b.numero,
	b.voie
FROM	building_mono_parcelle__com__ b
JOIN	adresses__com__ a
ON	a.voie = b.voie AND
	a.numero = b.numero;

DROP TABLE IF EXISTS buildings_complementaires__com__ CASCADE;
CREATE TABLE buildings_complementaires__com__
AS
SELECT id_building,
		voie
FROM	building_parcelle__com__
EXCEPT
SELECT id_building,
		voie
FROM	adresse_sur_buildings__com__;

DROP TABLE IF EXISTS buildings_hors_voies__com__ CASCADE;
CREATE TABLE buildings_hors_voies__com__
AS
SELECT id_building
FROM	building__com__
EXCEPT
(SELECT id_building
FROM	adresse_sur_buildings__com__
UNION
SELECT id_building
FROM	buildings_complementaires__com__);

-- rabbatement des points Adresse
--- Impossible de rabattre sur un batiment hors parcelle mono adresse
ALTER TABLE building_segments__com__ ADD COLUMN etape INTEGER;
UPDATE 	building_segments__com__
SET 	eligible = 0,
		etape = 1
WHERE 	id_building IN (SELECT id_building
						FROM	buildings_complementaires__com__);
--- Impossible de rabattre sur un batiment hors parcelle
UPDATE 	building_segments__com__
SET 	eligible = 0,
		etape = 2
WHERE 	id_building IN (SELECT id_building
						FROM	buildings_hors_voies__com__) AND
		eligible = 1;
						
--- Impossible de rabattre sur un segment mitoyen (building)
UPDATE	building_segments__com__
SET		eligible = 0,
		etape = 3
WHERE	id_node1||'-'||id_node2 IN (SELECT nd
									FROM	(SELECT id_node1||'-'||id_node2 nd
											FROM	building_segments__com__
											UNION ALL
											SELECT id_node2||'-'||id_node1
											FROM	building_segments__com__)a
									GROUP BY 1
									HAVING count(*) > 1) AND
		eligible = 1;

--- Impossible de rabattre sur un segment mitoyen (parcelle)
UPDATE	building_segments__com__
SET		eligible = 0,
		etape = 4
WHERE	id_node1||'-'||id_node2 IN (SELECT 	b.id_node1||'-'||b.id_node2 nd
									FROM	building_segments__com__ b
									JOIN	parcelles_union_buffer__com__ p
									ON		ST_Contains(p.geometrie,b.geometrie)
									WHERE	b.eligible = 1
									GROUP BY 1
									HAVING COUNT(*) > 1) AND
		eligible = 1;
	
--- Priorite aux segments de + de 2m quand ils existent parmi les eligibles
UPDATE 	building_segments__com__
SET 	eligible = 0,
		etape = 5
WHERE 	ST_Length(geometrie) < 2 AND
		eligible = 1 AND
		id_building IN (SELECT id_building
						FROM	building_segments__com__
						WHERE 	eligible = 1 AND
						ST_Length(geometrie) > 2);

DROP TABLE IF EXISTS centres_segments__com__ CASCADE;
CREATE TABLE centres_segments__com__
WITH (OIDS=TRUE)
AS
SELECT ST_Centroid(geometrie) geometrie,
	id_building,
	id_node1,
	id_node2,
	indice_node_1
FROM	building_segments__com__
WHERE	eligible = 1;

-- Detection des grandes facades
-- uniquement pour les batiments dont le cercle englobant est inscrit dans la parcelle de l'adresse
-- pour limiter aux batiments des residences contrairement à ceux avec façade sur rue
-- dont l'axe est perpendiculaire à la rue
DROP TABLE IF EXISTS buildings_mitoyens__com__ CASCADE;
CREATE TABLE buildings_mitoyens__com__
AS
SELECT b.id_building
FROM building_segments__com__ b
JOIN 	(SELECT id_node1
	FROM	(SELECT id_node1 FROM building_segments__com__
		UNION ALL
		SELECT id_node2 FROM building_segments__com__)a
	GROUP BY 1
	HAVING count(*) > 3) n
ON n.id_node1 = b.id_node1
UNION
SELECT b.id_building
FROM building_segments__com__ b
JOIN 	(SELECT id_node1
	FROM	(SELECT id_node1 FROM building_segments__com__
		UNION ALL
		SELECT id_node2 FROM building_segments__com__)a
	GROUP BY 1
	HAVING count(*) > 3) n
ON n.id_node1 = b.id_node2;

DROP TABLE IF EXISTS mbc__com__ CASCADE;
CREATE TABLE mbc__com__
WITH (OIDS=TRUE)
AS
SELECT ST_MinimumBoundingCircle(geometrie,4) geometrie_cercle,
		ST_Area(geometrie)::integer surface_building,
		0::integer surface_cercle,
		b.id_building,
		ST_Centroid(geometrie) geometrie_centroid
FROM 	building_mono_parcelle__com__ b
LEFT OUTER JOIN buildings_mitoyens__com__ m
ON		b.id_building = m.id_building AND
		m.id_building IS NULL;

DELETE FROM mbc__com__
WHERE oid NOT IN	(SELECT mbc.oid
					FROM 	mbc__com__ mbc
					JOIN	parcelles_union_buffer__com__ p
					ON		ST_Contains(p.geometrie,mbc.geometrie_cercle));
					
UPDATE mbc__com__
SET surface_cercle = ST_Area(geometrie_cercle);

-- Pour les grandes facades, on retient comme possible point d'accroche
-- les 2 plus proches du centroide de l'objet
DELETE FROM centres_segments__com__
WHERE oid IN (SELECT oid
			FROM	(SELECT c.oid,rank() over(partition by c.id_building order by ST_Distance(c.geometrie,m.geometrie_centroid))rang
					FROM mbc__com__ m
					JOIN	centres_segments__com__ c
					ON m.id_building = c.id_building
					WHERE m.surface_cercle > 3 * surface_building)s
			WHERE rang > 2);


DROP TABLE IF EXISTS points_adresse_sur_building__com__ CASCADE;
CREATE TABLE points_adresse_sur_building__com__
AS
SELECT *
FROM
	(SELECT c.*,
			ST_X(ST_Transform(c.geometrie,4326)) lon,
			ST_Y(ST_Transform(c.geometrie,4326)) lat,
			a.id_adresse,
			ab.numero,
			ab.voie,
			RANK() OVER(PARTITION BY ab.numero,ab.voie ORDER BY ST_Distance(c.geometrie,a.geometrie)) rang
	FROM	centres_segments__com__ c
	JOIN	adresse_sur_buildings__com__ ab
	ON		c.id_building = ab.id_building
	JOIN	adresses__com__ a
	ON		ab.numero = a.numero AND
			ab.voie = a.voie)a
WHERE a.rang = 1;

-- ajout des non elus de la voie dans les complementaires
INSERT INTO buildings_complementaires__com__
SELECT id_building,
		voie
FROM	adresse_sur_buildings__com__
EXCEPT
SELECT id_building,
		voie
FROM	points_adresse_sur_building__com__
COMMIT;