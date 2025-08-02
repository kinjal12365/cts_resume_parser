# lambda_utils.py

import boto3
import json
from aws.config import json_dashboard_bucket, region, json_data_anonymus_lambda


ZIP_FILE_NAME = 'lambda_anonymous.zip'
LAMBDA_ROLE_ARN = 'PLEASE SPECIFY THIS YOURSELF'
RUNTIME = 'python3.10'
ARCHITECTURE = 'x86_64'
HANDLER = 'lambda_function.lambda_handler'
LAMBDA_TIMEOUT = 60
LAMBDA_MEMORY = 512

# Layer ARNs
LAYER_ARNs = [
    'PLEASE SPECIFY THIS YOURSELF'
]

def create_lambda_function4():
    lambda_client = boto3.client('lambda', region_name=region)
    s3_client = boto3.client('s3', region_name=region)

    try:
        with open(ZIP_FILE_NAME, 'rb') as f:
            zipped_code = f.read()

        # Create Lambda
        response = lambda_client.create_function(
            FunctionName=json_data_anonymus_lambda,
            Runtime=RUNTIME,
            Role=LAMBDA_ROLE_ARN,
            Handler=HANDLER,
            Code={'ZipFile': zipped_code},
            Timeout=LAMBDA_TIMEOUT,
            MemorySize=LAMBDA_MEMORY,
            Publish=True,
            Architectures=[ARCHITECTURE],
            Layers=LAYER_ARNs
        )

        print("✅ Lambda function created.")

    except lambda_client.exceptions.ResourceConflictException:
        print(f"ℹ️ Lambda function '{json_data_anonymus_lambda}' already exists.")
    except Exception as e:
        return {'error': f'Lambda creation failed: {str(e)}'}

    try:
        # Add permission (handle id conflict by catching it)
        try:
            lambda_client.add_permission(
                FunctionName=json_data_anonymus_lambda,
                StatementId='s3invoke-permission-v(change)',  # Change StatementId to avoid conflict
                Action='lambda:InvokeFunction',
                Principal='s3.amazonaws.com',
                SourceArn=f'arn:aws:s3:::{json_dashboard_bucket}',
                SourceAccount='PLEASE SPECIFY THIS YOURSELF'  # Optional, but more secure
            )
            print("✅ Permission added to allow S3 to invoke Lambda.")
        except lambda_client.exceptions.ResourceConflictException:
            print("ℹ️ Permission already exists, skipping add_permission.")

        # Configure the bucket to send all object created events to Lambda
        s3_client.put_bucket_notification_configuration(
            Bucket=json_dashboard_bucket,
            NotificationConfiguration={
                'LambdaFunctionConfigurations': [
                    {
                        'LambdaFunctionArn': f'arn:aws:lambda:{region}:83xxx6614080(change):function:{json_data_anonymus_lambda}',
                        'Events': ['s3:ObjectCreated:*']
                    }
                ]
            }
        )
        print("✅ S3 trigger added.")
        return {'message': 'Lambda function and S3 trigger created successfully'}

    except Exception as e:
        return {'error': f'Trigger setup failed: {str(e)}'}