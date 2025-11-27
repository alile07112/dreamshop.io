"""
DreamShop API Media Handler
Convertit les file_id Telegram en URLs publiques pour affichage dans la mini-app.

Installation:
1. Ajouter ce code à votre api.py (dans la section des imports et routes)
2. Redémarrer l'API Flask
3. Les images/vidéos s'afficheront automatiquement via /api/media/<file_id>

Exemple d'utilisation dans index.html :
    const mediaUrl = `/api/media/${product.file_id}`;
"""

import requests
from flask import Flask, jsonify, abort

# === À AJOUTER DANS api.py ===

# Token de votre bot Telegram
TELEGRAM_BOT_TOKEN = '8075003654:AAFknb4-W0lPEPSKtGyq6dy4oCeNxs3xT7E'

@app.route('/api/media/<file_id>', methods=['GET'])
def get_media(file_id):
    """
    Convertit un file_id Telegram en URL publique.
    Retourne une URL qui pointe directement vers le fichier sur les serveurs Telegram.
    """
    try:
        # Appeler l'API Telegram pour obtenir l'URL du fichier
        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}'
        response = requests.get(url, timeout=5)
        
        if response.status_code != 200:
            abort(404)
        
        data = response.json()
        if not data.get('ok'):
            abort(404)
        
        # Construire l'URL publique du fichier
        file_path = data['result']['file_path']
        media_url = f'https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}'
        
        # Retourner un JSON avec l'URL (la mini-app utilisera cette URL en tant que src)
        return jsonify({
            'file_id': file_id,
            'media_url': media_url,
            'type': 'photo'  # ou 'video' selon le contexte
        }), 200
    
    except Exception as e:
        print(f'❌ Erreur media handler: {e}')
        abort(500)

# === FIN DU CODE À AJOUTER ===
