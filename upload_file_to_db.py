
from flask import Flask, request
import pandas as pd
import psycopg2
from os import getenv
from flask_cors import CORS
import chardet

app = Flask(__name__)
CORS(app)

# Function to establish a database connection
def get_db_connection():
    try:
        connection = psycopg2.connect(
            dbname=getenv('PGDATABASE'),
            user=getenv('PGUSER'),
            password=getenv('PGPASSWORD'),
            host=getenv('PGHOST'),
            port=getenv('PGPORT', '5432')
        )
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# Route to handle file upload and insertion into DB
@app.route('/upload', methods=['POST'])
def upload_file():
    # Retrieve admin_id from query parameter
    admin_id = request.args.get('admin_id')

    # Ensure admin_id is provided
    if not admin_id:
        return 'Admin ID is required', 400

    # Check if file is part of the request
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    # Check file extension and handle accordingly
    if file.filename.endswith('.csv'):
        try:
            # Detect file encoding
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            file.seek(0)  # Reset file pointer to the beginning

            # Read the CSV file with the detected encoding
            df = pd.read_csv(file, encoding=encoding)
        except Exception as e:
            return f'Error reading CSV file: {e}', 400

    elif file.filename.endswith('.xlsx'):
        try:
            df = pd.read_excel(file)
        except Exception as e:
            return f'Error reading Excel file: {e}', 400

    else:
        return 'Unsupported file type', 400

    # Ensure the required columns are present
    if 'Name' not in df.columns or 'Phone' not in df.columns:
        return 'File must contain "Name" and "Phone" columns', 400

    # Add SenderID and AdminID columns
    df['SenderID'] = 'POLYTS'
    df['AdminID'] = admin_id  # Set Admin ID from query parameter
    df['Phone'] = df['Phone'].apply(lambda x: str(int(float(x))) if isinstance(x, float) else str(x))

    df_to_upload = df[['Name', 'Phone', 'SenderID', 'AdminID']]

    # Insert into database
    connection = get_db_connection()
    if connection is None:
        return 'Database connection error', 500

    try:
        cursor = connection.cursor()
        for index, row in df_to_upload.iterrows():
            cursor.execute("""
                INSERT INTO admin_volunteer_map(name, volunteer_phone_number, sender_id, admin_id)
                VALUES (%s, %s, %s, %s)
            """, (row['Name'], row['Phone'], row['SenderID'], row['AdminID']))

        connection.commit()
        return 'File uploaded and database updated', 200
    except Exception as e:
        print(f"Error updating database: {e}")
        return 'Error updating database', 500
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
