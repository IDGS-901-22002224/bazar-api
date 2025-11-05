import json
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
    print("Firebase ya está inicializado (probablemente por app.py).")
    pass 

db = firestore.client()

# --- Cargar el JSON local ---
try:
    with open('products.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        products_list = data.get('products', [])
except FileNotFoundError:
    print("ERROR: No se encontró el archivo 'products.json'.")
    exit()
except json.JSONDecodeError:
    print("ERROR: El archivo 'products.json' no tiene un formato JSON válido.")
    exit()

# --- Subir a Firestore ---
products_collection = db.collection('products')
print(f"Subiendo {len(products_list)} productos a Firestore...")

count = 0
for product in products_list:
    try:
        # Usamos el 'id' del producto (convertido a string) como el ID del documento
        doc_id = str(product['id'])
        products_collection.document(doc_id).set(product)
        count += 1
    except Exception as e:
        print(f"Error subiendo producto {product.get('id')}: {e}")

print(f"¡Éxito! Se subieron {count} productos a la colección 'products'.")