import json
import boto3
import urllib.parse

# Initialize the SES client
ses_client = boto3.client('ses')

# --- CONFIGURATION ---
SENDER_EMAIL = "ENTER YOUR EMAIL" # Must be a verified SES identity
RECIPIENT_EMAIL = "ENTER YOUR EMAIL" # Must be a verified SES identity
# ---------------------

def lambda_handler(event, context):
    """
    This function is triggered by an S3 event. It parses the event,
    constructs an email, and uses SES to send it.
    """
    try:
        # 1. Get the bucket and file name from the S3 event notification
        s3_record = event['Records'][0]['s3']
        bucket_name = s3_record['bucket']['name']
        
        # The object key is URL-encoded, so we need to decode it
        object_key = urllib.parse.unquote_plus(s3_record['object']['key'], encoding='utf-8')
        
        print(f"New file '{object_key}' uploaded to bucket '{bucket_name}'.")

        # 2. Prepare the email content
        email_subject = f"New Resume Submitted !!!!"
        
        email_body_html = f"""
        <html>
        <head></head>
        <body>
          <h1>New Resume Submission</h1>
          <p>A new resume has been uploaded to the S3 bucket.</p>
          <p>Please review the candidate in the dashboard.</p>
        </body>
        </html>
        """
        
        email_body_text = f"A new resume was submitted.\nBucket: {bucket_name}\nFile: {object_key}"

        # 3. Send the email using SES
        response = ses_client.send_email(
            Source=SENDER_EMAIL,
            Destination={
                'ToAddresses': [RECIPIENT_EMAIL]
            },
            Message={
                'Subject': {
                    'Data': email_subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': email_body_text,
                        'Charset': 'UTF-8'
                    },
                    'Html': {
                        'Data': email_body_html,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        
        print(f"Email sent successfully! Message ID: {response['MessageId']}")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Email sent successfully!')
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        # It's important to raise the error to signal failure to Lambda
        raise e