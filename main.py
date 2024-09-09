import pandas as pd
from os import getenv
from dotenv import load_dotenv
import psycopg2

from flask_cors import CORS

load_dotenv()


DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': getenv('PGDATABASE'),
    'USER': getenv('PGUSER'),
    'PASSWORD': getenv('PGPASSWORD'),
    'HOST': getenv('PGHOST'),
    'PORT': getenv('PGPORT', 5432),
    'OPTIONS': {
      'sslmode': 'require',
    },
  }
}


def get_db_connection():
  connection = psycopg2.connect(
    dbname=getenv('PGDATABASE'),
    user=getenv('PGUSER'),
    password=getenv('PGPASSWORD'),
    host=getenv('PGHOST'),
    port=getenv('PGPORT', 5432)
  )
  return connection

file_path = "/home/chetansingh/Downloads/DeliveryReport__07-09-2024_03-36-09-8373.xlsx"
def push_to_db(filepath):
  df = pd.read_excel(filepath)

  connection = get_db_connection()
  cursor = connection.cursor()


  for index, row in df.iterrows():
    req_id= row['SMS Request ID']
    sender_id = row['Sender ID']
    receiver = row['Receiver']
    sent_message = row['Sent Message']
    status = row['Status']
    delivery_time = row['Delivery Time']


    insert_query = """
           INSERT INTO sms_delivery (request_id, sender_id, receiver, sent_message, status, delivery_time)
           VALUES (%s, %s, %s, %s, %s, %s)
           """
    cursor.execute(insert_query, (req_id, sender_id, receiver, sent_message, status, delivery_time))
  connection.commit()
  cursor.close()
  connection.close()

  print(f"Data successfully pushed to DB from")

push_to_db(file_path)


