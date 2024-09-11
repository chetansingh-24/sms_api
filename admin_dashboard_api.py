import os
import psycopg2
from flask import Flask, jsonify, request
from flask_cors import CORS
from os import getenv
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

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


def get_sms_info_admin(admin_ph_no):
    connection = get_db_connection()
    cursor = connection.cursor()
    admin_id_from_admin_phone_query = """
    SELECT id 
    FROM users
    WHERE phone_number = %s
    """
    cursor.execute(admin_id_from_admin_phone_query, (admin_ph_no,))
    admin_id_result = cursor.fetchone()
    if admin_id_result is None:
        cursor.close()
        connection.close()
        return None, "Admin phone number not found"

    admin_id = admin_id_result[0]
    volunteer_count_query = """
    SELECT COUNT(*) 
    FROM admin_volunteer_map
    WHERE admin_id = %s
    """
    cursor.execute(volunteer_count_query, (admin_id,))
    total_volunteers = cursor.fetchone()[0]
    sender_query = """
    SELECT sender_id
    FROM admin_volunteer_map
    WHERE admin_id = %s
    """
    cursor.execute(sender_query, (admin_id,))
    volunteers = cursor.fetchall()
    sent = 0
    delivered = 0

    for v in volunteers:
        count_query = """
        SELECT 
            COUNT(*) AS total_messages,
            COUNT(CASE WHEN status = 'Delivered' THEN 1 END) AS delivered_messages
        FROM sms_delivery
        WHERE sender_id = %s
        """
        cursor.execute(count_query, (v,))
        result = cursor.fetchone()
        total_messages, delivered_messages = result
        sent += total_messages
        delivered += delivered_messages

    cursor.close()
    connection.close()

    return {
        "active_volunteers": total_volunteers,
        "messages_sent": sent,
        "messages_delivered": delivered
    }, None




def get_sms_info_volunteer(volunteer_ph_no):
    connection = get_db_connection()
    cursor = connection.cursor()
    sender_id_for_volunteer = """
    SELECT sender_id 
    FROM admin_volunteer_map
    WHERE volunteer_phone_number = %s
    """
    cursor.execute(sender_id_for_volunteer, (volunteer_ph_no,))
    sender_id = cursor.fetchone()
    volunteers = cursor.fetchall()
    sent = 0
    delivered = 0

    count_query = """
    SELECT 
        COUNT(*) AS total_messages,
        COUNT(CASE WHEN status = 'Delivered' THEN 1 END) AS delivered_messages
    FROM sms_delivery
    WHERE sender_id = %s
    """
    cursor.execute(count_query, (sender_id,))
    result = cursor.fetchone()
    total_messages, delivered_messages = result
    sent += total_messages
    delivered += delivered_messages

    cursor.close()
    connection.close()

    return {
        "messages_sent": sent,
        "messages_delivered": delivered
    }, None

@app.route('/admin/sms_info', methods=['GET'])
def admin_sms_info():
    admin_ph_no = request.args.get('phone_number')
    if not admin_ph_no:
        return jsonify({"error": "Admin phone number is required"}), 400
    sms_info, error = get_sms_info_admin(admin_ph_no)
    if error:
        return jsonify({"error": error}), 404
    return jsonify(sms_info)


@app.route('/volunteer/sms_info', methods=['GET'])
def volunteer_sms_info():
    volunteer_ph_no = request.args.get('phone_number')
    if not volunteer_ph_no:
        return jsonify({"error": "Admin phone number is required"}), 400
    sms_info, error = get_sms_info_volunteer(volunteer_ph_no)
    if error:
        return jsonify({"error": error}), 404
    return jsonify(sms_info)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


