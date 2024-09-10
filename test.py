# import requests
# import json
#
# url = "https://api.interakt.ai/v1/public/create-campaign/"
#
# payload = json.dumps({
#   "campaign_name": "Testing campaignnn",
#   "campaign_type": "PublicAPI",
#   "template_name": "message",
#   "language_code": "en"
# })
# headers = {
#   'Authorization': 'Basic SUYyaW5TY3RZZWtJUUxodGJpSk04Q2h3Q1BVWEpOX09DbFBOMXNEVkNIRTo=',
#   'Content-Type': 'application/json'
# }
#
# response = requests.request("POST", url, headers=headers, data=payload)
#
# print(response.text)


import requests
import json

url = "https://push-draft-to-db-bxoz.onrender.com/create_sms_draft"

payload = json.dumps({
  "user_id": 1,
  "template_id": 2,
  "sender_id": "admindddede5u",
  "text": "This is a sample SMS draft for the user.",
  "sms_type": "SMS"
})

headers = {
  "Content-Type": "application/json",
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization"
}


response = requests.post(url, headers=headers, data=payload)

print(response.text)

