import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- Importaciones de Firebase ---
import firebase_admin
from firebase_admin import credentials, firestore

# --- Configuracion de Firebase ---
try:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
except FileNotFoundError:
    print("ERROR: No se encontró el archivo 'serviceAccountKey.json'.")
    exit() 
except ValueError:
    pass 

# --- Referencias a las Colecciones de Firestore ---
db = firestore.client()
sales_collection = db.collection('sales') 
products_collection = db.collection('products') 

# --- Configuracion de Flask ---
app = Flask(__name__)
CORS(app) 

# --- API Endpoints ---

@app.route('/')
def home():
    """Ruta de prueba para verificar que el servidor está vivo."""
    return jsonify({"message": "Bienvenido a la API del Bazar Universal (100% Firestore!)"})

# 1. Endpoint: /api/items?q=:query 
@app.route('/api/items', methods=['GET'])
def get_items():
    """Busca productos en la coleccion 'products' de Firestore."""
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify([])

    results = []
    try:
        docs = products_collection.stream()   
        for doc in docs:
            product = doc.to_dict()
            if query in product.get('title', '').lower() or \
               query in product.get('description', '').lower():
                results.append(product)
                
        return jsonify(results)
    except Exception as e:
        print(f"Error al buscar productos: {e}")
        return jsonify({"error": str(e)}), 500


# 2. Endpoint: /api/items/:id 
@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item_by_id(item_id):
    """Obtiene un producto especifico por su ID desde Firestore."""
    try:
        doc_ref = products_collection.document(str(item_id))
        doc = doc_ref.get()
        
        if doc.exists:
            return jsonify(doc.to_dict())
        else:
            return jsonify({"error": "Producto no encontrado"}), 404
            
    except Exception as e:
        print(f"Error al obtener producto: {e}")
        return jsonify({"error": str(e)}), 500

# 3. Endpoint: /api/addSale (Escribe en 'sales')
@app.route('/api/addSale', methods=['POST'])
def add_sale():
    """Registra una nueva venta en la colección 'sales' de Firestore."""
    data_to_save = request.json
    if not data_to_save:
        return jsonify(False)
    try:
        sales_collection.add(data_to_save)
        return jsonify(True)
    except Exception as e:
        print(f"Error al guardar en Firestore: {e}")
        return jsonify(False)

@app.route('/api/sales', methods=['GET'])
def get_sales():
    """Obtiene todas las ventas registradas desde la coleccion 'sales'."""
    try:
        sales_list = []
        docs = sales_collection.stream()
        for doc in docs:
            sale = doc.to_dict()
            sale['firebase_id'] = doc.id 
            sales_list.append(sale)
        return jsonify(sales_list)
    except Exception as e:
        print(f"Error al leer de Firestore: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
