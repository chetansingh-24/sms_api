import os
import psycopg2
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from os import getenv
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})

@app.after_request
def apply_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

def get_db_connection():
    try:
        connection = psycopg2.connect(
            dbname=getenv('PGDATABASE'),
            user=getenv('PGUSER'),
            password=getenv('PGPASSWORD'),
            host=getenv('PGHOST'),
            port=getenv('PGPORT', 5432)
        )
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/create_sms_draft', methods=['POST'])
@cross_origin()
def create_sms_draft():
    data = request.json
    required_fields = ['user_id', 'template_id', 'sender_id', 'text', 'sms_type']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing one or more required fields"}), 400

    user_id = data['user_id']
    template_id = data['template_id']
    sender_id = data['sender_id']
    text = data['text']
    sms_type = data['sms_type']

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Failed to connect to the database"}), 500

    try:
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO sms_draft (user_id, template_id, sender_id, text, sms_type, timestamp)
        VALUES (%s, %s, %s, %s,%s, NOW())
        RETURNING id;
        """
        cursor.execute(insert_query, (user_id, template_id, sender_id, text, sms_type))
        connection.commit()

        new_sms_id = cursor.fetchone()[0]

        cursor.close()
        connection.close()

        return jsonify({"message": "SMS draft created successfully", "sms_id": new_sms_id}), 201

    except Exception as e:
        print(f"Error inserting SMS draft: {e}")
        return jsonify({"error": "Error inserting SMS draft"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
