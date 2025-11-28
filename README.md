# Serveur API Yemba ASR

Serveur API containerisé pour la transcription audio Yemba utilisant le modèle Hugging Face.

## 🚀 Installation Rapide

### Option 1: Avec Docker Compose (Recommandé)

```bash
# 1. Aller dans le dossier du serveur
cd yemba_asr_server

# 2. Construire et démarrer le conteneur
docker-compose up -d

# 3. Vérifier que ça fonctionne
curl http://localhost:5000/health
```

### Option 2: Avec Docker seul

```bash
# 1. Construire l'image
docker build -t yemba-asr-server .

# 2. Lancer le conteneur
docker run -d \
  --name yemba-asr-server \
  -p 5000:5000 \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  yemba-asr-server

# 3. Vérifier
curl http://localhost:5000/health
```

## 📋 Prérequis

- Docker et Docker Compose installés
- Au moins 4GB de RAM disponible
- ~500MB d'espace disque (pour le modèle)

## 🔧 Configuration

### Changer le port

Modifiez `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Port externe:port interne
```

Ou avec Docker:
```bash
docker run -p 8080:5000 ...
```

### Variables d'environnement

- `PORT`: Port interne (défaut: 5000)
- `HOST`: Adresse d'écoute (défaut: 0.0.0.0)

## 📡 API Endpoints

### GET /health
Vérifier que le serveur fonctionne.

**Réponse:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### POST /transcribe
Transcrire un fichier audio.

**Requête:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Field: `audio` (fichier audio)

**Exemple avec curl:**
```bash
curl -X POST http://localhost:5000/transcribe \
  -F "audio=@votre_fichier.wav"
```

**Réponse succès:**
```json
{
  "success": true,
  "transcription": "texte transcrit en yemba",
  "error": null
}
```

**Réponse erreur:**
```json
{
  "success": false,
  "transcription": null,
  "error": "message d'erreur"
}
```

## 🛠️ Maintenance

### Voir les logs
```bash
docker-compose logs -f
```

### Redémarrer
```bash
docker-compose restart
```

### Arrêter
```bash
docker-compose down
```

### Mettre à jour
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🌐 Accès depuis le réseau

Pour accéder depuis d'autres machines (comme votre Raspberry Pi):

1. Trouvez l'IP de votre serveur:
   ```bash
   # Linux/Mac
   hostname -I
   
   # Windows
   ipconfig
   ```

2. Utilisez cette IP dans votre application:
   ```
   http://192.168.1.100:5000/transcribe
   ```

3. Assurez-vous que le firewall autorise le port 5000.

## ⚠️ Notes

- Le premier démarrage peut prendre 5-10 minutes (téléchargement du modèle ~300MB)
- Le modèle est mis en cache dans `~/.cache/huggingface` pour éviter de re-télécharger
- Le serveur utilise CPU uniquement (pas de GPU nécessaire)

