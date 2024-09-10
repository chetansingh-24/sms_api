from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os

import psycopg2
from os import getenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})
def get_db_connection():
    connection = psycopg2.connect(
        dbname=getenv('PGDATABASE'),
        user=getenv('PGUSER'),
        password=getenv('PGPASSWORD'),
        host=getenv('PGHOST'),
        port=getenv('PGPORT', 5432)
    )
    return connection


@app.route('/login', methods=['POST'])
def login():
    data = request.json
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

    cursor.close()
    connection.close()

    if user:
        columns = [desc[0] for desc in cursor.description]
        user_data = dict(zip(columns, user))
        return jsonify(user_data), 200
    else:
        return jsonify({'error': 'Invalid phone number or password'}), 401


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
