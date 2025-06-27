# python/Dockerfile
FROM continuumio/miniconda3:latest
WORKDIR /app

# 1) Installer client PostgreSQL
RUN apt-get update \
    && apt-get install -y postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 2) Copier et créer l'environnement conda
COPY environment.yml /app/
RUN echo "=== Création de l'environnement conda via environment.yml ===" \
    && conda env create -f /app/environment.yml \
    && conda clean -afy

# 3) Copier script d'entrée et code source
COPY entrypoint.sh /app/
COPY src/ /app/src/
RUN chmod +x /app/entrypoint.sh

# 4) Point d'entrée
ENTRYPOINT ["/app/entrypoint.sh"]
