import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

try:
    sts = boto3.client('sts')
    identity = sts.get_caller_identity()
    print("✅ AWS is configured! You're logged in as:", identity['Arn'])
except NoCredentialsError:
    print("❌ AWS credentials not found.")
except PartialCredentialsError:
    print("❌ AWS credentials are incomplete.")
