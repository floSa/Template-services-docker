FROM python:3.12-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de configuration
COPY requirements.txt /app/
COPY entrypoint.sh /app/
COPY src/ /app/src/

# Installation des packages Python
RUN pip install --no-cache-dir -r requirements.txt

# Rendre le script d'entrée exécutable
RUN chmod +x /app/entrypoint.sh

# Exposition du port Streamlit
EXPOSE 8501

CMD ["bash", "/app/entrypoint.sh"]
