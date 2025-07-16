install the dependencies

Create a s3 bucket and dynamo db and give the naming as per the code

set the cors in s3 enter this script ->

[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST"],
    "AllowedOrigins": ["http://127.0.0.1:5000"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]
