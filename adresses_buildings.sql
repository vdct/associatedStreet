DROP TABLE IF EXISTS tmp_parcelles_union CASCADE;
CREATE TABLE tmp_parcelles_union
AS
SELECT ST_Union(geometrie) AS geometrie,
		numero,
		voie
FROM	tmp_parcelles
GROUP BY 2,3;

DROP TABLE IF EXISTS tmp_parcelles_union_buffer CASCADE;
CREATE TABLE tmp_parcelles_union_buffer
AS
SELECT ST_Buffer(geometrie,1,'quad_segs=2') AS geometrie,
		numero,
		voie
FROM	tmp_parcelles_union;

DROP TABLE IF EXISTS bulding_parcelle CASCADE;
CREATE TABLE bulding_parcelle
AS
SELECT b.*,
		p.numero,
		p.voie
FROM tmp_parcelles_union_buffer p
JOIN tmp_building b
ON ST_Contains(p.geometrie,b.geometrie);

-- Election des batiments
--1 batiments en dur de + de 15m2 au sol
DROP TABLE IF EXISTS batiments_possibles CASCADE;
CREATE TABLE batiments_possibles
AS
SELECT 	b.*,1 etape
FROM	bulding_parcelle b
WHERE	ST_Area(b.geometrie) > 15 AND
		b.wall != 'no';
--2 batiments legers de + de 15m2 au sol
INSERT INTO batiments_possibles
SELECT 	b.*,2 etape
FROM	bulding_parcelle b
LEFT OUTER JOIN batiments_possibles bj
ON		b.numero = bj.numero 		AND
		b.voie = bj.voie
WHERE	ST_Area(b.geometrie) > 15 	AND
		b.wall = 'no' 				AND
		bj.numero IS NULL;
--3 le + grand batiment pour les parcelles restantes
INSERT INTO batiments_possibles
SELECT 	b.*,3 etape
FROM	bulding_parcelle b
JOIN 	(SELECT id_building,rank() OVER (PARTITION BY numero,voie ORDER BY ST_Area(geometrie) desc) rang
		FROM bulding_parcelle)r
ON	b.id_building = r.id_building
LEFT OUTER JOIN bulding_parcelle bj
ON		b.numero = bj.numero 	AND
		b.voie = bj.voie
WHERE	r.rang = 1 				AND
		bj.numero IS NULL;
		
DROP TABLE IF EXISTS bulding_mono_parcelle CASCADE;
CREATE TABLE bulding_mono_parcelle
AS
SELECT bp.geometrie,
	bp.id_building,
	bp.numero,
	bp.voie
FROM	(SELECT id_building
		FROM	batiments_possibles
		GROUP BY 1
		HAVING COUNT(*) = 1) bm
JOIN batiments_possibles bp
ON bm.id_building = bp.id_building;

DROP TABLE IF EXISTS adresse_sur_buildings CASCADE;
CREATE TABLE adresse_sur_buildings
AS
SELECT b.id_building,
	a.id_adresse,
	b.numero,
	b.voie
FROM	bulding_mono_parcelle b
JOIN	tmp_adresses a
ON	a.voie = b.voie AND
	a.numero = b.numero;

DROP TABLE IF EXISTS buildings_complementaires CASCADE;
CREATE TABLE buildings_complementaires
AS
SELECT id_building,
		voie
FROM	bulding_parcelle
EXCEPT
SELECT id_building,
		voie
FROM	adresse_sur_buildings;

DROP TABLE IF EXISTS buildings_hors_voies CASCADE;
CREATE TABLE buildings_hors_voies
AS
SELECT id_building
FROM	tmp_building
EXCEPT
(SELECT id_building
FROM	adresse_sur_buildings
UNION
SELECT id_building
FROM	buildings_complementaires);

-- rabbatement des points Adresse
UPDATE 	tmp_building_segments
SET 	eligible = 0
WHERE 	id_building IN (SELECT id_building
						FROM	buildings_complementaires);
UPDATE 	tmp_building_segments
SET 	eligible = 0
WHERE 	id_building IN (SELECT id_building
						FROM	buildings_hors_voies) AND
		eligible = 1;
						
UPDATE	tmp_building_segments
SET		eligible = 0
WHERE	id_node1||'-'||id_node2 IN (SELECT id_node1||'-'||id_node2
								FROM	tmp_building_segments
								WHERE 	eligible = 0
								UNION
								SELECT id_node2||'-'||id_node1
								FROM	tmp_building_segments
								WHERE 	eligible = 0) AND
		eligible = 1;

UPDATE 	tmp_building_segments
SET 	eligible = 0
WHERE 	ST_Length(geometrie) < 2 AND
		eligible = 1;

DROP TABLE IF EXISTS centres_segments CASCADE;
CREATE TABLE centres_segments
AS
SELECT ST_Centroid(geometrie) geometrie,
	id_building,
	id_node1,
	id_node2,
	indice_node_1
FROM	tmp_building_segments
WHERE	eligible = 1;

DROP TABLE IF EXISTS points_adresse_sur_building CASCADE;
CREATE TABLE points_adresse_sur_building
AS
SELECT *
FROM
	(SELECT c.*,
			ST_X(ST_Transform(c.geometrie,4326)) lon,
			ST_Y(ST_Transform(c.geometrie,4326)) lat,
			ab.numero,
			ab.voie,
			RANK() OVER(PARTITION BY ab.numero,ab.voie ORDER BY ST_Distance(c.geometrie,a.geometrie)) rang
	FROM	centres_segments c
	JOIN	adresse_sur_buildings ab
	ON		c.id_building = ab.id_building
	JOIN	tmp_adresses a
	ON		ab.numero = a.numero AND
			ab.voie = a.voie)a
WHERE a.rang = 1;