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
SELECT b.geometrie geometrie_building,
	b.id id_building,
	p.geometrie geometrie_parcelle,
	p.numero,
	p.voie
FROM tmp_parcelles_union_buffer p
JOIN tmp_building b
ON ST_Contains(p.geometrie,b.geometrie);

DROP TABLE IF EXISTS bulding_mono_parcelle CASCADE;
CREATE TABLE bulding_mono_parcelle
AS
SELECT bp.geometrie_building,
	bp.id_building,
	bp.numero,
	bp.voie
FROM
(SELECT id_building
FROM	bulding_parcelle
GROUP BY 1
HAVING COUNT(*) = 1) bm
JOIN bulding_parcelle bp
ON bm.id_building = bp.id_building;

DROP TABLE IF EXISTS adresse_sur_buildings CASCADE;
CREATE TABLE adresse_sur_buildings
AS
SELECT b.id_building,
	a.id id_adresse,
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