FROM python:3.11-slim

# Installer les dépendances système pour audio
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Créer le répertoire de travail
WORKDIR /app

# Copier les requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Installer PyTorch CPU (plus léger, compatible partout)
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Copier le code de l'application
COPY app.py .

# Exposer le port
EXPOSE 5000

# Variables d'environnement
ENV PORT=5000
ENV HOST=0.0.0.0

# Commande pour démarrer le serveur
CMD ["python", "app.py"]

