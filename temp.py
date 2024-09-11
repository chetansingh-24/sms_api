# from flask import Flask, request, jsonify
# import pandas as pd
# import io
#
# app = Flask(__name__)
#
# @app.route('/upload_csv', methods=['POST'])
# def upload_csv():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400
#
#     file = request.files['file']
#
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400
#
#     if file and file.filename.endswith('.csv'):
#         # Read the file into a DataFrame
#         try:
#             df = pd.read_csv(file)
#             print("Received CSV Data:")
#             print(df)
#
#             # Convert DataFrame to a dictionary and return as JSON
#             data = df.to_dict(orient='records')
#             return jsonify({'data': data}), 200
#         except Exception as e:
#             return jsonify({'error': str(e)}), 500
#     else:
#         return jsonify({'error': 'Unsupported file type'}), 400
#
#
# if __name__ == '__main__':
#     app.run(debug=True)


import requests
import json

url = "https://api.interakt.ai/v1/public/message/"
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Basic SUYyaW5TY3RZZWtJUUxodGJpSk04Q2h3Q1BVWEpOX09DbFBOMXNEVkNIRTo='
}

# List of phone numbers
contacts = {
    "7783063159": "Prince",
    "6386365575": "Chetan",
    # "9873159656": "Amit",
    # "9013102841": "Asif",
    # "9555864171": "Mohnish",
    # "8800814115":"Nayab"
}
# Loop through each phone number and send the message
for phone_number, name in contacts.items():
    payload = {
        "countryCode": "+91",
        "phoneNumber": phone_number,
        "campaignId": "e8e337db-2825-4478-be66-ad00f06f95b0",
        "callbackData": f"Message for {name}",
        "type": "Template",
        "template": {
            "name": "message",
            "languageCode": "en",
            "headerValues":[ name ],
            "bodyValues": ["Sent by Chetan"]
        }
    }

    payload_json = json.dumps(payload)
    response = requests.post(url, headers=headers, data=payload_json)
    print(f"Response for {name} ({phone_number}): {response.text}")
