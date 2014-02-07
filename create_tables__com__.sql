DROP TABLE IF EXISTS building__com__ CASCADE;
					CREATE TABLE building__com__
					(geometrie geometry,
					id_building double precision,
					wall character varying (250));

DROP TABLE IF EXISTS building_segments__com__ CASCADE;
					CREATE TABLE building_segments__com__
					(geometrie geometry,
					id_building double precision,
					id_node1 double precision,
					id_node2 double precision,
					indice_node_1 integer,
					eligible integer default 1);

DROP TABLE IF EXISTS parcelles__com__ CASCADE;
					CREATE TABLE parcelles__com__ 
					(geometrie geometry,
					id_parcelle double precision,
					numero character varying(50),
					voie character varying (250));

DROP TABLE IF EXISTS adresses__com__ CASCADE;
					CREATE TABLE adresses__com__
					(geometrie geometry,
					id_adresse double precision,
					numero character varying(50),
					voie character varying (250));

COMMIT;
					