import json
import boto3
import requests
from botocore.exceptions import ClientError
import datetime
import os
import uuid
import re
import hashlib
import logging
from typing import Dict, List, Any

# --- Setup professional logging ---
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# --- Configuration: Use Environment Variables & Constants ---
DESTINATION_BUCKET = os.environ.get("DESTINATION_BUCKET", "name-extraction-bucket1")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DYNAMODB_TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "candidate-profile-table")

TECHNICAL_SKILLS = [
    'python', 'java', 'c++', 'javascript', 'aws', 'docker', 'kubernetes', 'sql',
    'nosql', 'git', 'terraform', 'react', 'node.js', 'django', 'flask',
    'machine learning', 'data analysis', 'api development', 'cicd', 'linux'
]
NON_TECHNICAL_SKILLS = [
    'communication', 'teamwork', 'problem solving', 'leadership', 'management',
    'project management', 'agile', 'scrum', 'critical thinking', 'creativity',
    'adaptability', 'time management', 'customer service', 'negotiation'
]

# --- Initialize AWS Clients ---
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
dynamodb_table = dynamodb.Table(DYNAMODB_TABLE_NAME)

class ProfileProcessingError(Exception):
    """Custom exception for processing errors."""
    pass

def get_gemini_details(resume_text: str, api_key: str) -> Dict[str, str]:
    """Extracts details using the Gemini API, raising an exception on failure."""
    if not api_key:
        raise ProfileProcessingError("Gemini API Key is not configured.")
    
    model_name = "gemini-1.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    prompt = f"Analyze the following resume text and extract the full name and a one-line summary of total work experience. Return ONLY a valid JSON object with keys 'name' and 'experience'.\n\nResume Text:\n---\n{resume_text}\n---"
    
    try:
        response = requests.post(
            url,
            headers={'Content-Type': 'application/json'},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30
        )
        response.raise_for_status()
        response_data = response.json()
        raw_text = response_data['candidates'][0]['content']['parts'][0]['text']
        clean_text = re.sub(r'```json\s*|\s*```', '', raw_text).strip()
        return json.loads(clean_text)
    except requests.exceptions.RequestException as e:
        raise ProfileProcessingError(f"API Request Error: {e}")
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        raise ProfileProcessingError(f"Failed to parse Gemini response: {e}")

def get_local_details(resume_text: str) -> Dict[str, Any]:
    """Extracts emails, phone numbers, and skills using local regex and lists."""
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text)
    phone_numbers = re.findall(r'\b(?:\+?\d{1,3}[-\s.]?)?\(?\d{3}\)?[-\s.]?\d{3}[-\s.]?\d{4}\b', resume_text)
    tech_skills = [skill for skill in TECHNICAL_SKILLS if re.search(r'\b' + re.escape(skill) + r'\b', resume_text, re.IGNORECASE)]
    non_tech_skills = [skill for skill in NON_TECHNICAL_SKILLS if re.search(r'\b' + re.escape(skill) + r'\b', resume_text, re.IGNORECASE)]
    return {
        "emails": emails,
        "phone_numbers": phone_numbers,
        "skills": {"technical": tech_skills, "non_technical": non_tech_skills}
    }

def process_and_save_profile(resume_text: str, candidate_id: str, primary_email: str, local_details: Dict[str, Any]) -> str:
    """Processes resume, constructs profile, and saves it to S3 and DynamoDB."""
    gemini_details = get_gemini_details(resume_text, GEMINI_API_KEY)

    final_output = {
        "candidate_id": candidate_id,
        "name": gemini_details.get('name', 'Extraction Failed'),
        "email": primary_email,
        "phone_number": local_details['phone_numbers'][0] if local_details['phone_numbers'] else "Not Found",
        "skills": local_details['skills'],
        "experience_summary": gemini_details.get('experience', 'Extraction Failed')
    }

    output_key = f"processed/{candidate_id}.json"
    
    # Save to S3
    s3_client.put_object(
        Bucket=DESTINATION_BUCKET,
        Key=output_key,
        Body=json.dumps(final_output, indent=4),
        ContentType='application/json'
    )
    logger.info(f"Successfully saved profile to S3: s3://{DESTINATION_BUCKET}/{output_key}")

    # Save metadata to DynamoDB
    new_resume_hash = hashlib.md5(resume_text.encode('utf-8')).hexdigest()
    dynamodb_table.put_item(
        Item={
            'email': primary_email,
            'candidate_id': candidate_id,
            'resume_hash': new_resume_hash,
            'last_updated': datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
    )
    logger.info(f"Successfully saved metadata to DynamoDB for email: {primary_email}")
    return f"Processed profile for '{primary_email}' with ID '{candidate_id}'."


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler that orchestrates the resume processing workflow."""
    try:
        source_bucket = event['Records'][0]['s3']['bucket']['name']
        source_key = event['Records'][0]['s3']['object']['key']
        logger.info(f"Processing '{source_key}' from bucket '{source_bucket}'.")
    except (KeyError, IndexError):
        logger.error("Invalid S3 event format.")
        return {'statusCode': 400, 'body': json.dumps('Invalid S3 event format.')}

    try:
        s3_object = s3_client.get_object(Bucket=source_bucket, Key=source_key)
        resume_text = s3_object['Body'].read().decode('utf-8')
        # --- THIS IS THE ADDED DEBUGGING LINE ---
        logger.info(f"--- Resume Content Received ---\n{resume_text}\n--- End of Content ---")
        # ----------------------------------------
    except ClientError as e:
        logger.error(f"Could not read file from S3: {e}")
        return {'statusCode': 500, 'body': json.dumps('Error reading from source S3.')}

    local_details = get_local_details(resume_text)
    primary_email = local_details['emails'][0].lower() if local_details['emails'] else None
    
    if not primary_email:
        logger.error("No email address found in the resume. Cannot process.")
        return {'statusCode': 400, 'body': json.dumps('No email address found.')}

    try:
        response = dynamodb_table.get_item(Key={'email': primary_email})
        existing_item = response.get('Item')
    except ClientError as e:
        logger.error(f"Could not check DynamoDB for {primary_email}: {e}")
        return {'statusCode': 500, 'body': json.dumps('Error accessing DynamoDB.')}

    if existing_item:
        new_resume_hash = hashlib.md5(resume_text.encode('utf-8')).hexdigest()
        if new_resume_hash == existing_item.get('resume_hash'):
            message = f"Candidate '{primary_email}' exists and resume content is unchanged. Skipping."
            logger.info(message)
            return {'statusCode': 200, 'body': json.dumps({'status': 'skipped', 'message': message})}
        
        logger.info(f"Existing candidate '{primary_email}' found with new resume. Updating profile.")
        candidate_id = existing_item['candidate_id']
        status_message = "updated"
    else:
        logger.info(f"New candidate '{primary_email}' detected. Creating new profile.")
        candidate_id = f"R{datetime.datetime.now().year}-{uuid.uuid4().hex[:7].upper()}"
        status_message = "created"

    try:
        success_message = process_and_save_profile(resume_text, candidate_id, primary_email, local_details)
        logger.info(f"Successfully {status_message} profile.")
        return {'statusCode': 200, 'body': json.dumps(success_message)}
    except (ProfileProcessingError, ClientError) as e:
        logger.error(f"Failed to process profile for {primary_email}: {e}")
        return {'statusCode': 500, 'body': json.dumps(f"Failed to process profile: {e}")}