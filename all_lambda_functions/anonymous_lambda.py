import json
import boto3
from botocore.exceptions import ClientError
from faker import Faker
import urllib.parse
import uuid

# Seting the destination bucket name directly.
DESTINATION_BUCKET = "ENTER YOUR BUCKET"
# as well as the output bucket name
OUTPUT_FILENAME = "ENTER YOUR BUCKET"

# Initializing Boto3 S3 client and Faker instance
s3_client = boto3.client('s3')
fake = Faker()

def anonymize_data(candidate_data: dict) -> dict:
    
    # This function does

    # Anonymizes the sensitive fields in a single candidate's data dictionary.

    # Args:
        # candidate_data: The original dictionary for one candidate.

    # Returns:
        # The dictionary with anonymized PII.

    # Keep a copy to avoid modifying the original data in place

    anonymized = candidate_data.copy()

    # 1. Anonymize Candidate ID: Replace with a new, randomly generated ID.
    anonymized['candidateId'] = f"CAND_{uuid.uuid4().hex[:12].upper()}"

    # 2. Anonymize Name: Replace with a new, randomly generated name.
    anonymized['name'] = fake.name()

    # 3. Anonymize Email: Generate a fake email.
    # basing the fake email on the new fake name for consistency.
    
    fake_name_parts = anonymized['name'].lower().split()
    fake_email_user = '.'.join(fake_name_parts).replace(' ', '_')
    anonymized['email'] = f"{fake_email_user}@{fake.free_email_domain()}"

    # 4. Anonymize Phone Number: Mask the number, keeping the last 4 digits.
    phone = anonymized.get('phoneNumber')
    if phone and isinstance(phone, str) and len(phone) > 4:
        # Keep only digits for consistent masking
        digits_only = ''.join(filter(str.isdigit, phone))
        if len(digits_only) > 4:
            masked_part = 'X' * (len(digits_only) - 4)
            visible_part = digits_only[-4:]
            anonymized['phoneNumber'] = f"{masked_part}{visible_part}"
        else:
            anonymized['phoneNumber'] = 'XXXX' # Mask short numbers completely
    elif phone:
        anonymized['phoneNumber'] = 'XXXX' # Mask non-string or short numbers

    return anonymized

def lambda_handler(event, context):
    """
    Main Lambda handler function triggered by an S3 file upload.
    This version processes a list of candidates from the input JSON file.
    """
    try:
        # 1. Get the source bucket and file key from the S3 trigger event
        source_bucket = event['Records'][0]['s3']['bucket']['name']
        source_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
        print(f"New file detected: '{source_key}' in bucket '{source_bucket}'.")

        # 2. Read and parse the input JSON file which contains a list of candidates
        s3_object = s3_client.get_object(Bucket=source_bucket, Key=source_key)
        list_of_candidates = json.loads(s3_object['Body'].read().decode('utf-8'))
        
        if not isinstance(list_of_candidates, list):
            raise TypeError("Input JSON is not a list. This function expects a list of candidates.")
            
        print(f"Successfully parsed a list of {len(list_of_candidates)} candidates.")

        # 3. Anonymize each candidate in the list
        newly_anonymized_list = [anonymize_data(candidate) for candidate in list_of_candidates]
        print(f"Anonymized all {len(newly_anonymized_list)} candidates from the input file.")

        # 4. Read existing data from the destination file
        try:
            existing_data_object = s3_client.get_object(Bucket=DESTINATION_BUCKET, Key=OUTPUT_FILENAME)
            all_candidates = json.loads(existing_data_object['Body'].read().decode('utf-8'))
            print(f"Successfully read existing file '{OUTPUT_FILENAME}' with {len(all_candidates)} records.")
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                print(f"File '{OUTPUT_FILENAME}' not found. Starting a new file.")
                all_candidates = []
            else:
                raise

        # 5. Append the new batch of anonymized data to the existing list
        all_candidates.extend(newly_anonymized_list)

        # 6. Write the updated, combined list back to the S3 bucket
        s3_client.put_object(
            Bucket=DESTINATION_BUCKET,
            Key=OUTPUT_FILENAME,
            Body=json.dumps(all_candidates, indent=4),
            ContentType='application/json'
        )
        
        success_message = f"Successfully processed and appended {len(newly_anonymized_list)} candidates to '{OUTPUT_FILENAME}'."
        print(success_message)

        return {'statusCode': 200, 'body': json.dumps(success_message)}

    except Exception as e:
        print(f"ERROR: An unexpected error occurred. {e}")
        return {'statusCode': 500, 'body': json.dumps(f"An unexpected error occurred: {str(e)}")}
