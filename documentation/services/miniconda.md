# miniconda

## Description Générale
Conteneur de **calcul Python** basé sur Miniconda. Au démarrage, il attend PostgreSQL,
active un environnement conda, puis exécute `connexion_bdd.py` qui démontre les
opérations lecture/écriture sur PostgreSQL et MongoDB. Le conteneur reste ensuite vivant
pour permettre le debug interactif.

## Structure du Service
| Fichier | Rôle |
|---|---|
| `python/Dockerfile` | Image `continuumio/miniconda3`, installe le client `postgresql-client` et crée l'env conda |
| `python/environment.yml` | Définition de l'env conda `mon_env_test` (Python `3.11`) |
| `python/requirements.txt` | Dépendances Python (versions minimales) |
| `python/entrypoint.sh` | Attente Postgres → activation conda → exécution du script → `tail -f /dev/null` |
| `python/src/connexion_bdd.py` | Script principal (Postgres + Mongo) |
| `python/src/connexion_bdd.ipynb` | Notebook équivalent (Postgres, Mongo, test Ollama) |

## Spécifications / Pipeline
Déroulé de `python/entrypoint.sh` :

1. Attente active de PostgreSQL (`pg_isready`, boucle jusqu'à disponibilité).
2. Activation de l'environnement conda `mon_env_test`.
3. Affichage des paquets clés installés.
4. Exécution de `connexion_bdd.py` :
   - **PostgreSQL** : insertion de 2 lignes dans `iris`, lecture des 3 dernières ;
   - **MongoDB** : insertion de 2 documents, lecture des derniers.
5. `tail -f /dev/null` pour maintenir le conteneur actif.

## Flux de Données
- **Entrée** : tables/collections `iris` de PostgreSQL et MongoDB.
- **Sortie** : nouveaux enregistrements écrits dans les deux BDD + logs stdout.

## Lancement
```bash
docker compose up -d miniconda
docker compose logs -f miniconda
# accès interactif :
docker exec -it miniconda_app bash
```

## Dépendances / Port
Dépend de `ollama`, `postgres`, `mongodb` (`condition: service_healthy`). Aucun port
exposé. Code source monté à chaud via `./python/src:/app/src`.
