import boto3

s3 = boto3.client("s3")

def upload_to_s3(file_path: str, bucket: str, key: str):
    s3.upload_file(file_path, bucket, key)
    print(f"Uploaded {file_path} to s3://{bucket}/{key}")
