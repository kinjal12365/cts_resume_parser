import json
import boto3
import os
import tempfile
import logging
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError
from urllib.parse import unquote_plus

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
DEST_BUCKET = 'ENTER YOUR BUCKET'

def clean_text(text):
    return ' '.join(text.split())

def lambda_handler(event, context):
    try:
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = unquote_plus(record['s3']['object']['key'])
            logger.info(f"Received file: s3://{bucket}/{key}")

            with tempfile.NamedTemporaryFile() as tmp_file:
                s3.download_file(bucket, key, tmp_file.name)

                try:
                    text = extract_text(tmp_file.name)
                    cleaned_text = clean_text(text)

                    output_key = key.replace('.pdf', '.txt')
                    s3.put_object(
                        Bucket=DEST_BUCKET,
                        Key=output_key,
                        Body=cleaned_text.encode('utf-8')
                    )
                    logger.info(f"✅ Extracted text saved to s3://{DEST_BUCKET}/{output_key}")

                except PDFSyntaxError:
                    logger.error(f"❌ PDFSyntaxError: Could not parse {key}")
                except Exception as e:
                    logger.error(f"❌ Error during extraction from {key}: {str(e)}")

    except Exception as e:
        logger.error(f"❌ Lambda handler failed: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error processing PDF file.')
        }

    return {
        'statusCode': 200,
        'body': json.dumps('✅ PDF text extraction complete.')
    }

