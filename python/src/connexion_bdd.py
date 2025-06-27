#!/usr/bin/env python3

import os
import pandas as pd
import sys
from datetime import datetime

##### PostgreSQL #####

from sqlalchemy import create_engine, text


def get_db_connection():
    """Créer la connexion à PostgreSQL via les variables d'environnement"""
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD') 
    host = os.getenv('POSTGRES_HOST', 'postgres')
    port = os.getenv('POSTGRES_PORT')
    database = os.getenv('POSTGRES_DB')
    
    if not all([user, password, port, database]):
        print("ERREUR : Variables d'environnement manquantes (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_PORT, POSTGRES_DB)")
        sys.exit(1)
    
    connection_url = f'postgresql://{user}:{password}@{host}:{port}/{database}'
    
    try:
        engine = create_engine(connection_url, echo=False)
        return engine
    except Exception as e:
        print(f"Erreur de connexion à la base : {e}")
        sys.exit(1)


def insert_new_records(engine):
    """Insérer deux nouveaux enregistrements dans la table iris"""
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COALESCE(MAX(id), 0) as max_id FROM iris"))
        max_id = result.scalar()
    
    new_data = pd.DataFrame({
        'id': [max_id + 1, max_id + 2],
        'sepal_length_cm': [5.8, 6.2],
        'sepal_width_cm': [2.7, 3.1], 
        'petal_length_cm': [4.1, 4.8],
        'petal_width_cm': [1.0, 1.8],
        'species': ['setosa', 'versicolor']
    })
    
    new_data.to_sql(
        name='iris',
        con=engine,
        if_exists='append',
        index=False,
        method='multi'
    )
    
    print(f"✓ Insertion de {len(new_data)} nouveaux enregistrements réussie")


def fetch_last_records(engine, limit=3):
    """Récupérer les derniers enregistrements de la table iris"""
    
    query = """
    SELECT id, sepal_length_cm, sepal_width_cm, 
           petal_length_cm, petal_width_cm, species
    FROM iris 
    ORDER BY id DESC 
    LIMIT 3
    """
    
    df_result = pd.read_sql_query(query, engine) # , params={"limit":limit}
    print(f"✓ Les {len(df_result)} derniers enregistrements :")
    print(df_result.to_string(index=False))
    return df_result


##### MongoDB #####

from pymongo import MongoClient


def get_mongo_connection():
    """Créer la connexion à MongoDB via les variables d'environnement"""
    user = os.getenv('MONGO_ROOT_USERNAME')
    password = os.getenv('MONGO_ROOT_PASSWORD')
    host = os.getenv('MONGO_HOST', 'mongodb_db')
    port = os.getenv('MONGO_PORT')
    database = os.getenv('MONGO_DB')
    
    if not all([user, password, port, database]):
        print("ERREUR : Variables d'environnement manquantes")
        sys.exit(1)
    
    connection_url = f"mongodb://{user}:{password}@{host}:{port}/{database}?authSource=admin"
    
    try:
        client = MongoClient(connection_url)
        # Test de la connexion
        client.admin.command('ping')
        return client
    except Exception as e:
        print(f"Erreur de connexion à la base : {e}")
        sys.exit(1)


def insert_new_records_mongo(collection):
    """Insérer deux nouveaux enregistrements dans la collection iris"""
    
    # Récupérer l'ID maximum pour générer les nouveaux IDs
    last_record = collection.find().sort("Id", -1).limit(1)
    print("~~~~~~~~~~~~~~ last_record", last_record[0])
    max_id = list(last_record)[0]["Id"] if collection.count_documents({}) > 0 else 0
    
    new_data = [
        {
            "Id": max_id + 1,
            "SepalLengthCm": 6.2,
            "SepalWidthCm": 3.8,
            "PetalLengthCm": 4.5,
            "PetalWidthCm": 1.3,
            "Species": "versicolor"
        },
        {
            "Id": max_id + 2,
            "SepalLengthCm": 7.1,
            "SepalWidthCm": 2.9,
            "PetalLengthCm": 5.8,
            "PetalWidthCm": 2.1,
            "Species": "virginica"
        }
    ]

    #{'_id': ObjectId('685d5d0652792039b134104d'), 'Id': 132, 'SepalLengthCm': 7.9, 'SepalWidthCm': 3.8, 'PetalLengthCm': 6.4, 'PetalWidthCm': 2.0, 'Species': 'Iris-virginica'}
    
    try:
        result = collection.insert_many(new_data)
        print(f"✓ Insertion de {len(result.inserted_ids)} nouveaux enregistrements réussie")
    except Exception as e:
        print(f"Erreur lors de l'insertion : {e}")
        sys.exit(1)


def fetch_last_records_mongo(collection, limit=3):
    """Récupérer les derniers enregistrements de la collection iris"""
    
    try:
        # Récupérer et trier par id décroissant
        cursor = collection.find(
            projection={"_id": 0, "id": 1, "sepal_length_cm": 1, 
                       "sepal_width_cm": 1, "petal_length_cm": 1, 
                       "petal_width_cm": 1, "species": 1}
        ).sort("id", -1).limit(limit)
        
        records = list(cursor)
        
        if records:
            # Conversion en DataFrame pour affichage uniforme
            df_result = pd.DataFrame(records)
            print(f"✓ Les {len(df_result)} derniers enregistrements :")
            print(df_result.to_string(index=False))
            return df_result
        else:
            print("Aucun enregistrement trouvé")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Erreur lors de la récupération : {e}")
        return pd.DataFrame()


def main():
    
    ##### PostgreSQL #####
    
    print("=== Traitement PostgreSQL ===")
    
    engine = get_db_connection()
    print("✓ Connexion PostgreSQL établie")
    
    insert_new_records(engine)
    fetch_last_records(engine, limit=3)
    
    engine.dispose()
    print("✓ Connexion PostgreSQL fermée\n")

    ##### MongoDB #####
    
    print("=== Traitement MongoDB ===")
    
    client = get_mongo_connection()
    print("✓ Connexion MongoDB établie")
    
    database = os.getenv('MONGO_DB')
    db = client[database]
    collection = db.iris

    insert_new_records_mongo(collection)
    fetch_last_records_mongo(collection, limit=3)
    
    client.close()
    print("✓ Connexion MongoDB fermée")


if __name__ == "__main__":
    main()
