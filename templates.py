from flask import Flask, jsonify
import psycopg2
import os
from collections import defaultdict

app = Flask(__name__)


# Database connection (replace with your actual config)
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    return conn


@app.route('/api/sms_headers', methods=['GET'])
def get_sms_headers():
    conn = get_db_connection()
    cur = conn.cursor()

    # Query to get unique sms_header and corresponding sms_template_id
    query = """
    SELECT sms_header, sms_template_id 
    FROM broadcast_templates 
    WHERE msg_type = 'SMS';
    """

    cur.execute(query)
    rows = cur.fetchall()

    # Close the database connection
    cur.close()
    conn.close()

    # Use a defaultdict to group sms_template_id by sms_header
    header_map = defaultdict(list)

    for row in rows:
        sms_header = row[0]
        sms_template_id = row[1]
        header_map[sms_header].append(sms_template_id)

    # Convert the defaultdict to a regular dictionary
    headers = [{"sms_header": key, "sms_template_ids": value} for key, value in header_map.items()]

    return jsonify(headers)


@app.route('/api/whatsapp_campaigns', methods=['GET'])
def get_whatsapp_campaigns():
    conn = get_db_connection()
    cur = conn.cursor()

    # Query to get wp_campaign_name and lang_code
    query = """
    SELECT wp_campaign_name, lang_code
    FROM broadcast_templates
    WHERE msg_type = 'WhatsApp';;
    """

    cur.execute(query)
    rows = cur.fetchall()

    # Close the database connection
    cur.close()
    conn.close()

    # Use a set to store unique wp_campaign_name and lang_code pairs
    campaign_set = set()

    for row in rows:
        wp_campaign_name = row[0]
        lang_code = row[1]
        campaign_set.add((wp_campaign_name, lang_code))

    # Convert the set to a list of dictionaries
    campaigns = [{"wp_campaign_name": name, "lang_code": code} for name, code in campaign_set]

    return jsonify(campaigns)


if __name__ == '__main__':
    app.run(debug=True)
