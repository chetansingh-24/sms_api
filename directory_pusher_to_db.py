from flask import Flask, request, jsonify
import pandas as pd
from elasticsearch import Elasticsearch, helpers
import os
from dotenv import load_dotenv
from flask_cors import CORS
import re

load_dotenv()

app = Flask(__name__)

# Configure CORS to allow all origins
CORS(app, resources={r"/*": {"origins": "*"}})

es = Elasticsearch(
    cloud_id=os.getenv("ELASTIC_CLOUD_ID"),
    api_key=os.getenv("ELASTIC_API_KEY")
)

INDEX_NAME = "phone_name_map_messaging_piece"

# Define the index mapping
mapping = {
    "mappings": {
        "properties": {
            "name": {
                "type": "text"  # Use "text" for full-text search or "keyword" for exact matches
            },
            "phone_number": {
                "type": "keyword"  # Use "keyword" for exact match of phone numbers
            }
        }
    }
}

def validate_phone_number(phone):
    return bool(re.fullmatch(r'\d{10}', str(phone)))
@app.route('/create_index', methods=['POST'])
def create_index():
    if not es.indices.exists(INDEX_NAME):
        es.indices.create(index=INDEX_NAME, body=mapping)
        return jsonify({"status": "success", "message": f"Index '{INDEX_NAME}' created successfully."}), 200
    else:
        return jsonify({"status": "info", "message": f"Index '{INDEX_NAME}' already exists."}), 200

@app.route('/upload', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.csv'):
        try:
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file.stream)

            required_columns = ['Phone', 'Name']
            if not all(col in df.columns for col in required_columns):
                missing_cols = [col for col in required_columns if col not in df.columns]
                return jsonify({"error": f"Missing columns: {', '.join(missing_cols)}"}), 400

            df = df[required_columns]
            df.columns = ['phone_number', 'name']
            errors = []
            for index, row in df.iterrows():
                phone_number = row['phone_number']

                if not validate_phone_number(phone_number):
                    errors.append(
                        f"Error on line {index + 2}: Invalid phone number '{phone_number}' (must be 10 digits)")

            if errors:
                return jsonify({"status": "error", "errors": errors}), 400
            actions = [
                {
                    "_index": INDEX_NAME,
                    "_source": row.to_dict()
                }
                for _, row in df.iterrows()
            ]
            helpers.bulk(es, actions)
            return jsonify({"status": "success", "message": "Data uploaded successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid file format"}), 400

@app.route('/fetch', methods=['GET'])
def fetch_all():
    try:
        query = {
            "query": {
                "match_all": {}
            }
        }
        response = es.search(index=INDEX_NAME, body=query, size=10000)  # Adjust size as needed

        results = [
            {
                "name": hit["_source"].get("name"),
                "phone_number": hit["_source"].get("phone_number")
            }
            for hit in response['hits']['hits']
        ]

        return jsonify({"status": "success", "data": results}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete', methods=['DELETE'])
def delete_data():
    try:
        # Delete the index
        es.indices.delete(index=INDEX_NAME, ignore=[400, 404])
        return jsonify({"status": "success", "message": f"Index '{INDEX_NAME}' deleted successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
