"""
Serveur API pour la transcription Yemba (ASR)
Utilise le modèle Hugging Face RobinsonNgeukeu237/working
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.serving import WSGIRequestHandler
import os
import tempfile
import traceback
import torch
from transformers import AutoProcessor, AutoModelForCTC
from pydub import AudioSegment
import librosa

app = Flask(__name__)
CORS(app)  # Permettre les requêtes depuis n'importe quelle origine

# Variables globales pour le modèle (chargé une seule fois)
processor = None
model = None
device = None

def load_model():
    """Charger le modèle Yemba ASR une seule fois au démarrage"""
    global processor, model, device
    
    if model is not None:
        print("[INFO] Model already loaded")
        return
    
    try:
        print("[INFO] Initializing PyTorch device...")
        device = torch.device("cpu")  # Utiliser CPU (compatible partout)
        print(f"[INFO] Using device: {device}")
        
        model_name = "RobinsonNgeukeu237/working"
        print(f"[INFO] Loading Yemba ASR model: {model_name}")
        print("[INFO] This may take a few minutes on first run (downloading ~300MB)...")
        
        processor = AutoProcessor.from_pretrained(model_name)
        model = AutoModelForCTC.from_pretrained(
            model_name,
            ignore_mismatched_sizes=True
        )
        model.to(device)
        model.eval()  # Mode évaluation
        
        print("[INFO] Model loaded successfully!")
        
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        traceback.print_exc()
        raise

@app.route('/health', methods=['GET'])
@app.route('/yemba-asr/health', methods=['GET'])
def health_check():
    """Vérifier que le serveur fonctionne"""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None
    }), 200

@app.route('/transcribe', methods=['POST'])
@app.route('/yemba-asr/transcribe', methods=['POST'])
def transcribe():
    """
    Transcrire un fichier audio en texte Yemba
    
    Requête:
        - Fichier audio dans 'audio' (multipart/form-data)
        - Formats supportés: WAV, MP3, FLAC, etc.
    
    Réponse:
        {
            "success": true,
            "transcription": "texte transcrit",
            "error": null
        }
    """
    global processor, model, device
    
    try:
        # Vérifier que le modèle est chargé
        if model is None:
            load_model()
        
        # Vérifier qu'un fichier audio a été envoyé
        if 'audio' not in request.files:
            return jsonify({
                "success": False,
                "transcription": None,
                "error": "No audio file provided. Use 'audio' field in multipart/form-data"
            }), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({
                "success": False,
                "transcription": None,
                "error": "No audio file selected"
            }), 400
        
        # Sauvegarder le fichier temporairement
        file_ext = os.path.splitext(audio_file.filename)[-1].lower()
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
        audio_file.save(temp_audio.name)
        temp_audio.close()
        
        try:
            # Charger et préparer l'audio
            if file_ext == ".mp3":
                # Convertir MP3 en WAV
                audio_segment = AudioSegment.from_file(temp_audio.name, format="mp3")
                temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                audio_segment.export(temp_wav.name, format="wav")
                temp_wav.close()
                audio, sr = librosa.load(temp_wav.name, sr=16000)
                os.unlink(temp_wav.name)  # Nettoyer
            else:
                # Charger WAV directement
                audio, sr = librosa.load(temp_audio.name, sr=16000)
            
            # Traiter l'audio avec le processeur
            inputs = processor(audio, sampling_rate=sr, return_tensors="pt")
            input_values = inputs.input_values.to(device)
            
            # Inférence (pas de gradient nécessaire)
            with torch.no_grad():
                logits = model(input_values).logits
            
            # Décoder les prédictions
            pred_ids = torch.argmax(logits, dim=-1)
            transcription = processor.batch_decode(pred_ids)[0]
            
            # Nettoyer la transcription
            transcription = transcription.replace("[PAD]", " ").strip()
            
            return jsonify({
                "success": True,
                "transcription": transcription,
                "error": None
            }), 200
            
        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_audio.name):
                os.unlink(temp_audio.name)
    
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Transcription failed: {error_msg}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "transcription": None,
            "error": error_msg
        }), 500

if __name__ == '__main__':
    # Charger le modèle au démarrage
    print("[INFO] Starting Yemba ASR Server...")
    load_model()
    
    # Démarrer le serveur
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    print(f"[INFO] Server starting on {host}:{port}")
    app.run(host=host, port=port, debug=False)

