from flask import Flask, request, jsonify, render_template, abort, Blueprint
from flask_cors import CORS
import sqlite3
import os
import logging
from init_db import init_db  # Import init_db from init_db.py

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Restrict CORS to specific routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
DB_PATH = os.getenv('DB_PATH', os.path.join(os.path.dirname(__file__), 'maize_milling.db'))
DEBUG_MODE = os.getenv('DEBUG_MODE', 'True').lower() == 'true'

# Initialize the database
init_db()

# Helper function to execute queries
def execute_query(query, params=()):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return {"success": True}
    except sqlite3.Error as e:
        logger.error(f"Query execution error: {e}")
        return {"error": "Database error", "details": str(e)}
    finally:
        conn.close()

# Helper function to fetch data from the database
def fetch_data(query, params=()):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        logger.error(f"Data fetching error: {e}")
        return {"error": "Database error", "details": str(e)}
    finally:
        conn.close()

# ============================
# CUSTOMER MANAGEMENT ROUTES
# ============================
customer_bp = Blueprint('customers', __name__)

@customer_bp.route('/customers', methods=['GET'])
def get_customers():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    if page < 1 or per_page < 1:
        return jsonify({"error": "Page and per_page must be positive integers"}), 400
    offset = (page - 1) * per_page
    query = "SELECT * FROM Customers WHERE is_deleted = FALSE LIMIT ? OFFSET ?"
    customers = fetch_data(query, (per_page, offset))
    if isinstance(customers, dict) and "error" in customers:
        return jsonify(customers), 500
    return jsonify(customers)

@customer_bp.route('/customers', methods=['POST'])
def add_customer():
    data = request.json
    required_fields = ['name', 'phone', 'email', 'address']
    if not all(field in data for field in required_fields):
        abort(400, description="Missing required fields")
    query = '''
        INSERT INTO Customers (name, phone, email, address, is_deleted)
        VALUES (?, ?, ?, ?, FALSE)
    '''
    result = execute_query(query, (data['name'], data['phone'], data['email'], data['address']))
    if "error" in result:
        return jsonify(result), 500
    return jsonify({"message": "Customer added successfully!"}), 201

@customer_bp.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    data = request.json
    query = "SELECT * FROM Customers WHERE customer_id = ? AND is_deleted = FALSE"
    customer = fetch_data(query, (customer_id,))
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    query = '''
        UPDATE Customers
        SET name = ?, phone = ?, email = ?, address = ?
        WHERE customer_id = ? AND is_deleted = FALSE
    '''
    result = execute_query(query, (data['name'], data['phone'], data['email'], data['address'], customer_id))
    if "error" in result:
        return jsonify(result), 500
    return jsonify({"message": "Customer updated successfully!"})

@customer_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    query = "SELECT * FROM Customers WHERE customer_id = ? AND is_deleted = FALSE"
    customer = fetch_data(query, (customer_id,))
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    query = "UPDATE Customers SET is_deleted = TRUE WHERE customer_id = ?"
    result = execute_query(query, (customer_id,))
    if "error" in result:
        return jsonify(result), 500
    return jsonify({"message": "Customer marked as deleted!"})

# Register Blueprints
app.register_blueprint(customer_bp, url_prefix='/api')

# ============================
# FRONT-END ROUTE
# ============================
@app.route('/')
def index():
    return render_template('index.html')  # Ensure 'index.html' is in a 'templates' folder

# ============================
# MAIN ENTRY POINT
# ============================
if __name__ == '__main__':
    app.run(debug=DEBUG_MODE)  # Set debug=False in production