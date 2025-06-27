import os
import pandas as pd
import streamlit as st
import pymongo
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration de la page
st.set_page_config(
    page_title="Intégration PostgreSQL & MongoDB",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Application de test Streamlit avec PostgreSQL et MongoDB")
st.markdown("---")

# Sidebar
st.sidebar.title("Navigation")
option = st.sidebar.selectbox(
    "Choisissez une section:",
    ["Accueil", "PostgreSQL", "MongoDB"]
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

# Footer
st.markdown("---")
st.markdown("📦 Application Streamlit avec PostgreSQL & MongoDB - version dockerisée.")
