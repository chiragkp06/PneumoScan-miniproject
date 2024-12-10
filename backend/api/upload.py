from flask import Blueprint, request, jsonify
import boto3
import os
from .auth import token_required
from .rekognition_service import detect_pneumonia_in_image  # Import the Rekognition service

upload_bp = Blueprint('upload', __name__)

# Load AWS credentials from environment variables
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

@upload_bp.route('/upload', methods=['POST'])
@token_required
def upload_image(user):
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    try:
        file = request.files['image']
        bucket_name = os.getenv('AWS_BUCKET_NAME')
        file_name = file.filename

        # Upload to S3
        s3.upload_fileobj(file, bucket_name, file_name)
        file_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"

        # Detect pneumonia using Rekognition
        confidence = detect_pneumonia_in_image(bucket_name, file_name)

        if confidence is None:
            return jsonify({"error": "Pneumonia not detected in the image"}), 400

        # Store the result in the database (if needed, you can send this to another endpoint to store it)
        diagnosis = "Pneumonia detected" if confidence >= 90 else "No pneumonia detected"
        
        return jsonify({
            'message': 'File uploaded and analyzed successfully',
            'url': file_url,
            'confidence': confidence,
            'diagnosis': diagnosis
        })

    except Exception as e:
        return jsonify({"error": f"Failed to upload image: {str(e)}"}), 500
