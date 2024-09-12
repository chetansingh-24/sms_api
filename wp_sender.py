import requests
from flask import Flask, request, jsonify
import os
from elasticsearch import Elasticsearch
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime  # Import datetime module
import json

load_dotenv()
app = Flask(__name__)

# Configure CORS to allow specific origins if needed
CORS(app, resources={r"/*": {"origins": "*"}})  # Adjust origins as necessary

es = Elasticsearch(
    cloud_id=os.getenv("ELASTIC_CLOUD_ID"),
    api_key=os.getenv("ELASTIC_API_KEY")
)

def send_message(phone_number, campaign_id, template_name, header_values, body_values):
    url = "https://api.interakt.ai/v1/public/message/"

    payload = {
        "countryCode": "+91",
        "phoneNumber": phone_number,
        "fullPhoneNumber": None,  # Optional, either fullPhoneNumber or phoneNumber + CountryCode is required
        "campaignId": campaign_id,
        "callbackData": "some text here",
        "type": "Template",
        "template": {
            "name": template_name,
            "languageCode": "en",
            "headerValues": header_values,
            "bodyValues": body_values
        }
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic SUYyaW5TY3RZZWtJUUxodGJpSk04Q2h3Q1BVWEpOX09DbFBOMXNEVkNIRTo='
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response

@app.route('/send_bulk_msg', methods=['POST'])
def send_bulk_sms():
    data = request.get_json()
    campaign_id = "ef85a3ba-bdbb-4567-ad92-495d4facd8fc"
    template_name = data.get('template', {}).get('name')
    body_values =  data.get('template', {}).get('bodyValues')

    if not campaign_id or not template_name:
        return jsonify({"error": "Missing campaign_id, template_name, or API key"}), 400

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
                header_values = [name]
                message_response = send_message(phone_number, campaign_id, template_name, header_values, body_values)
                print(f"Message sent to {phone_number}: {message_response.text}")
                total_messages_sent += 1
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return jsonify({
            "status": "success",
            "message": "Messages sent successfully",
            "total_messages_sent": total_messages_sent,
            "datetime": current_time
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
