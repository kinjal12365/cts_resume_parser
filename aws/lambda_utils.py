# lambda_utils.py

import boto3
import json
from aws.config import bucket_name, table_name, region,LAMBDA_FUNCTION_NAME

ZIP_FILE_NAME = 'lambda_package.zip'
LAMBDA_ROLE_ARN = 'PLEASE SPECIFY THIS YOURSELF YOUR LAMBDA IAM ROLE'
RUNTIME = 'python3.10'
ARCHITECTURE = 'x86_64'
HANDLER = 'lambda_function.lambda_handler'
LAMBDA_TIMEOUT = 60
LAMBDA_MEMORY = 128

# Layer ARNs
LAYER_ARNs = [
    'PLEASE SPECIFY THIS YOURSELF, THE LAYER ARN'
]

def create_lambda_function():
    lambda_client = boto3.client('lambda', region_name=region)
    s3_client = boto3.client('s3', region_name=region)

    try:
        with open(ZIP_FILE_NAME, 'rb') as f:
            zipped_code = f.read()

        # Create Lambda
        response = lambda_client.create_function(
            FunctionName=LAMBDA_FUNCTION_NAME,
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
        print(f"ℹ️ Lambda function '{LAMBDA_FUNCTION_NAME}' already exists.")
    except Exception as e:
        return {'error': f'Lambda creation failed: {str(e)}'}

    try:
        # Add permission (handle id conflict by catching it)
        try:
            lambda_client.add_permission(
                FunctionName=LAMBDA_FUNCTION_NAME,
                StatementId='s3invoke-permission-v(CHANGE)',  # StatementId should be unique to avoid conflict
                Action='lambda:InvokeFunction',
                Principal='s3.amazonaws.com',
                SourceArn=f'arn:aws:s3:::{bucket_name}',
                SourceAccount='PLEASE SPECIFY THIS YOURSELF'  # basically its Optional, but more secure as nobody outside of my account cant acess it
            )
            print("✅ Permission added to allow S3 to invoke Lambda.")
        except lambda_client.exceptions.ResourceConflictException:
            print("ℹ️ Permission already exists, skipping add_permission.")

        # Configure the bucket to send all object created events to Lambda
        s3_client.put_bucket_notification_configuration(
            Bucket=bucket_name,
            NotificationConfiguration={
                'LambdaFunctionConfigurations': [
                    {
                        'LambdaFunctionArn': f'arn:aws:lambda:{region}:{831926xx40xx(change)}:function:{LAMBDA_FUNCTION_NAME}',
                        'Events': ['s3:ObjectCreated:*']
                    }
                ]
            }
        )
        print("✅ S3 trigger added.")
        return {'message': 'Lambda function and S3 trigger created successfully'}

    except Exception as e:
        return {'error': f'Trigger setup failed: {str(e)}'}