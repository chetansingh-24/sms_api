from flask import Flask, request, jsonify
import psycopg2
import os
from os import getenv
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
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

@app.route('/get_sms_draft', methods=['GET'])
def get_sms_draft():
    user_id = request.args.get('user_id')  # Get user_id from query params

    # Validate that user_id is provided and is an integer
    if not user_id or not user_id.isdigit():
        return jsonify({'error': 'Invalid user_id'}), 400

    user_id = int(user_id)  # Convert to integer

    connection = get_db_connection()
    cursor = connection.cursor()

    # Query for user_id=1
    cursor.execute("SELECT * FROM sms_draft WHERE user_id = 1")
    user1_data = cursor.fetchall()

    if not user1_data:
        return jsonify({'error': 'No drafts found for user_id 1'}), 404

    columns = [desc[0] for desc in cursor.description]
    user1_response = [dict(zip(columns, row)) for row in user1_data]

    combined_response = user1_response  # Start with user1_response

    if user_id != 1:
        cursor.execute("SELECT * FROM sms_draft WHERE user_id = %s", (user_id,))
        user_admin_data = cursor.fetchall()

        if user_admin_data:
            user_admin_response = [dict(zip(columns, row)) for row in user_admin_data]

            # Combine both responses into a single list
            combined_response = user1_response + user_admin_response

    cursor.close()
    connection.close()

    return jsonify(combined_response), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

