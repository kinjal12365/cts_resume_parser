import json
import boto3
import urllib.parse

# Initializing the S3 client
s3_client = boto3.client('s3')

#  CONFIGURATION 
# have to choose the bucket where the main file is stored.
DESTINATION_BUCKET = 'ENTER YOUR BUCKET' 
# The name of the master JSON file.
MASTER_FILE_KEY = 'candidates.json'

def lambda_handler(event, context):
    """
    This function is triggered by a new JSON file upload. It reads the
    master JSON file, appends the new candidate data, and overwrites
    the master file with the updated content.
    """

    # 1. Get the bucket and file key of the NEWLY uploaded file from the trigger event
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    source_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    print(f"New file detected: '{source_key}' in bucket '{source_bucket}'.")

    try:
        # 2. Get the new candidate's data
        new_candidate_response = s3_client.get_object(Bucket=source_bucket, Key=source_key)
        new_candidate_data = json.loads(new_candidate_response['Body'].read().decode('utf-8'))
        print("Successfully read new candidate data.")

        # 3. Get the existing master candidates.json file
        try:
            existing_file_response = s3_client.get_object(Bucket=DESTINATION_BUCKET, Key=MASTER_FILE_KEY)
            all_candidates = json.loads(existing_file_response['Body'].read().decode('utf-8'))
            print(f"Successfully read master file with {len(all_candidates)} existing candidates.")
        except s3_client.exceptions.NoSuchKey:
            # If the master file doesn't exist yet, start with an empty list
            print("Master file not found. Starting with a new list.")
            all_candidates = []

        # 4. Append the new candidate data to the list
        all_candidates.append(new_candidate_data)
        print(f"Appended new candidate. Total candidates now: {len(all_candidates)}.")

        # 5. Upload the updated list back to S3, overwriting the old file
        s3_client.put_object(
            Bucket=DESTINATION_BUCKET,
            Key=MASTER_FILE_KEY,
            Body=json.dumps(all_candidates, indent=4), # indent makes the JSON readable
            ContentType='application/json'
        )

        print(f"Successfully updated and uploaded '{MASTER_FILE_KEY}' to bucket '{DESTINATION_BUCKET}'.")

        return {
            'statusCode': 200,
            'body': json.dumps('Successfully updated the master candidates file.')
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        raise e