import json
from botocore.exceptions import ClientError

def setup_s3_bucket(s3, bucket_name, region):
    try:
        if region == 'us-east-1':
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        print(f"✅ S3 bucket '{bucket_name}' created.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f"ℹ️ Bucket '{bucket_name}' already exists.")
        else:
            raise e

    # Disable Block Public Access
    try:
        s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': False,
                'IgnorePublicAcls': False,
                'BlockPublicPolicy': False,
                'RestrictPublicBuckets': False
            }
        )
        print("✅ Block Public Access settings disabled.")
    except ClientError as e:
        print(f"⚠️ Failed to disable Block Public Access: {e}")

    # CORS configuration
    cors_config = {
        'CORSRules': [
            {
                "AllowedHeaders": ["*"],
                "AllowedMethods": ["GET", "PUT", "POST"],
                "AllowedOrigins": ["*"],
                "ExposeHeaders": ["ETag"],
                "MaxAgeSeconds": 3000
            }
        ]
    }
    s3.put_bucket_cors(Bucket=bucket_name, CORSConfiguration=cors_config)
    print("✅ CORS policy applied.")

    # Public bucket policy
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicAccessToObjects",
                "Effect": "Allow",
                "Principal": "*",
                "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"],
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*"
                ]
            }
        ]
    }

    try:
        s3.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(bucket_policy))
        print("✅ Bucket policy applied.")
    except ClientError as e:
        print(f"⚠️ Failed to apply bucket policy: {e}")
