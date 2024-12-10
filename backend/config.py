import os

class Config:
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION', 'ap-south-1')
    AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')
    AWS_RDS_DATABASE_NAME = os.getenv('AWS_RDS_DATABASE_NAME')
    AWS_RDS_CLUSTER_ARN = os.getenv('AWS_RDS_CLUSTER_ARN')
    AWS_RDS_SECRET_ARN = os.getenv('AWS_RDS_SECRET_ARN')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
