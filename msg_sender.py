import requests
from flask import Flask, request, jsonify
import os
from elasticsearch import Elasticsearch
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime  # Import datetime module

load_dotenv()
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

es = Elasticsearch(
    cloud_id=os.getenv("ELASTIC_CLOUD_ID"),
    api_key=os.getenv("ELASTIC_API_KEY")
)

def send_sms(phone_number, message_id, sender_id, name):
    url = "https://www.fast2sms.com/dev/bulkV2"

    querystring = {
        "authorization": "hJsT2Y7kmsrCJDOzdm5UeobfKLlY2EiQ0gbDrvOBFg4lUVrlBTvcRxpED3Zf",
        "sender_id": sender_id,
        "message": message_id,
        "route": "dlt",
        "variables_values": name,
        "numbers": phone_number
    }
    headers = {
        'cache-control': "no-cache"
    }
    response = requests.get(url, headers=headers, params=querystring)
    return response

@app.route('/send_bulk_sms', methods=['POST'])
def send_bulk_sms():
    data = request.get_json()
    message = data.get('message')
    sender_id = data.get('sender_id')

    if not message or not sender_id:
        return jsonify({"error": "Missing message or sender_id"}), 400

    index_name = 'phone_name_map_messaging_piece'
    query = {
        "query": {
            "match_all": {}
        }
    }

    try:
        response = es.search(index=index_name, body=query)
        hits = response['hits']['hits']

        total_messages_sent = 0

        for hit in hits:
            source = hit['_source']
            phone_number = source.get('phone_number')
            name = source.get('name')

            if phone_number:
                sms_response = send_sms(phone_number, message, sender_id, name)
                print(f"Message sent to {phone_number}: {sms_response.text}")
                total_messages_sent += 1  # Increment the counter

        # Get the current datetime
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return jsonify({
            "status": "success",
            "message": "Messages sent successfully",
            "total_messages_sent": total_messages_sent,
            "datetime": current_time  # Add datetime to the response
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
