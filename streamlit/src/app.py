import os
import pandas as pd
import streamlit as st
import pymongo
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import requests
import json
from minio import Minio
import io


# Accès au service streamlit à l'adresse http://localhost:8501/ 

# Chargement des variables d'environnement
load_dotenv()

# Configuration de la page
st.set_page_config(
    page_title="Intégration PostgreSQL & MongoDB",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Application de test Streamlit avec PostgreSQL, MongoDB et Ollama")
st.markdown("---")

# Sidebar
st.sidebar.title("Navigation")
option = st.sidebar.selectbox(
    "Choisissez une section:",
    ["Accueil", "PostgreSQL", "MongoDB", "Ollama", "Minio"]
)

if option == "Accueil":
    st.subheader("🏠 Accueil")
    st.write("Bienvenue dans l'application. Utilisez la sidebar pour accéder aux différentes sections.")
    
    st.subheader("🔧 Variables d'environnement détectées")
    cols = st.columns(2)
    with cols[0]:
        st.write("**PostgreSQL**")
        for var in ['POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB', 'POSTGRES_PORT']:
            st.write(f"- {var}: {os.getenv(var, '❌ Non défini')}")
    with cols[1]:
        st.write("**MongoDB**")
        for var in ['MONGO_ROOT_USERNAME', 'MONGO_ROOT_PASSWORD', 'MONGO_DB', 'MONGO_PORT']:
            st.write(f"- {var}: {os.getenv(var, '❌ Non défini')}")

elif option == "PostgreSQL":
    st.subheader("🐘 PostgreSQL : Insertion et affichage")

    try:
        # Connexion
        db_url = os.getenv("DATABASE_URL") or f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
        engine = create_engine(db_url)

        # Formulaire d'insertion
        with st.form("pg_insert_form"):
            st.markdown("### ➕ Ajouter un enregistrement dans `iris`")
            col1, col2, col3 = st.columns(3)
            with col1:
                sepal_length = st.number_input("Sepal Length (cm)", min_value=0.0, step=0.1)
                petal_length = st.number_input("Petal Length (cm)", min_value=0.0, step=0.1)
            with col2:
                sepal_width = st.number_input("Sepal Width (cm)", min_value=0.0, step=0.1)
                petal_width = st.number_input("Petal Width (cm)", min_value=0.0, step=0.1)
            with col3:
                species = st.selectbox("Species", ["setosa", "versicolor", "virginica"])
                submitted = st.form_submit_button("Insérer")

            if submitted:
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT COALESCE(MAX(id), 0) FROM iris"))
                    max_id = result.scalar()
                    new_row = pd.DataFrame([{
                        "id": max_id + 1,
                        "sepal_length_cm": sepal_length,
                        "sepal_width_cm": sepal_width,
                        "petal_length_cm": petal_length,
                        "petal_width_cm": petal_width,
                        "species": species
                    }])
                    new_row.to_sql("iris", engine, if_exists="append", index=False)
                    st.success("✅ Ligne insérée dans PostgreSQL.")

        # Bouton d'affichage
        if st.button("📥 Afficher les 5 derniers enregistrements"):
            df = pd.read_sql("""
                SELECT id, sepal_length_cm, sepal_width_cm, 
                       petal_length_cm, petal_width_cm, species
                FROM iris ORDER BY id DESC LIMIT 5
            """, engine)
            st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Erreur PostgreSQL : {e}")

elif option == "MongoDB":
    st.subheader("🍃 MongoDB : Insertion et affichage")

    try:
        # Connexion
        mongo_uri = f"mongodb://{os.getenv('MONGO_ROOT_USERNAME')}:{os.getenv('MONGO_ROOT_PASSWORD')}@{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}?authSource=admin"
        client = pymongo.MongoClient(mongo_uri)
        db = client[os.getenv("MONGO_DB")]
        collection = db["iris"]

        # Formulaire d'insertion
        with st.form("mongo_insert_form"):
            st.markdown("### ➕ Ajouter un document dans `iris`")
            col1, col2, col3 = st.columns(3)
            with col1:
                sepal_length = st.number_input("Sepal Length (cm)", min_value=0.0, step=0.1, key="mongo_sl")
                petal_length = st.number_input("Petal Length (cm)", min_value=0.0, step=0.1, key="mongo_pl")
            with col2:
                sepal_width = st.number_input("Sepal Width (cm)", min_value=0.0, step=0.1, key="mongo_sw")
                petal_width = st.number_input("Petal Width (cm)", min_value=0.0, step=0.1, key="mongo_pw")
            with col3:
                species = st.selectbox("Species", ["setosa", "versicolor", "virginica"], key="mongo_sp")
                submitted = st.form_submit_button("Insérer")

            if submitted:
                last_doc = collection.find_one(sort=[("Id", -1)])
                new_id = (last_doc["Id"] + 1) if last_doc else 1
                doc = {
                    "Id": new_id,
                    "SepalLengthCm": sepal_length,
                    "SepalWidthCm": sepal_width,
                    "PetalLengthCm": petal_length,
                    "PetalWidthCm": petal_width,
                    "Species": species
                }
                collection.insert_one(doc)
                st.success("✅ Document inséré dans MongoDB.")

        # Bouton d'affichage
        if st.button("📥 Afficher les 5 derniers documents"):
            docs = collection.find({}, {"_id": 0}).sort("Id", -1).limit(5)
            df = pd.DataFrame(list(docs))
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Aucun document trouvé.")

    except Exception as e:
        st.error(f"❌ Erreur MongoDB : {e}")

elif option == "Ollama":
    st.subheader("🧠 Ollama : Chat avec un modèle")

    base_url = os.getenv("OLLAMA_URL", "http://ollama:11434")

    # Étape 1 : Charger la liste des modèles disponibles
    try:
        tags_response = requests.get(f"{base_url}/api/tags")
        tags_response.raise_for_status()
        models = tags_response.json().get("models", [])
        model_names = [model["name"] for model in models]

        if not model_names:
            st.warning("⚠️ Aucun modèle Ollama disponible.")
        else:
            # Étape 2 : Choisir un modèle
            selected_model = st.selectbox("🧠 Choisissez un modèle Ollama :", model_names)

            # Étape 3 : Interface de chatbot
            st.markdown("### 💬 Chatbot")
            default_prompt = "Peux-tu te présenter ?"
            user_input = st.text_area("🗨️ Votre question :", value=default_prompt, height=100)

            if st.button("Envoyer la requête au modèle"):
                with st.spinner("Réponse en cours..."):
                    try:
                        chat_payload = {
                                        "model": selected_model,
                                        "prompt": user_input,
                                        "stream": False  # 🔧 Ajouter cette ligne
                                    }
                        chat_response = requests.post(f"{base_url}/api/generate", json=chat_payload)
                        chat_response.raise_for_status()
                        answer = chat_response.json().get("response", "❌ Aucune réponse.")
                        st.success("✅ Réponse du modèle :")
                        st.write(answer)
                    except Exception as e:
                        st.error(f"❌ Erreur lors de la génération : {e}")
    except Exception as e:
        st.error(f"❌ Erreur de connexion à Ollama : {e}")

elif option == "Minio":
    st.subheader("📦 MinIO : Gestion des images")

    # Initialisation du client MinIO
    minio_host = os.getenv("MINIO_HOST", "minio")
    minio_port = os.getenv("MINIO_PORT", "9000")
    access_key = os.getenv("MINIO_ROOT_USER")
    secret_key = os.getenv("MINIO_ROOT_PASSWORD")
    bucket = os.getenv("MINIO_BUCKET_NAME")

    client = Minio(
        f"{minio_host}:{minio_port}",
        access_key=access_key,
        secret_key=secret_key,
        secure=False
    )

    st.markdown("### 🖼️ Afficher les 3 dernières images du bucket")
    if st.button("🔄 Charger les images"):
        try:
            objs = client.list_objects(bucket, recursive=True)
            derniers = sorted(objs, key=lambda o: o.last_modified, reverse=True)[:3]
            if derniers:
                cols = st.columns(3)
                for col, obj in zip(cols, derniers):
                    # Récupérer l'objet en mémoire
                    response = client.get_object(bucket, obj.object_name)
                    image_data = response.read()
                    response.close()
                    response.release_conn()
                    # Afficher
                    col.image(
                        io.BytesIO(image_data),
                        caption=obj.object_name,
                        use_column_width=True
                    )
            else:
                st.info("Aucune image dans le bucket.")
        except Exception as e:
            st.error(f"Erreur lecture bucket MinIO : {e}")

    st.markdown("---")
    st.markdown("### ➕ Charger une nouvelle image")
    uploaded = st.file_uploader(
        "Sélectionnez une image à uploader",
        type=["png", "jpg", "jpeg"]
    )
    if uploaded and st.button("📤 Envoyer vers MinIO"):
        try:
            client.put_object(
                bucket_name=bucket,
                object_name=uploaded.name,
                data=uploaded,
                length=uploaded.size,
                content_type=uploaded.type
            )
            st.success(f"Image « {uploaded.name} » uploadée !")
        except Exception as e:
            st.error(f"Erreur upload MinIO : {e}")



# Footer
st.markdown("---")
st.markdown("📦 Application Streamlit avec PostgreSQL, MongoDB, Ollama - version dockerisée.")
