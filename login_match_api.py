from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2 import OperationalError, InterfaceError
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

def get_db_connection():
    try:
        connection = psycopg2.connect(
            dbname=os.getenv('PGDATABASE'),
            user=os.getenv('PGUSER'),
            password=os.getenv('PGPASSWORD'),
            host=os.getenv('PGHOST'),
            port=os.getenv('PGPORT', 5432)
        )
        return connection
    except OperationalError as e:
        print(f"Database connection error: {e}")
        raise

@app.route('/login', methods=['POST'])
def login():
    global cursor, connection
    try:
        data = request.json
        if not data or not all(k in data for k in ('phone_number', 'password')):
            return jsonify({'error': 'Invalid payload. Both phone_number and password are required.'}), 400

        phone_number = data.get('phone_number')
        password = data.get('password')

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            SELECT * FROM users
            WHERE phone_number = %s AND password = %s
        """

        cursor.execute(query, (phone_number, password))
        user = cursor.fetchone()

        if user:
            columns = [desc[0] for desc in cursor.description]
            user_data = dict(zip(columns, user))
            return jsonify(user_data), 200
        else:
            return jsonify({'error': 'Invalid phone number or password'}), 401

    except InterfaceError as e:
        print(f"Database query error: {e}")
        return jsonify({'error': 'Database error. Please try again later.'}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred. Please try again later.'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
