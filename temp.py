from flask import Flask, request, jsonify
import pandas as pd
import io

app = Flask(__name__)

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and file.filename.endswith('.csv'):
        # Read the file into a DataFrame
        try:
            df = pd.read_csv(file)

            # Print the DataFrame to the console (or handle it as needed)
            print("Received CSV Data:")
            print(df)

            # Convert DataFrame to a dictionary and return as JSON
            data = df.to_dict(orient='records')
            return jsonify({'data': data}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Unsupported file type'}), 400


if __name__ == '__main__':
    app.run(debug=True)
