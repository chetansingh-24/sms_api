import os
import psycopg2
from flask import Flask, jsonify, request
from flask_cors import CORS
from os import getenv
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

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

def get_sms_info(volunteer_ph_no):
    connection = get_db_connection()
    if not connection:
        return None, "Failed to connect to the database"

    try:
        cursor = connection.cursor()
        sender_id_for_volunteer = """
        SELECT admin_id
        FROM admin_volunteer_map
        WHERE volunteer_phone_number = %s
        """
        cursor.execute(sender_id_for_volunteer, (volunteer_ph_no,))
        admin_id = cursor.fetchone()

        if not admin_id:
            return None, "Admin ID not found for the given volunteer phone number"

        sms_query = """
        SELECT sms_text, draft_time
        FROM sms_draft
        WHERE admin_id = %s
        """
        cursor.execute(sms_query, (admin_id,))
        sms_drafts = cursor.fetchall()

        sms_list = []
        for sms in sms_drafts:
            sms_list.append({
                "message": sms[0],
                "draft_time": sms[1].strftime("%d-%m-%Y %H:%M:%S")
            })

        cursor.close()
        connection.close()

        return {
            "sender_id": sender_id,
            "sms_drafts": sms_list
        }, None

    except Exception as e:
        print(f"Error fetching SMS info: {e}")
        return None, "Error fetching SMS info"

@app.route('/get_sms', methods=['GET'])
def volunteer_sms_info():
    volunteer_ph_no = request.args.get('phone_number')
    if not volunteer_ph_no:
        return jsonify({"error": "Volunteer phone number is required"}), 400
    sms_info, error = get_sms_info(volunteer_ph_no)
    if error:
        return jsonify({"error": error}), 404
    return jsonify(sms_info)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
