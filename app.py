from flask import Flask, request, jsonify, render_template
import boto3
import datetime

# Setup Flask
app = Flask(__name__)

# AWS configuration
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
bucket_name = 'resume-parser-input-bucket'  # 🔁 CHANGE this to your actual bucket

# Optional: enable DynamoDB logging
USE_DYNAMO = True
table_name = 'ResumeMetadata'
if USE_DYNAMO:
    table = dynamodb.Table(table_name)

# ✅ Serve the upload form using Jinja2 templating
@app.route('/')
def serve_form():
    return render_template('upload.html')  # looks inside templates/upload.html

# ✅ Pre-signed URL endpoint
@app.route('/generate-url', methods=['POST'])
def generate_presigned_url():
    data = request.json
    filename = data['filename']

    # Validate file type
    if not filename.endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are allowed'}), 400

    # Generate presigned S3 upload URL
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

        # Log metadata to DynamoDB (optional)
        if USE_DYNAMO:
            table.put_item(Item={
                'filename': filename,
                'timestamp': datetime.datetime.utcnow().isoformat()
            })

        return jsonify({'url': presigned_url})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
