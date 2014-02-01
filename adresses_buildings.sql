DROP TABLE IF EXISTS tmp_parcelles_union__com__ CASCADE;
CREATE TABLE tmp_parcelles_union__com__
AS
SELECT ST_Union(geometrie) AS geometrie,
		numero,
		voie
FROM	tmp_parcelles__com__
GROUP BY 2,3;

DROP TABLE IF EXISTS tmp_parcelles_union_buffer__com__ CASCADE;
CREATE TABLE tmp_parcelles_union_buffer__com__
AS
SELECT ST_Buffer(geometrie,1,'quad_segs=2') AS geometrie,
		numero,
		voie
FROM	tmp_parcelles_union__com__;

CREATE INDEX gidx_tmp_building__com__ 
ON tmp_building__com__
USING GIST(geometrie);

DROP TABLE IF EXISTS bulding_parcelle__com__ CASCADE;
CREATE TABLE bulding_parcelle__com__
AS
SELECT b.*,
		p.numero,
		p.voie
FROM tmp_parcelles_union_buffer__com__ p
JOIN tmp_building__com__ b
ON ST_Contains(p.geometrie,b.geometrie);

-- Election des batiments
--1 batiments en dur de + de 15m2 au sol
DROP TABLE IF EXISTS batiments_possibles__com__ CASCADE;
CREATE TABLE batiments_possibles__com__
AS
SELECT 	b.*,1 etape
FROM	bulding_parcelle b
WHERE	ST_Area(b.geometrie) > 15 AND
		b.wall != 'no';
--2 batiments legers de + de 15m2 au sol
INSERT INTO batiments_possibles__com__
SELECT 	b.*,2 etape
FROM	bulding_parcelle__com__ b
LEFT OUTER JOIN batiments_possibles__com__ bj
ON		b.numero = bj.numero 		AND
		b.voie = bj.voie
WHERE	ST_Area(b.geometrie) > 15 	AND
		b.wall = 'no' 				AND
		bj.numero IS NULL;
--3 le + grand batiment pour les parcelles restantes
INSERT INTO batiments_possibles__com__
SELECT 	b.*,3 etape
FROM	bulding_parcelle__com__ b
JOIN 	(SELECT id_building,rank() OVER (PARTITION BY numero,voie ORDER BY ST_Area(geometrie) desc) rang
		FROM bulding_parcelle__com__)r
ON	b.id_building = r.id_building
LEFT OUTER JOIN bulding_parcelle__com__ bj
ON		b.numero = bj.numero 	AND
		b.voie = bj.voie
WHERE	r.rang = 1 				AND
		bj.numero IS NULL;
		
DROP TABLE IF EXISTS bulding_mono_parcelle__com__ CASCADE;
CREATE TABLE bulding_mono_parcelle__com__
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
FROM	bulding_mono_parcelle__com__ b
JOIN	tmp_adresses__com__ a
ON	a.voie = b.voie AND
	a.numero = b.numero;

DROP TABLE IF EXISTS buildings_complementaires__com__ CASCADE;
CREATE TABLE buildings_complementaires__com__
AS
SELECT id_building,
		voie
FROM	bulding_parcelle__com__
EXCEPT
SELECT id_building,
		voie
FROM	adresse_sur_buildings__com__;

DROP TABLE IF EXISTS buildings_hors_voies__com__ CASCADE;
CREATE TABLE buildings_hors_voies__com__
AS
SELECT id_building
FROM	tmp_building__com__
EXCEPT
(SELECT id_building
FROM	adresse_sur_buildings__com__
UNION
SELECT id_building
FROM	buildings_complementaires__com__);

-- rabbatement des points Adresse
--- Impossible de rabattre sur un batiment hors parcelle mono adresse
UPDATE 	tmp_building_segments__com__
SET 	eligible = 0
WHERE 	id_building IN (SELECT id_building
						FROM	buildings_complementaires__com__);
--- Impossible de rabattre sur un batiment hors parcelle mono adresse
UPDATE 	tmp_building_segments__com__
SET 	eligible = 0
WHERE 	id_building IN (SELECT id_building
						FROM	buildings_hors_voies__com__) AND
		eligible = 1;
						
--- Impossible de rabattre sur un segment mitoyen
UPDATE	tmp_building_segments__com__
SET		eligible = 0
WHERE	id_node1||'-'||id_node2 IN (SELECT nd
									FROM	(SELECT id_node1||'-'||id_node2 nd
											FROM	tmp_building_segments__com__
											UNION ALL
											SELECT id_node2||'-'||id_node1
											FROM	tmp_building_segments__com__)a
									GROUP BY 1
									HAVING count(*) > 1) AND
		eligible = 1;

--- Priorite aux segments de + de 2m
UPDATE 	tmp_building_segments__com__
SET 	eligible = 0
WHERE 	ST_Length(geometrie) < 2 AND
		eligible = 1 AND
		id_building IN (SELECT id_building
						FROM	tmp_building_segments__com__
						WHERE 	eligible = 1 AND
						ST_Length(geometrie) > 2);

DROP TABLE IF EXISTS centres_segments__com__ CASCADE;
CREATE TABLE centres_segments__com__
AS
SELECT ST_Centroid(geometrie) geometrie,
	id_building,
	id_node1,
	id_node2,
	indice_node_1
FROM	tmp_building_segments__com__
WHERE	eligible = 1;

DROP TABLE IF EXISTS points_adresse_sur_building__com__ CASCADE;
CREATE TABLE points_adresse_sur_building__com__
AS
SELECT *
FROM
	(SELECT c.*,
			ST_X(ST_Transform(c.geometrie,4326)) lon,
			ST_Y(ST_Transform(c.geometrie,4326)) lat,
			ab.numero,
			ab.voie,
			RANK() OVER(PARTITION BY ab.numero,ab.voie ORDER BY ST_Distance(c.geometrie,a.geometrie)) rang
	FROM	centres_segments__com__ c
	JOIN	adresse_sur_buildings__com__ ab
	ON		c.id_building = ab.id_building
	JOIN	tmp_adresses__com__ a
	ON		ab.numero = a.numero AND
			ab.voie = a.voie)a
WHERE a.rang = 1;