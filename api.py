from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime
import requests
from flask import Flask, jsonify, abort, Response

app = Flask(__name__)
# ⚠️ Permet à Netlify d'accéder à l'API depuis n'importe où
CORS(app, resources={r"/*": {"origins": "*"}})

STOCK_FILE = "stock.json"

def load_stock():
    """Charge le stock depuis stock.json"""
    try:
        if os.path.exists(STOCK_FILE):
            with open(STOCK_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Convertir ancien format si nécessaire
                if isinstance(data, list):
                    return {"hash": data, "weed": []}
                elif isinstance(data, dict):
                    # S'assurer que les catégories existent
                    if "hash" not in data:
                        data["hash"] = []
                    if "weed" not in data:
                        data["weed"] = []
                    return data
                return {"hash": [], "weed": []}
        else:
            # Créer le fichier s'il n'existe pas
            initial_data = {"hash": [], "weed": []}
            save_stock(initial_data)
            return initial_data
    except Exception as e:
        print(f"❌ Erreur chargement stock: {e}")
        return {"hash": [], "weed": []}

def save_stock(data):
    """Sauvegarde le stock dans stock.json"""
    try:
        with open(STOCK_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"✅ Stock sauvegardé: {datetime.now().strftime('%H:%M:%S')}")
        return True
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")
        return False

# ===== ROUTES API =====

@app.route('/')
def home():
    """Page d'accueil de l'API"""
    return jsonify({
        "name": "🛒 DreamShop API",
        "version": "1.0",
        "status": "running",
        "endpoints": {
            "/api/stock": "GET - Récupérer tout le stock",
            "/api/stock/<category>": "GET - Récupérer une catégorie",
            "/api/health": "GET - Vérifier l'état du serveur"
        }
    })

TELEGRAM_BOT_TOKEN = '8075003654:AAFknb4-W0lPEPSKtGyq6dy4oCeNxs3xT7E'
ADMIN_ID = 8470082934


def send_telegram_message(chat_id, text, reply_markup=None):
    """Envoie un message via l'API Telegram Bot."""
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    if reply_markup is not None:
        payload['reply_markup'] = json.dumps(reply_markup, ensure_ascii=False)
    try:
        r = requests.post(url, data=payload, timeout=6)
        return r.ok, r.json() if r.content else {}
    except Exception as e:
        print(f'❌ Erreur send_telegram_message: {e}')
        return False, {'error': str(e)}

@app.route('/api/video/<file_id>', methods=['GET'])
def get_video(file_id):
    """Retourne l'URL Telegram publique pour la vidéo"""
    try:
        print(f"🎬 Récupération URL vidéo: {file_id[:30]}...")
        
        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}'
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if not data.get('ok'):
            return jsonify({'error': 'File not found'}), 404
        
        file_path = data['result']['file_path']
        media_url = f'https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}'
        
        print(f"✅ Media URL: {media_url[:80]}...")
        
        return jsonify({'media_url': media_url}), 200
    
    except Exception as e:
        print(f'❌ Erreur: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock', methods=['GET'])
def get_all_stock():
    """Récupère tout le stock"""
    try:
        stock = load_stock()
        print(f"📦 Stock demandé - Hash: {len(stock.get('hash', []))} | Weed: {len(stock.get('weed', []))}")
        return jsonify(stock), 200
    except Exception as e:
        print(f"❌ Erreur API /stock: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/stock/<category>', methods=['GET'])
def get_category_stock(category):
    """Récupère une catégorie spécifique"""
    try:
        stock = load_stock()
        if category not in stock:
            return jsonify({"error": f"Catégorie '{category}' non trouvée"}), 404
        
        print(f"📦 Catégorie '{category}' demandée - {len(stock[category])} produits")
        return jsonify({category: stock[category]}), 200
    except Exception as e:
        print(f"❌ Erreur API /stock/{category}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Vérifier que l'API fonctionne"""
    stock = load_stock()
    return jsonify({
        "status": "✅ OK",
        "message": "DreamShop API is running",
        "timestamp": datetime.now().isoformat(),
        "stock_file_exists": os.path.exists(STOCK_FILE),
        "total_products": {
            "hash": len(stock.get("hash", [])),
            "weed": len(stock.get("weed", []))
        }
    }), 200

@app.route('/api/reload', methods=['POST'])
def reload_stock():
    """Recharger le stock (pour forcer un refresh)"""
    try:
        stock = load_stock()
        return jsonify({
            "success": True,
            "message": "Stock rechargé",
            "data": stock
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/order', methods=['POST'])
def receive_order():
    """Recevoir une commande depuis le frontend et la forwarder au bot/admin, puis notifier le client."""
    try:
        data = request.get_json(force=True)
        # Attendu: product, category, weight, price, address, phone, user:{id,username}
        product = data.get('product')
        category = data.get('category')
        weight = data.get('weight')
        price = data.get('price')
        address = data.get('address')
        phone = data.get('phone')
        user = data.get('user') or {}
        user_id = int(user.get('id') or 0)
        username = user.get('username') or 'unknown'

        if not product or not address or not phone:
            return jsonify({'success': False, 'error': 'Champs manquants'}), 400

        caption = (
            f"📦 *Nouvelle commande reçue !*\n\n"
            f"🛍️ Produit : {product}\n"
            f"👤 Client : @{username} (id:{user_id})\n"
            f"🏠 Adresse : {address}\n"
            f"📞 Contact : {phone}\n"
            f"⚖️ Poids : {weight}g\n"
            f"💰 Prix : {price}€"
        )

        # Inline keyboard: validate/refuse with callback_data understood by the admin bot
        reply_markup = {
            'inline_keyboard': [
                [
                    {'text': '✅ Valider', 'callback_data': f'validate_{user_id}'},
                    {'text': '❌ Refuser', 'callback_data': f'refuse_{user_id}'}
                ]
            ]
        }

        ok_admin, resp_admin = send_telegram_message(ADMIN_ID, caption, reply_markup=reply_markup)

        # Notify client (acknowledgement)
        if user_id and user_id != 0:
            user_text = f"✅ Ta commande pour *{product}* a bien été envoyée à l'admin pour validation."
            ok_user, resp_user = send_telegram_message(user_id, user_text)
        else:
            ok_user, resp_user = False, {'error': 'no user id'}

        return jsonify({'success': True, 'admin_ok': ok_admin, 'admin_resp': resp_admin, 'user_ok': ok_user, 'user_resp': resp_user}), 200

    except Exception as e:
        print(f'❌ Erreur /api/order: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 API DREAMSHOP DÉMARRÉE")
    print("=" * 60)
    print(f"📡 Port: 5000")
    print(f"🌍 Accessible depuis: http://45.158.77.19:5000")
    print(f"📂 Fichier stock: {os.path.abspath(STOCK_FILE)}")
    print(f"✅ CORS activé pour toutes les origines")
    print("=" * 60)
    
    # Vérifier que le fichier stock existe
    if not os.path.exists(STOCK_FILE):
        print("⚠️  stock.json n'existe pas, création...")
        save_stock({"hash": [], "weed": []})
    
    # Lancer le serveur sur toutes les interfaces
    app.run(
        host='45.158.77.19',  # Écoute sur toutes les interfaces
        port=5000,
        debug=False,     # Désactiver le debug en production
        threaded=True    # Support multi-thread
    )
