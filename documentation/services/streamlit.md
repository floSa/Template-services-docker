# streamlit

## 📌 Présentation du Service
Interface web de **test et démonstration** des autres services. C'est la seule façade
visible par l'utilisateur : elle regroupe, dans une même application, un accès à
PostgreSQL, MongoDB, Ollama et MinIO via une barre latérale de navigation.

Concrètement, l'app joue le rôle de « tableau de bord de vérification » du template :
depuis le navigateur, on insère et affiche des lignes Iris dans chaque base, on dialogue
avec le LLM local, et on parcourt/téléverse des images dans le stockage objet — sans
écrire une ligne de code.

## 🔗 Accès au service
- URL : `http://localhost:8501` (port `${STREAMLIT_PORT}` = `8501`).
- Image construite depuis `streamlit/Dockerfile` (`python:3.12-slim`).
- Container : `streamlit_app`.
- Sonde : `GET /healthz`.

## 🗂️ Structure et définition des données
Code : `streamlit/src/app.py`. Sections (barre latérale) :

| Section | Ce qu'elle fait | Service ciblé |
|---|---|---|
| Accueil | Affiche les variables d'environnement détectées | — |
| PostgreSQL | Formulaire d'insertion + affichage des 5 dernières lignes `iris` | `postgres` |
| MongoDB | Formulaire d'insertion + affichage des 5 derniers documents `iris` | `mongodb` |
| Ollama | Sélection de modèle + chat (`/api/tags`, `/api/generate`) | `ollama` |
| MinIO | Affiche les 3 dernières images du bucket + upload | `minio` |

Variables d'environnement utilisées (via `.env`) : `DATABASE_URL` /
`POSTGRES_*`, `MONGO_*`, `OLLAMA_URL` (défaut `http://ollama:11434`),
`MINIO_HOST`/`MINIO_PORT`/`MINIO_ROOT_USER`/`MINIO_ROOT_PASSWORD`/`MINIO_BUCKET_NAME`.

## 💻 Commandes Utiles
```bash
docker compose up -d --build streamlit
docker compose logs -f streamlit
# rebuild après modif des dépendances :
docker compose build streamlit
```
Le code est monté à chaud (`./streamlit/src:/app/src`) : une modification de `app.py` est
prise en compte au rechargement Streamlit sans rebuild.

## 🛠️ Problèmes rencontrés et Solutions
- **Problème** : la section MinIO utilise `use_column_width` (`app.py:224`).
  **Cause** : paramètre déprécié dans les versions récentes de Streamlit.
  **Solution** : ce n'est pas bloquant avec `streamlit==1.28.2` (version épinglée) ; à
  migrer vers `use_container_width` en cas de montée de version. `<à confirmer>`
- **Problème** : erreur de connexion à un service au démarrage.
  **Cause** : service non encore prêt.
  **Solution** : `streamlit` attend déjà `postgres`, `mongodb` et `ollama` en
  `service_healthy` ; vérifier les logs du service concerné si l'erreur persiste.

## Dépendances / Port
Dépend de `ollama`, `postgres`, `mongodb` (`condition: service_healthy`). Port exposé :
`8501`. Dépendances Python figées dans `streamlit/requirements.txt`.
