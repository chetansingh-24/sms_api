# # import requests
# # import json
# #
# # url = "https://api.interakt.ai/v1/public/create-campaign/"
# #
# # payload = json.dumps({
# #   "campaign_name": "Testing campaignnn",
# #   "campaign_type": "PublicAPI",
# #   "template_name": "message",
# #   "language_code": "en"
# # })
# # headers = {
# #   'Authorization': 'Basic SUYyaW5TY3RZZWtJUUxodGJpSk04Q2h3Q1BVWEpOX09DbFBOMXNEVkNIRTo=',
# #   'Content-Type': 'application/json'
# # }
# #
# # response = requests.request("POST", url, headers=headers, data=payload)
# #
# # print(response.text)
#
#
# import requests
# import json
#
# url = "https://push-draft-to-db-bxoz.onrender.com/create_sms_draft"
#
# payload = json.dumps({
#   "user_id": 1,
#   "template_id": 2,
#   "sender_id": "admindddede5u",
#   "text": "This is a sample SMS draft for the user.",
#   "sms_type": "SMS"
# })
#
# headers = {
#   "Content-Type": "application/json",
#   "Access-Control-Allow-Origin": "*",
#   "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
#   "Access-Control-Allow-Headers": "Content-Type, Authorization"
# }
#
#
# response = requests.post(url, headers=headers, data=payload)
#
# print(response.text)
#

import requests
import pandas as pd


# Function to send SMS using Fast2SMS
def send_sms(phone_number, message):
  url = "https://www.fast2sms.com/dev/bulkV2"

  querystring = {
    "authorization": "hJsT2Y7kmsrCJDOzdm5UeobfKLlY2EiQ0gbDrvOBFg4lUVrlBTvcRxpED3Zf",
    "sender_id": "POLYTS",
    "message":173035,
    "variables_values": message,
    "route": "dlt",
    "numbers": phone_number
  }

  headers = {
    'cache-control': "no-cache"
  }

  response = requests.get(url, headers=headers, params=querystring)
  return response

# Read CSV file
csv_file_path = '/home/chetansingh/Downloads/admin_volunteer_map.csv'
df = pd.read_csv(csv_file_path)
for index, row in df.iterrows():
    phone_number = row['Phone']
    name = row['Name']
    response = send_sms(phone_number, name)
    print(f"Message sent to {phone_number}: {response.text}")

