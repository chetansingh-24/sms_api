import requests
import pandas as pd
from elasticsearch import Elasticsearch

# Initialize Elasticsearch client
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])  # Update with your ES instance details

def send_sms(phone_number, message):
    url = "https://www.fast2sms.com/dev/bulkV2"

    querystring = {
        "authorization": "hJsT2Y7kmsrCJDOzdm5UeobfKLlY2EiQ0gbDrvOBFg4lUVrlBTvcRxpED3Zf",
        "sender_id": "POLYTS",
        "message": message,  # Use the actual message here
        "route": "dlt",
        "numbers": phone_number
    }

    headers = {
        'cache-control': "no-cache"
    }

    response = requests.get(url, headers=headers, params=querystring)
    return response

# Fetch data from Elasticsearch
index_name = 'your_index_name'  # Replace with your index name
query = {
    "query": {
        "match_all": {}
    }
}

response = es.search(index=index_name, body=query)
hits = response['hits']['hits']

# Process each document
for hit in hits:
    source = hit['_source']
    phone_number = source.get('phone_number')
    name = source.get('name')

    if phone_number and name:
        response = send_sms(phone_number, name)
        print(f"Message sent to {phone_number}: {response.text}")
    else:
        print("Missing phone number or name in document:", hit)

