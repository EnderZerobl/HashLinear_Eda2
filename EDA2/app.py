from flask import Flask, request, jsonify, render_template
from linear_hash import LinearHash
import json

app = Flask(__name__)

hash_table = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/init', methods=['POST'])
def init_hash():
    global hash_table
    data = request.json
    p = int(data.get('page_capacity', 10))
    alpha = float(data.get('max_load_factor', 0.75))
    
    hash_table = LinearHash(page_capacity=p, max_load_factor=alpha)
    return hash_table.export_json(), 200, {'Content-Type': 'application/json'}

@app.route('/api/insert', methods=['POST'])
def insert_key():
    global hash_table
    if not hash_table:
        return jsonify({"error": "Tabela não inicializada"}), 400
    
    data = request.json
    key = int(data.get('key'))
    result = hash_table.insert(key)
    
    state = json.loads(hash_table.export_json())
    return jsonify({"operation": result, "state": state})

@app.route('/api/lookup', methods=['POST'])
def lookup_key():
    global hash_table
    if not hash_table:
        return jsonify({"error": "Tabela não inicializada"}), 400
    
    data = request.json
    key = int(data.get('key'))
    result = hash_table.lookup(key)
    
    state = json.loads(hash_table.export_json())
    return jsonify({"operation": result, "state": state})

if __name__ == '__main__':
    app.run(debug=True, port=5000)