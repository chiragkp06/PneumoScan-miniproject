import boto3
import os

# Initialize Rekognition client
rekognition_client = boto3.client(
    'rekognition',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'ap-south-1')
)

def detect_pneumonia_in_image(bucket_name, image_name):
    """
    Uses AWS Rekognition to detect pneumonia in an X-ray image stored in S3.
    Returns the confidence score for the "Pneumonia" label.
    """
    try:
        # Call Rekognition to detect labels
        response = rekognition_client.detect_labels(
            Image={'S3Object': {'Bucket': bucket_name, 'Name': image_name}},
            MaxLabels=10,
            MinConfidence=90
        )

        # Iterate through the detected labels to find "Pneumonia"
        for label in response.get('Labels', []):
            if label['Name'].lower() == "pneumonia":
                return label['Confidence']

        return None  # Return None if pneumonia is not detected
    except Exception as e:
        print(f"Error in Rekognition service: {str(e)}")
        return None
