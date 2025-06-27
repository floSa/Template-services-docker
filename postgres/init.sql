-- Script d'initialisation PostgreSQL simplifié
-- Ce script s'exécute à chaque démarrage du conteneur

-- Créer la iris users si elle n'existe pas

-- Créer la table iris si elle n'existe pas
CREATE TABLE IF NOT EXISTS iris (
    id               INTEGER PRIMARY KEY,
    sepal_length_cm  DOUBLE PRECISION,
    sepal_width_cm   DOUBLE PRECISION,
    petal_length_cm  DOUBLE PRECISION,
    petal_width_cm   DOUBLE PRECISION,
    species          VARCHAR(50)
);

-- Importer les données du fichier CSV (avec en-tête)
COPY iris(id, sepal_length_cm, sepal_width_cm, petal_length_cm, petal_width_cm, species)
FROM '/docker-entrypoint-initdb.d/Iris.csv'
DELIMITER ','
CSV HEADER;


\echo 'Initialisation de la base de données terminée !';
