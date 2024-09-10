from flask import Flask, request, jsonify
import requests
import os
from elasticsearch import Elasticsearch
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

es = Elasticsearch(
    cloud_id=os.getenv("ELASTIC_CLOUD_ID"),
    api_key=os.getenv("ELASTIC_API_KEY")
)
def send_sms(phone_number, message, sender_id):
    url = "https://www.fast2sms.com/dev/bulkV2"

    querystring = {
        "authorization": "hJsT2Y7kmsrCJDOzdm5UeobfKLlY2EiQ0gbDrvOBFg4lUVrlBTvcRxpED3Zf",
        "sender_id": sender_id,
        "message": message,
        "route": "dlt",
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

    # Fetch data from Elasticsearch
    index_name = 'phone_name_map_messaging_piece'
    query = {
        "query": {
            "match_all": {}
        }
    }

    try:
        response = es.search(index=index_name, body=query)
        hits = response['hits']['hits']

        for hit in hits:
            source = hit['_source']
            phone_number = source.get('phone_number')

            if phone_number:
                sms_response = send_sms(phone_number, message, sender_id)
                print(f"Message sent to {phone_number}: {sms_response.text}")

        return jsonify({"status": "success", "message": "Messages sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
