from flask import Flask, request, jsonify, render_template, redirect, url_for,send_file
import boto3
import datetime
import requests
import tempfile
import json

from aws.config import bucket_name, output_bucket_name, json_extraction_bucket, json_dashboard_bucket, table_name, region, USE_DYNAMO,json_anonymous_bucket
from aws.s3_utils import setup_s3_bucket
from aws.dynamodb_utils import setup_dynamodb_table
from aws.lambda_utils import create_lambda_function
from aws.lambda_utils2 import create_lambda_function2
from aws.lambda_utils3 import create_lambda_function3
from aws.lambda_utils4 import create_lambda_function4
from aws.lambda_utils5 import create_lambda_function5

# Setup Flask
app = Flask(__name__)

# AWS clients
session = boto3.session.Session()
s3 = session.client('s3', region_name=region)
dynamodb = session.client('dynamodb', region_name=region)
dynamodb_resource = session.resource('dynamodb', region_name=region)

# Setup resources
setup_s3_bucket(s3, bucket_name, region)
setup_s3_bucket(s3, output_bucket_name, region)
setup_s3_bucket(s3, json_extraction_bucket, region)
setup_s3_bucket(s3, json_dashboard_bucket, region)
setup_s3_bucket(s3, json_anonymous_bucket, region)


if USE_DYNAMO:
    table = setup_dynamodb_table(dynamodb, dynamodb_resource, table_name)

# Auto-create Lambda function on startup
try:
    lambda_creation_result = create_lambda_function()
    print("Lambda setup result:", lambda_creation_result)
except Exception as e:
    print("Failed to create Lambda function at startup:", e)

try:
    lambda_creation_result2 = create_lambda_function2()
    print("Lambda setup result:", lambda_creation_result2)
except Exception as e:
    print("Failed to create Lambda function at startup:", e)

try:
    lambda_creation_result3 = create_lambda_function3()
    print("Lambda setup result:", lambda_creation_result3)
except Exception as e:
    print("Failed to create Lambda function at startup:", e)

try:
    lambda_creation_result4 = create_lambda_function4()
    print("Lambda setup result:", lambda_creation_result4)
except Exception as e:
    print("Failed to create Lambda function at startup:", e)

try:
    lambda_creation_result5 = create_lambda_function5()
    print("Lambda setup result:", lambda_creation_result5)
except Exception as e:
    print("Failed to create Lambda function at startup:", e)

# Upload form
@app.route('/')
def serve_form():
    return render_template('upload.html')

# Generate pre-signed URL
@app.route('/generate-url', methods=['POST'])
def generate_presigned_url():
    data = request.json
    filename = data.get('filename')

    if not filename or not filename.endswith('.pdf'):
        return jsonify({'error': 'Only PDF files allowed'}), 400

    try:
        presigned_url = s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': bucket_name,
                'Key': filename,
                'ContentType': 'application/pdf'
            },
            ExpiresIn=300
        )

        if USE_DYNAMO:
            table.put_item(Item={
                'filename': filename,
                'timestamp': datetime.datetime.utcnow().isoformat()
            })

        return jsonify({'url': presigned_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Manual Lambda creation route (optional)
@app.route('/create-lambda', methods=['GET'])
def trigger_lambda_creation():
    result = create_lambda_function()
    return jsonify(result)

@app.route('/create-lambda2', methods=['GET'])
def trigger_lambda_creation2():
    result = create_lambda_function2()
    return jsonify(result)

@app.route('/create-lambda3', methods=['GET'])
def trigger_lambda_creation3():
    result = create_lambda_function3()
    return jsonify(result)

@app.route('/create-lambda4', methods=['GET'])
def trigger_lambda_creation4():
    result = create_lambda_function4()
    return jsonify(result)

@app.route('/create-lambda5', methods=['GET'])
def trigger_lambda_creation5():
    result = create_lambda_function5()
    return jsonify(result)


# Admin credentials (simple version)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password123'

# Admin Login Route
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')

# Admin Dashboard Route
@app.route('/dashboard')
def admin_dashboard():
    return render_template('dashboard.html')

@app.route("/reports")
def reports():
    return render_template("reports.html")

@app.route("/candidates")
def candidate_pdfs():
    return render_template("candidatestyle.html")


@app.route('/list-files')
def list_files():
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        files = []

        for obj in response.get('Contents', []):
            files.append({
                'name': obj['Key'],
                'size': round(obj['Size'] / 1024, 2),
                'last_modified': obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S'),
                'url': f'https://{bucket_name}.s3.amazonaws.com/{obj["Key"]}'
            })

        return jsonify(files)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/download-anonymized-json')
def download_anonymized_json():
    # Initialize S3 client
    s3 = boto3.client('s3')

    # Define the S3 key for the anonymized JSON file
    s3_key = 'anonymized_candidates.json'

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode='wb') as tmp_file:
        s3.download_fileobj(json_anonymous_bucket, s3_key, tmp_file)
        tmp_file_path = tmp_file.name

    # Send the file as a downloadable response
    return send_file(tmp_file_path, as_attachment=True, download_name="anonymized_candidates.json")
# Run server
if __name__ == '__main__':
    app.run(debug=True)