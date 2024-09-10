import requests
import json

url = "https://api.interakt.ai/v1/public/create-campaign/"

payload = json.dumps({
  "campaign_name": "Testing campaignnn",
  "campaign_type": "PublicAPI",
  "template_name": "message",
  "language_code": "en"
})
headers = {
  'Authorization': 'Basic SUYyaW5TY3RZZWtJUUxodGJpSk04Q2h3Q1BVWEpOX09DbFBOMXNEVkNIRTo=',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
